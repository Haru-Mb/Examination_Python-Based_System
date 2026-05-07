"""
Modal dialogs and confirmation boxes
"""
import tkinter as tk
from views.components.theme import get_theme


class Modal(tk.Toplevel):
    """Base modal window"""
    def __init__(self, parent, title="", width=420, height=300):
        super().__init__(parent)
        t = get_theme()
        self.configure(bg=t["bg"])
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        # Center over parent
        self.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + (pw // 2) - (width // 2)
        y = py + (ph // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self._t = t
        self._body = tk.Frame(self, bg=t["bg"], padx=24, pady=20)
        self._body.pack(fill="both", expand=True)

    @property
    def body(self):
        return self._body


def confirm_dialog(parent, title, message, ok_text="Confirm", cancel_text="Cancel",
                   ok_color=None, on_confirm=None, on_cancel=None):
    t = get_theme()
    dlg = Modal(parent, title=title, width=400, height=200)

    tk.Label(dlg.body, text=title, bg=t["bg"], fg=t["text"],
             font=("Helvetica", 13, "bold")).pack(anchor="w")
    tk.Label(dlg.body, text=message, bg=t["bg"], fg=t["text2"],
             font=("Helvetica", 11), wraplength=340, justify="left").pack(anchor="w", pady=(8, 20))

    btn_row = tk.Frame(dlg.body, bg=t["bg"])
    btn_row.pack(fill="x")

    def do_cancel():
        dlg.destroy()
        if on_cancel:
            on_cancel()

    def do_confirm():
        dlg.destroy()
        if on_confirm:
            on_confirm()

    tk.Button(btn_row, text=cancel_text, bg=t["bg3"], fg=t["text2"],
              activebackground=t["card_hover"], activeforeground=t["text"],
              relief="flat", bd=0, font=("Helvetica", 11), padx=16, pady=7,
              cursor="hand2", command=do_cancel).pack(side="left", padx=(0, 8))

    ok_bg = ok_color or t["accent"]
    tk.Button(btn_row, text=ok_text, bg=ok_bg, fg="#FFFFFF",
              activebackground=t["accent2"], activeforeground="#FFFFFF",
              relief="flat", bd=0, font=("Helvetica", 11, "bold"), padx=16, pady=7,
              cursor="hand2", command=do_confirm).pack(side="left")

    return dlg


def input_dialog(parent, title, label, placeholder="", on_submit=None):
    t = get_theme()
    dlg = Modal(parent, title=title, width=400, height=220)

    tk.Label(dlg.body, text=title, bg=t["bg"], fg=t["text"],
             font=("Helvetica", 13, "bold")).pack(anchor="w")
    tk.Label(dlg.body, text=label, bg=t["bg"], fg=t["text2"],
             font=("Helvetica", 11)).pack(anchor="w", pady=(8, 4))

    var = tk.StringVar()
    entry = tk.Entry(dlg.body, textvariable=var, bg=t["bg2"], fg=t["text"],
                     insertbackground=t["text"], relief="flat", bd=0,
                     font=("Helvetica", 12))
    entry.pack(fill="x", ipady=8, pady=(0, 16))
    if placeholder:
        entry.insert(0, placeholder)
        entry.config(fg=t["text3"])
        def _clear(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=t["text"])
        entry.bind("<FocusIn>", _clear)

    tk.Frame(dlg.body, bg=t["border"], height=1).pack(fill="x", pady=(0, 12))

    btn_row = tk.Frame(dlg.body, bg=t["bg"])
    btn_row.pack(fill="x")

    def do_submit():
        val = var.get().strip()
        dlg.destroy()
        if on_submit:
            on_submit(val)

    tk.Button(btn_row, text="Cancel", bg=t["bg3"], fg=t["text2"],
              activebackground=t["card_hover"], activeforeground=t["text"],
              relief="flat", bd=0, font=("Helvetica", 11), padx=16, pady=7,
              cursor="hand2", command=dlg.destroy).pack(side="left", padx=(0, 8))

    tk.Button(btn_row, text="Submit", bg=t["accent"], fg="#FFFFFF",
              activebackground=t["accent2"], activeforeground="#FFFFFF",
              relief="flat", bd=0, font=("Helvetica", 11, "bold"), padx=16, pady=7,
              cursor="hand2", command=do_submit).pack(side="left")

    entry.focus()
    dlg.bind("<Return>", lambda e: do_submit())

    return dlg


def toast(parent, message, kind="info", duration=2500):
    """Non-blocking toast notification"""
    t = get_theme()
    colors = {
        "info": t["accent"],
        "success": t["success"],
        "error": t["danger"],
        "warning": t["warning"],
    }
    bg = colors.get(kind, t["accent"])

    toast_win = tk.Toplevel(parent)
    toast_win.overrideredirect(True)
    toast_win.configure(bg=bg)
    toast_win.attributes("-topmost", True)

    tk.Label(toast_win, text=message, bg=bg, fg="#FFFFFF",
             font=("Helvetica", 11), padx=20, pady=10).pack()

    toast_win.update_idletasks()
    w = toast_win.winfo_width()
    h = toast_win.winfo_height()
    sw = parent.winfo_screenwidth()
    sh = parent.winfo_screenheight()
    toast_win.geometry(f"+{sw - w - 30}+{sh - h - 60}")

    parent.after(duration, toast_win.destroy)
    return toast_win
