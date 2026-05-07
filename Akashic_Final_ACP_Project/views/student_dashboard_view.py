"""
Student Dashboard View
"""
import tkinter as tk
from tkinter import ttk
from views.components.theme import get_theme, on_theme_change
from views.components.sidebar import Sidebar
from views.components.modal import toast, confirm_dialog, input_dialog
from utils.session_manager import get_current_user
import controllers.student_controller as sc


MENU = [
    ("home",       "Home",       "⌂"),
    ("activities", "Activities", "⚡"),
    ("tests",      "Tests",      "📝"),
    ("scores",     "Scores",     "📊"),
    ("join",       "Join Class", "＋"),
]


class StudentDashboard(tk.Frame):
    def __init__(self, parent, on_logout=None):
        t = get_theme()
        super().__init__(parent, bg=t["bg"])
        self._on_logout = on_logout
        self._selected_class = None
        on_theme_change(self._refresh_theme)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        t = get_theme()
        self.configure(bg=t["bg"])

        self._sidebar = Sidebar(self, MENU, on_logout=self._logout, active_key="home")
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.on_navigate(self._on_nav)

        self._content = tk.Frame(self, bg=t["bg"])
        self._content.pack(side="left", fill="both", expand=True)

        self._show_home()

    def _on_nav(self, key):
        self._show(key)

    def _show(self, key):
        for w in self._content.winfo_children():
            w.destroy()
        t = get_theme()
        self._content.configure(bg=t["bg"])

        if key == "home":
            self._show_home()
        elif key == "activities":
            self._show_activities()
        elif key == "tests":
            self._show_tests()
        elif key == "scores":
            self._show_scores()
        elif key == "join":
            self._show_join()

    def _page_header(self, parent, title, subtitle=""):
        t = get_theme()
        hdr = tk.Frame(parent, bg=t["bg"], pady=0)
        hdr.pack(fill="x", padx=32, pady=(28, 16))
        tk.Label(hdr, text=title, bg=t["bg"], fg=t["text"],
                 font=("Helvetica", 22, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, bg=t["bg"], fg=t["text2"],
                     font=("Helvetica", 11)).pack(anchor="w")
        tk.Frame(parent, bg=t["border"], height=1).pack(fill="x", padx=32)

    def _scrollable(self, parent):
        t = get_theme()
        canvas = tk.Canvas(parent, bg=t["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=t["bg"])
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def _on_canvas_resize(e):
            canvas.itemconfig(win_id, width=e.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return inner

    # ── HOME ────────────────────────────────────────────────────────────────
    def _show_home(self):
        t = get_theme()
        user = get_current_user()
        classes = sc.get_my_classes()

        self._page_header(self._content, f"Welcome back, {user.get('nickname') or user['username']} 👋",
                          "Here's your overview.")

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        # Stats row
        stats_row = tk.Frame(pad, bg=t["bg"])
        stats_row.pack(fill="x", pady=(0, 24))

        all_scores = sc.get_my_scores()
        completed = len(all_scores)
        avg = round(sum(s["percentage"] for s in all_scores) / completed, 1) if completed else 0

        for label, val, color in [
            ("Classes Joined", len(classes), t["accent"]),
            ("Tests Completed", completed, t["success"]),
            ("Average Score", f"{avg}%", t["accent2"]),
        ]:
            card = tk.Frame(stats_row, bg=t["card"], padx=24, pady=18)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            tk.Label(card, text=str(val), bg=t["card"], fg=color,
                     font=("Helvetica", 28, "bold")).pack(anchor="w")
            tk.Label(card, text=label, bg=t["card"], fg=t["text2"],
                     font=("Helvetica", 11)).pack(anchor="w")

        # My Classes
        tk.Label(pad, text="My Classes", bg=t["bg"], fg=t["text"],
                 font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 12))

        if not classes:
            tk.Label(pad, text="No classes yet. Use 'Join Class' to get started.",
                     bg=t["bg"], fg=t["text3"], font=("Helvetica", 12)).pack(anchor="w")
        else:
            for cls in classes:
                self._class_card(pad, cls)

    def _class_card(self, parent, cls):
        t = get_theme()
        card = tk.Frame(parent, bg=t["card"], padx=20, pady=14, cursor="hand2")
        card.pack(fill="x", pady=(0, 8))

        row = tk.Frame(card, bg=t["card"])
        row.pack(fill="x")

        dot = tk.Frame(row, bg=t["accent"], width=12, height=12)
        dot.pack(side="left", padx=(0, 12), pady=6)

        info = tk.Frame(row, bg=t["card"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=cls["name"], bg=t["card"], fg=t["text"],
                 font=("Helvetica", 13, "bold")).pack(anchor="w")
        tk.Label(info, text=f"Prof. {cls['professor_name']}  ·  Code: {cls['class_code']}",
                 bg=t["card"], fg=t["text2"], font=("Helvetica", 10)).pack(anchor="w")

        # Hover effect
        for w in [card, row, info, dot]:
            w.bind("<Enter>", lambda e, c=card: c.configure(bg=t["card_hover"]))
            w.bind("<Leave>", lambda e, c=card: c.configure(bg=t["card"]))

    # ── ACTIVITIES ──────────────────────────────────────────────────────────
    def _show_activities(self):
        t = get_theme()
        classes = sc.get_my_classes()
        self._page_header(self._content, "Activities ⚡", "Kahoot-style timed quizzes")

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        if not classes:
            tk.Label(pad, text="Join a class to see activities.",
                     bg=t["bg"], fg=t["text3"], font=("Helvetica", 12)).pack(anchor="w")
            return

        for cls in classes:
            acts = sc.get_activities(cls["id"])
            if not acts:
                continue
            tk.Label(pad, text=cls["name"], bg=t["bg"], fg=t["text"],
                     font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(12, 6))
            for act in acts:
                self._test_card(pad, act, cls, "activity")

    # ── TESTS ───────────────────────────────────────────────────────────────
    def _show_tests(self):
        t = get_theme()
        classes = sc.get_my_classes()
        self._page_header(self._content, "Tests 📝", "Secure exams with anti-cheat monitoring")

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        if not classes:
            tk.Label(pad, text="Join a class to see tests.",
                     bg=t["bg"], fg=t["text3"], font=("Helvetica", 12)).pack(anchor="w")
            return

        for cls in classes:
            tests = sc.get_tests(cls["id"], "test")
            if not tests:
                continue
            tk.Label(pad, text=cls["name"], bg=t["bg"], fg=t["text"],
                     font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(12, 6))
            for test in tests:
                self._test_card(pad, test, cls, "test")

    def _test_card(self, parent, item, cls, kind):
        t = get_theme()
        done = item.get("done", 0)
        card = tk.Frame(parent, bg=t["card"], padx=20, pady=12)
        card.pack(fill="x", pady=(0, 8))

        row = tk.Frame(card, bg=t["card"])
        row.pack(fill="x")

        # Status badge
        badge_bg = t["success"] if done else t["accent"]
        badge_text = "Done" if done else "Start"
        tk.Label(row, text=badge_text, bg=badge_bg, fg="#FFF",
                 font=("Helvetica", 9, "bold"), padx=8, pady=3).pack(side="right")

        info = tk.Frame(row, bg=t["card"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=item["title"], bg=t["card"], fg=t["text"],
                 font=("Helvetica", 12, "bold")).pack(anchor="w")

        meta = []
        if item.get("time_limit"):
            meta.append(f"⏱ {item['time_limit']} min")
        if kind == "test":
            meta.append("🔒 Anti-cheat active")
        if meta:
            tk.Label(info, text="  ·  ".join(meta), bg=t["card"], fg=t["text3"],
                     font=("Helvetica", 10)).pack(anchor="w")

        if not done:
            card.configure(cursor="hand2")
            card.bind("<Button-1>", lambda e, tid=item["id"], k=kind, cid=cls["id"]:
                      self._start_test(tid, k, cid))

    # ── SCORES ──────────────────────────────────────────────────────────────
    def _show_scores(self):
        t = get_theme()
        self._page_header(self._content, "Scores 📊", "Your submission history with PH CHED grades")

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        scores = sc.get_my_scores()
        if not scores:
            tk.Label(pad, text="No submissions yet.", bg=t["bg"], fg=t["text3"],
                     font=("Helvetica", 12)).pack(anchor="w")
            return

        # Header row
        hdr = tk.Frame(pad, bg=t["bg3"], padx=12, pady=8)
        hdr.pack(fill="x", pady=(0, 4))
        for col, w in [("Title", 280), ("Type", 90), ("Score", 90), ("Grade", 70), ("Remarks", 120)]:
            tk.Label(hdr, text=col, bg=t["accent"], fg="#FFFFFF",
                     font=("Helvetica", 10, "bold"), width=w//8, anchor="w").pack(side="left")

        for s in scores:
            row = tk.Frame(pad, bg=t["card"], padx=12, pady=10)
            row.pack(fill="x", pady=(0, 4))
            grade_color = self._grade_color(s.get("grade", "5.00"), t)
            for val, w in [
                (s["title"][:35], 280),
                (s["type"].capitalize(), 90),
                (f"{s['percentage']:.1f}%", 90),
                (s.get("grade", "-"), 70),
                (s.get("grade", ""), 120),
            ]:
                color = grade_color if val == s.get("grade", "-") else t["text"]
                tk.Label(row, text=val, bg=t["card"], fg=color,
                         font=("Helvetica", 11), width=w//8, anchor="w").pack(side="left")

    def _grade_color(self, grade, t):
        try:
            g = float(grade)
            if g <= 1.5: return t["success"]
            if g <= 2.5: return t["accent"]
            if g <= 3.0: return t["warning"]
            return t["danger"]
        except Exception:
            return t["text2"]

    # ── JOIN CLASS ──────────────────────────────────────────────────────────
    def _show_join(self):
        t = get_theme()
        self._page_header(self._content, "Join a Class ＋", "Enter a class code from your professor")

        pad = tk.Frame(self._content, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=32)

        card = tk.Frame(pad, bg=t["card"], padx=32, pady=32)
        card.pack(anchor="nw", ipadx=20)

        tk.Label(card, text="Class Code", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 11)).pack(anchor="w", pady=(0, 6))

        var = tk.StringVar()
        entry = tk.Entry(card, textvariable=var, bg=t["bg2"], fg=t["text"],
                         insertbackground=t["text"], relief="flat", bd=0,
                         font=("Helvetica", 18), width=20)
        entry.pack(ipady=12, pady=(0, 16))
        entry.focus()

        err_lbl = tk.Label(card, text="", bg=t["card"], fg=t["danger"],
                           font=("Helvetica", 10))
        err_lbl.pack(anchor="w", pady=(0, 8))

        def do_join():
            code = var.get().strip()
            if not code:
                err_lbl.config(text="Please enter a class code.")
                return
            result = sc.join_class_by_code(code)
            if result["ok"]:
                toast(self, f"Joined: {result['class']['name']} 🎉", kind="success")
                self._sidebar.set_active("home")
                self._show("home")
            else:
                err_lbl.config(text=result.get("error", "Failed to join."))

        tk.Button(card, text="Join Class →",
                  bg=t["accent"], fg="#FFFFFF",
                  activebackground=t["accent2"], activeforeground="#FFFFFF",
                  font=("Helvetica", 13, "bold"), relief="flat", bd=0,
                  padx=24, pady=10, cursor="hand2", command=do_join).pack(anchor="w")

        entry.bind("<Return>", lambda e: do_join())

    # ── TEST RUNNER ─────────────────────────────────────────────────────────
    def _start_test(self, test_id, kind, class_id):
        data = sc.load_test_questions(test_id)
        if not data:
            toast(self, "Could not load test.", kind="error")
            return

        result = sc.begin_test(test_id)
        if not result["ok"]:
            toast(self, result.get("error", "Failed to start."), kind="error")
            return

        sub_id = result["submission_id"]

        if kind == "test":
            from views.test_window import TestWindow
            TestWindow(self, data, sub_id, on_submit=self._on_test_done)
        else:
            from views.activity_window import ActivityWindow
            ActivityWindow(self, data, sub_id, class_id=class_id, on_submit=self._on_test_done)

    def _on_test_done(self, result):
        if result["ok"]:
            pct = result["percentage"]
            grade = result["grade"]
            remarks = result["remarks"]
            toast(self, f"Submitted! Score: {pct:.1f}%  Grade: {grade} ({remarks})", kind="success")
        else:
            toast(self, result.get("error", "Submission error."), kind="error")
        self._show("scores")
        self._sidebar.set_active("scores")

    def _logout(self):
        from controllers.auth_controller import logout_user
        logout_user()
        if self._on_logout:
            self._on_logout()

    def _refresh_theme(self):
        self._build()
