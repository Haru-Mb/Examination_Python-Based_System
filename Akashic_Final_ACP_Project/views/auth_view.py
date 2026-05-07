"""
Auth view — Login and Sign Up with tab switching
"""
import tkinter as tk
from views.components.theme import get_theme, on_theme_change
from views.components.modal import toast
from controllers.auth_controller import login_user, register_user


class AuthView(tk.Frame):
    def __init__(self, parent, on_login_success=None, on_back=None):
        t = get_theme()
        super().__init__(parent, bg=t["bg"])
        self._on_login_success = on_login_success
        self._on_back = on_back
        self._mode = "login"  # or "register"
        on_theme_change(self._refresh)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        t = get_theme()
        self.configure(bg=t["bg"])

        # Back button top-left
        tk.Button(self, text="← Back", bg=t["card"], fg=t["text"],
                  activebackground=t["accent"], activeforeground="#FFFFFF",
                  font=("Helvetica", 11), relief="flat", bd=0,
                  cursor="hand2", command=self._on_back).place(x=20, y=16)

        # Card
        card = tk.Frame(self, bg=t["card"], padx=44, pady=36)
        card.place(relx=0.5, rely=0.5, anchor="center", width=440)

        # Logo
        tk.Label(card, text="AKASHIC", bg=t["card"], fg=t["accent"],
                 font=("Helvetica", 20, "bold")).pack(pady=(0, 4))
        tk.Label(card, text="Examination Platform", bg=t["card"], fg=t["text3"],
                 font=("Helvetica", 10)).pack(pady=(0, 20))

        # Tab switcher
        tab_frame = tk.Frame(card, bg=t["bg3"])
        tab_frame.pack(fill="x", pady=(0, 24))

        self._login_tab = tk.Button(
            tab_frame, text="Login",
            bg=t["accent"] if self._mode == "login" else t["bg3"],
            fg="#FFFFFF" if self._mode == "login" else t["text2"],
            font=("Helvetica", 11, "bold" if self._mode == "login" else "normal"),
            relief="flat", bd=0, padx=20, pady=8, cursor="hand2",
            command=lambda: self._switch("login")
        )
        self._login_tab.pack(side="left", fill="x", expand=True)

        self._reg_tab = tk.Button(
            tab_frame, text="Sign Up",
            bg=t["accent"] if self._mode == "register" else t["bg3"],
            fg="#FFFFFF" if self._mode == "register" else t["text2"],
            font=("Helvetica", 11, "bold" if self._mode == "register" else "normal"),
            relief="flat", bd=0, padx=20, pady=8, cursor="hand2",
            command=lambda: self._switch("register")
        )
        self._reg_tab.pack(side="left", fill="x", expand=True)

        # Form area
        self._form_frame = tk.Frame(card, bg=t["card"])
        self._form_frame.pack(fill="x")

        if self._mode == "login":
            self._build_login_form(self._form_frame, t)
        else:
            self._build_register_form(self._form_frame, t)

    def _entry(self, parent, label, var, show=None):
        t = get_theme()
        tk.Label(parent, text=label, bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w", pady=(10, 2))
        kwargs = dict(textvariable=var, bg=t["bg2"], fg=t["text"],
                      insertbackground=t["text"], relief="flat", bd=0,
                      font=("Helvetica", 12))
        if show:
            kwargs["show"] = show
        e = tk.Entry(parent, **kwargs)
        e.pack(fill="x", ipady=9)
        return e

    def _build_login_form(self, parent, t):
        self._login_id = tk.StringVar()
        self._login_pw = tk.StringVar()

        self._entry(parent, "Username or Email", self._login_id)
        self._entry(parent, "Password", self._login_pw, show="•")

        self._err_label = tk.Label(parent, text="", bg=t["card"], fg=t["danger"],
                                   font=("Helvetica", 10))
        self._err_label.pack(anchor="w", pady=(6, 0))

        tk.Button(parent, text="Login →",
                  bg=t["accent"], fg="#FFFFFF",
                  activebackground=t["accent2"], activeforeground="#FFFFFF",
                  font=("Helvetica", 12, "bold"), relief="flat", bd=0,
                  padx=20, pady=10, cursor="hand2",
                  command=self._do_login).pack(fill="x", pady=(16, 0))

        parent.bind_all("<Return>", lambda e: self._do_login())

    def _build_register_form(self, parent, t):
        self._reg_username = tk.StringVar()
        self._reg_email = tk.StringVar()
        self._reg_srcode = tk.StringVar()
        self._reg_pw = tk.StringVar()
        self._reg_role = tk.StringVar(value="student")

        self._entry(parent, "Username", self._reg_username)
        self._entry(parent, "Email", self._reg_email)
        self._entry(parent, "SR Code / Employee ID", self._reg_srcode)
        self._entry(parent, "Password", self._reg_pw, show="•")

        # Role selector
        tk.Label(parent, text="Role", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w", pady=(10, 4))
        role_row = tk.Frame(parent, bg=t["card"])
        role_row.pack(fill="x")

        for val, lbl in [("student", "Student"), ("professor", "Professor")]:
            tk.Radiobutton(role_row, text=lbl, value=val,
                           variable=self._reg_role,
                           bg=t["card"], fg=t["text"],
                           activebackground=t["card"],
                           selectcolor=t["accent"],
                           font=("Helvetica", 11)).pack(side="left", padx=(0, 20))

        self._err_label = tk.Label(parent, text="", bg=t["card"], fg=t["danger"],
                                   font=("Helvetica", 10))
        self._err_label.pack(anchor="w", pady=(6, 0))

        tk.Button(parent, text="Create Account →",
                  bg=t["accent"], fg="#FFFFFF",
                  activebackground=t["accent2"], activeforeground="#FFFFFF",
                  font=("Helvetica", 12, "bold"), relief="flat", bd=0,
                  padx=20, pady=10, cursor="hand2",
                  command=self._do_register).pack(fill="x", pady=(14, 0))

    def _switch(self, mode):
        self._mode = mode
        self._build()

    def _do_login(self):
        identifier = self._login_id.get().strip()
        password = self._login_pw.get()
        if not identifier or not password:
            self._err_label.config(text="Please fill in all fields.")
            return
        result = login_user(identifier, password)
        if result["ok"]:
            if self._on_login_success:
                self._on_login_success(result["user"])
        else:
            self._err_label.config(text=result.get("error", "Login failed."))

    def _do_register(self):
        username = self._reg_username.get().strip()
        email = self._reg_email.get().strip()
        sr_code = self._reg_srcode.get().strip()
        password = self._reg_pw.get()
        role = self._reg_role.get()

        if not all([username, email, sr_code, password]):
            self._err_label.config(text="Please fill in all fields.")
            return

        result = register_user(username, email, sr_code, password, role)
        if result["ok"]:
            toast(self, "Account created! Please log in.", kind="success")
            self._switch("login")
        else:
            self._err_label.config(text=result.get("error", "Registration failed."))

    def _refresh(self):
        self._build()
