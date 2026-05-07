"""
Professor Dashboard View
"""
import tkinter as tk
from tkinter import ttk
from views.components.theme import get_theme, on_theme_change
from views.components.sidebar import Sidebar
from views.components.modal import toast, confirm_dialog, input_dialog
from utils.session_manager import get_current_user
import controllers.professor_controller as pc


MENU = [
    ("home",     "Home",         "⌂"),
    ("create",   "Create",       "＋"),
    ("students", "Student Data", "👥"),
    ("flagged",  "Flagged",      "⚠"),
    ("settings", "Settings",     "⚙"),
]


class ProfessorDashboard(tk.Frame):
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
        elif key == "create":
            self._show_create()
        elif key == "students":
            self._show_students()
        elif key == "flagged":
            self._show_flagged()
        elif key == "settings":
            self._show_settings()

    def _page_header(self, parent, title, subtitle="", btn_text=None, btn_cmd=None):
        t = get_theme()
        hdr = tk.Frame(parent, bg=t["bg"])
        hdr.pack(fill="x", padx=32, pady=(28, 16))

        left = tk.Frame(hdr, bg=t["bg"])
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text=title, bg=t["bg"], fg=t["text"],
                 font=("Helvetica", 22, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(left, text=subtitle, bg=t["bg"], fg=t["text2"],
                     font=("Helvetica", 11)).pack(anchor="w")

        if btn_text and btn_cmd:
            tk.Button(hdr, text=btn_text,
                      bg=t["accent"], fg="#FFF",
                      activebackground=t["accent2"], activeforeground="#FFF",
                      relief="flat", bd=0, font=("Helvetica", 11, "bold"),
                      padx=16, pady=8, cursor="hand2", command=btn_cmd).pack(side="right")

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
        classes = pc.get_my_classes()

        self._page_header(self._content,
                          f"Dashboard — {user.get('nickname') or user['username']}",
                          "Manage your classes and tests.",
                          btn_text="＋ New Class",
                          btn_cmd=self._create_class)

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        # Stats
        stats_row = tk.Frame(pad, bg=t["bg"])
        stats_row.pack(fill="x", pady=(0, 24))

        total_students = sum(len([s for s in pc.get_students(c["id"]) if not s["is_removed"]]) for c in classes)
        total_tests = sum(len(pc.get_class_tests(c["id"])) for c in classes)

        for label, val, color in [
            ("Classes", len(classes), t["accent"]),
            ("Total Students", total_students, t["success"]),
            ("Tests & Activities", total_tests, t["accent2"]),
        ]:
            card = tk.Frame(stats_row, bg=t["card"], padx=24, pady=18)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            tk.Label(card, text=str(val), bg=t["card"], fg=color,
                     font=("Helvetica", 28, "bold")).pack(anchor="w")
            tk.Label(card, text=label, bg=t["card"], fg=t["text2"],
                     font=("Helvetica", 11)).pack(anchor="w")

        # Class list
        tk.Label(pad, text="Your Classes", bg=t["bg"], fg=t["text"],
                 font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(0, 12))

        if not classes:
            tk.Label(pad, text="No classes yet. Click '+ New Class' to create one.",
                     bg=t["bg"], fg=t["text3"], font=("Helvetica", 12)).pack(anchor="w")
        else:
            for cls in classes:
                self._class_card(pad, cls)

    def _class_card(self, parent, cls):
        t = get_theme()
        students = [s for s in pc.get_students(cls["id"]) if not s.get("is_removed")]
        tests = pc.get_class_tests(cls["id"])

        card = tk.Frame(parent, bg=t["card"], padx=20, pady=14)
        card.pack(fill="x", pady=(0, 8))

        top = tk.Frame(card, bg=t["card"])
        top.pack(fill="x")

        left = tk.Frame(top, bg=t["card"])
        left.pack(side="left", fill="x", expand=True)

        tk.Label(left, text=cls["name"], bg=t["card"], fg=t["text"],
                 font=("Helvetica", 13, "bold")).pack(anchor="w")

        code_badge = tk.Frame(left, bg=t["accent_glow"], padx=8, pady=2)
        code_badge.pack(anchor="w", pady=(4, 0))
        tk.Label(code_badge, text=f"Code: {cls['class_code']}",
                 bg=t["accent_glow"], fg=t["accent"],
                 font=("Helvetica", 10, "bold")).pack()

        meta = tk.Frame(top, bg=t["card"])
        meta.pack(side="right")
        for val, lbl in [(len(students), "students"), (len(tests), "tests")]:
            m = tk.Frame(meta, bg=t["card"], padx=12)
            m.pack(side="left")
            tk.Label(m, text=str(val), bg=t["card"], fg=t["text"],
                     font=("Helvetica", 16, "bold")).pack()
            tk.Label(m, text=lbl, bg=t["card"], fg=t["text3"],
                     font=("Helvetica", 9)).pack()

    def _create_class(self):
        t = get_theme()
        input_dialog(self, "Create New Class", "Class name:",
                     on_submit=self._do_create_class)

    def _do_create_class(self, name):
        if not name:
            return
        result = pc.create_new_class(name)
        if result["ok"]:
            cls = result["class"]
            toast(self, f"Class created! Code: {cls['class_code']}", kind="success")
            self._show("home")
        else:
            toast(self, result.get("error", "Failed."), kind="error")

    # ── CREATE ──────────────────────────────────────────────────────────────
    def _show_create(self):
        t = get_theme()
        classes = pc.get_my_classes()
        self._page_header(self._content, "Create Test / Activity ＋",
                          "Build tests and activities for your classes")

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        if not classes:
            tk.Label(pad, text="Create a class first.",
                     bg=t["bg"], fg=t["text3"], font=("Helvetica", 12)).pack(anchor="w")
            return

        # Form card
        form = tk.Frame(pad, bg=t["card"], padx=28, pady=24)
        form.pack(anchor="nw", fill="x", ipadx=0)

        tk.Label(form, text="New Assessment", bg=t["card"], fg=t["text"],
                 font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(0, 16))

        # Class selector
        tk.Label(form, text="Select Class", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w", pady=(0, 4))
        cls_var = tk.StringVar()
        cls_map = {c["name"]: c["id"] for c in classes}
        cls_combo = ttk.Combobox(form, textvariable=cls_var,
                                 values=list(cls_map.keys()), state="readonly", width=36)
        cls_combo.pack(anchor="w", pady=(0, 12))
        if classes:
            cls_combo.current(0)

        # Title
        tk.Label(form, text="Title", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w", pady=(0, 4))
        title_var = tk.StringVar()
        tk.Entry(form, textvariable=title_var, bg=t["bg2"], fg=t["text"],
                 insertbackground=t["text"], relief="flat", bd=0,
                 font=("Helvetica", 12), width=40).pack(anchor="w", ipady=8, pady=(0, 12))

        # Description
        tk.Label(form, text="Description (optional)", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w", pady=(0, 4))
        desc_text = tk.Text(form, bg=t["bg2"], fg=t["text"],
                            insertbackground=t["text"], relief="flat", bd=0,
                            font=("Helvetica", 11), width=40, height=3)
        desc_text.pack(anchor="w", pady=(0, 12))

        # Type + time
        row = tk.Frame(form, bg=t["card"])
        row.pack(anchor="w", pady=(0, 12))

        type_var = tk.StringVar(value="test")
        tk.Label(row, text="Type:", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(side="left", padx=(0, 8))
        for val, lbl in [("test", "Test"), ("activity", "Activity")]:
            tk.Radiobutton(row, text=lbl, value=val, variable=type_var,
                           bg=t["card"], fg=t["text"],
                           activebackground=t["card"],
                           selectcolor=t["accent"],
                           font=("Helvetica", 11)).pack(side="left", padx=(0, 16))

        tk.Label(row, text="Time (min):", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(side="left", padx=(16, 8))
        time_var = tk.StringVar(value="30")
        tk.Entry(row, textvariable=time_var, bg=t["bg2"], fg=t["text"],
                 insertbackground=t["text"], relief="flat", bd=0,
                 font=("Helvetica", 12), width=6).pack(side="left", ipady=6)

        err_lbl = tk.Label(form, text="", bg=t["card"], fg=t["danger"],
                           font=("Helvetica", 10))
        err_lbl.pack(anchor="w", pady=(4, 0))

        # Questions section (shown after creating the test)
        self._questions_container = tk.Frame(pad, bg=t["bg"])
        self._current_test_id = None
        self._questions_list = []

        def do_create():
            class_name = cls_var.get()
            title = title_var.get().strip()
            desc = desc_text.get("1.0", tk.END).strip()
            kind = type_var.get()
            try:
                tl = int(time_var.get())
            except ValueError:
                tl = 0

            if not class_name or not title:
                err_lbl.config(text="Class and title are required.")
                return

            class_id = cls_map[class_name]
            result = pc.create_new_test(class_id, title, desc, kind, tl)
            if result["ok"]:
                self._current_test_id = result["test"]["id"]
                self._questions_list = []
                toast(self, "Test created! Now add questions below.", kind="success")
                self._build_question_builder(self._questions_container, result["test"])
                self._questions_container.pack(fill="x", pady=(16, 0))
            else:
                err_lbl.config(text=result.get("error", "Failed."))

        tk.Button(form, text="Create & Add Questions →",
                  bg=t["accent"], fg="#FFF",
                  activebackground=t["accent2"], activeforeground="#FFF",
                  font=("Helvetica", 12, "bold"), relief="flat", bd=0,
                  padx=20, pady=10, cursor="hand2", command=do_create).pack(anchor="w", pady=(12, 0))

    def _build_question_builder(self, parent, test):
        for w in parent.winfo_children():
            w.destroy()
        t = get_theme()

        header = tk.Frame(parent, bg=t["bg"])
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text=f"Questions for: {test['title']}", bg=t["bg"], fg=t["text"],
                 font=("Helvetica", 14, "bold")).pack(side="left")
        tk.Button(header, text="✓ Publish Test",
                  bg=t["success"], fg="#FFF",
                  activebackground=t["success"], activeforeground="#FFF",
                  font=("Helvetica", 11, "bold"), relief="flat", bd=0,
                  padx=14, pady=7, cursor="hand2",
                  command=lambda tid=test["id"]: self._publish_test(tid)).pack(side="right")

        # Question form
        qform = tk.Frame(parent, bg=t["card"], padx=24, pady=18)
        qform.pack(fill="x")

        tk.Label(qform, text="Question Text", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w")
        q_text = tk.Text(qform, bg=t["bg2"], fg=t["text"],
                         insertbackground=t["text"], relief="flat", bd=0,
                         font=("Helvetica", 11), width=60, height=3)
        q_text.pack(anchor="w", pady=(4, 10))

        row = tk.Frame(qform, bg=t["card"])
        row.pack(anchor="w", pady=(0, 10))

        tk.Label(row, text="Type:", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(side="left", padx=(0, 8))
        qt_var = tk.StringVar(value="multiple_choice")
        qt_combo = ttk.Combobox(row, textvariable=qt_var, state="readonly", width=18,
                                values=["multiple_choice", "true_false", "short_answer", "essay"])
        qt_combo.pack(side="left", padx=(0, 20))

        tk.Label(row, text="Points:", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(side="left", padx=(0, 6))
        pts_var = tk.StringVar(value="1")
        tk.Entry(row, textvariable=pts_var, bg=t["bg2"], fg=t["text"],
                 insertbackground=t["text"], relief="flat", bd=0,
                 font=("Helvetica", 11), width=4).pack(side="left", ipady=5)

        tk.Label(qform, text="Options (one per line, for MC)", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w")
        opts_text = tk.Text(qform, bg=t["bg2"], fg=t["text"],
                            insertbackground=t["text"], relief="flat", bd=0,
                            font=("Helvetica", 11), width=60, height=4)
        opts_text.pack(anchor="w", pady=(4, 8))

        tk.Label(qform, text="Correct Answer", bg=t["card"], fg=t["text2"],
                 font=("Helvetica", 10)).pack(anchor="w")
        ans_var = tk.StringVar()
        tk.Entry(qform, textvariable=ans_var, bg=t["bg2"], fg=t["text"],
                 insertbackground=t["text"], relief="flat", bd=0,
                 font=("Helvetica", 12), width=40).pack(anchor="w", ipady=8, pady=(4, 12))

        # Questions list display
        self._q_list_frame = tk.Frame(parent, bg=t["bg"])
        self._q_list_frame.pack(fill="x", pady=(12, 0))
        self._render_q_list(t)

        def add_question():
            qtext = q_text.get("1.0", tk.END).strip()
            if not qtext:
                toast(self, "Question text is required.", kind="error")
                return
            try:
                pts = int(pts_var.get())
            except ValueError:
                pts = 1
            order = len(self._questions_list) + 1
            opts = opts_text.get("1.0", tk.END).strip()
            ans = ans_var.get().strip()

            result = pc.add_test_question(
                self._current_test_id, qtext, qt_var.get(),
                opts, ans, pts, order
            )
            if result["ok"]:
                self._questions_list.append({
                    "text": qtext, "type": qt_var.get(),
                    "points": pts, "order": order
                })
                q_text.delete("1.0", tk.END)
                opts_text.delete("1.0", tk.END)
                ans_var.set("")
                self._render_q_list(t)
                toast(self, "Question added!", kind="success")
            else:
                toast(self, result.get("error", "Failed."), kind="error")

        tk.Button(qform, text="＋ Add Question",
                  bg=t["accent2"], fg="#FFF",
                  activebackground=t["accent"], activeforeground="#FFF",
                  font=("Helvetica", 11, "bold"), relief="flat", bd=0,
                  padx=16, pady=8, cursor="hand2", command=add_question).pack(anchor="w")

    def _render_q_list(self, t):
        for w in self._q_list_frame.winfo_children():
            w.destroy()
        if not self._questions_list:
            return
        tk.Label(self._q_list_frame, text=f"{len(self._questions_list)} question(s) added:",
                 bg=t["bg"], fg=t["text2"], font=("Helvetica", 10)).pack(anchor="w", pady=(0, 6))
        for i, q in enumerate(self._questions_list, 1):
            row = tk.Frame(self._q_list_frame, bg=t["card"], padx=14, pady=8)
            row.pack(fill="x", pady=(0, 4))
            tk.Label(row, text=f"{i}. {q['text'][:60]}{'...' if len(q['text']) > 60 else ''}",
                     bg=t["card"], fg=t["text"], font=("Helvetica", 11)).pack(side="left")
            tk.Label(row, text=f"{q['type']} · {q['points']}pt",
                     bg=t["card"], fg=t["text3"], font=("Helvetica", 10)).pack(side="right")

    def _publish_test(self, test_id):
        pc.publish(test_id)
        toast(self, "Test published! Students can now see it.", kind="success")
        self._show("home")
        self._sidebar.set_active("home")

    # ── STUDENTS ────────────────────────────────────────────────────────────
    def _show_students(self):
        t = get_theme()
        classes = pc.get_my_classes()
        self._page_header(self._content, "Student Data 👥",
                          "View grades, ranks, and manage enrollment")

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        if not classes:
            tk.Label(pad, text="No classes yet.", bg=t["bg"], fg=t["text3"],
                     font=("Helvetica", 12)).pack(anchor="w")
            return

        for cls in classes:
            tk.Label(pad, text=cls["name"], bg=t["bg"], fg=t["text"],
                     font=("Helvetica", 14, "bold")).pack(anchor="w", pady=(12, 8))

            grades = pc.get_grades(cls["id"])
            if not grades:
                tk.Label(pad, text="No students enrolled.", bg=t["bg"], fg=t["text3"],
                         font=("Helvetica", 11)).pack(anchor="w", pady=(0, 8))
                continue

            # Table header
            hdr = tk.Frame(pad, bg=t["bg3"], padx=12, pady=7)
            hdr.pack(fill="x", pady=(0, 4))
            for col, w in [("Rank", 50), ("Name", 180), ("SR Code", 120),
                           ("Avg%", 80), ("Grade", 70), ("Remarks", 120), ("⚠", 40)]:
                tk.Label(hdr, text=col, bg=t["accent"], fg="#FFFFFF",
                         font=("Helvetica", 10, "bold"), width=w//8, anchor="w").pack(side="left")

            for g in grades:
                row = tk.Frame(pad, bg=t["card"], padx=12, pady=9)
                row.pack(fill="x", pady=(0, 3))
                grade_color = self._grade_color(g.get("grade", "5.00"), t)
                vals = [
                    (f"#{g['rank']}", 50, t["text2"]),
                    (g.get("nickname") or g["username"], 180, t["text"]),
                    (g["sr_code"], 120, t["text2"]),
                    (f"{g['avg_score']:.1f}%", 80, t["text"]),
                    (g["grade"], 70, grade_color),
                    (g["remarks"], 120, t["text2"]),
                    (str(g.get("flagged_count", 0)) if g.get("flagged_count") else "—", 40, t["text3"]),
                ]
                for val, w, color in vals:
                    tk.Label(row, text=val, bg=t["card"], fg=color,
                             font=("Helvetica", 11), width=w//8, anchor="w").pack(side="left")

                # Remove btn
                tk.Button(row, text="Remove",
                          bg="#2a1020", fg="#f87171",
                          activebackground="#3a1830", activeforeground="#fca5a5",
                          font=("Helvetica", 9), relief="flat", bd=0, padx=8, pady=4,
                          cursor="hand2",
                          command=lambda sid=g["id"], cid=cls["id"]: self._remove_student(cid, sid)
                          ).pack(side="right")

    def _grade_color(self, grade, t):
        try:
            g = float(grade)
            if g <= 1.5: return t["success"]
            if g <= 2.5: return t["accent"]
            if g <= 3.0: return t["warning"]
            return t["danger"]
        except Exception:
            return t["text2"]

    def _remove_student(self, class_id, student_id):
        confirm_dialog(self, "Remove Student",
                       "Remove this student from the class? They can rejoin with the class code.",
                       ok_text="Remove", ok_color=None,
                       on_confirm=lambda: self._do_remove(class_id, student_id))

    def _do_remove(self, class_id, student_id):
        result = pc.kick_student(class_id, student_id)
        if result["ok"]:
            toast(self, "Student removed.", kind="info")
            self._show("students")
        else:
            toast(self, result.get("error", "Failed."), kind="error")

    # ── FLAGGED ─────────────────────────────────────────────────────────────
    def _show_flagged(self):
        t = get_theme()
        classes = pc.get_my_classes()
        self._page_header(self._content, "⚠ Flagged Submissions",
                          "Students flagged for cheating (window focus lost during test)")

        scroll = self._scrollable(self._content)
        pad = tk.Frame(scroll, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=20)

        any_found = False
        for cls in classes:
            flagged = pc.get_flagged(cls["id"])
            if not flagged:
                continue
            any_found = True
            tk.Label(pad, text=cls["name"], bg=t["bg"], fg=t["text"],
                     font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(12, 6))
            for f in flagged:
                row = tk.Frame(pad, bg=t["card"], padx=16, pady=10)
                row.pack(fill="x", pady=(0, 6))

                tk.Label(row, text="⚠", bg=t["card"], fg=t["warning"],
                         font=("Helvetica", 14)).pack(side="left", padx=(0, 10))

                info = tk.Frame(row, bg=t["card"])
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=f"{f['username']} ({f['sr_code']})",
                         bg=t["card"], fg=t["text"], font=("Helvetica", 12, "bold")).pack(anchor="w")
                tk.Label(info, text=f"{f['title']} · {f.get('flag_reason','Window focus lost')}",
                         bg=t["card"], fg=t["text2"], font=("Helvetica", 10)).pack(anchor="w")

                if f.get("submitted_at"):
                    tk.Label(row, text=str(f["submitted_at"])[:16],
                             bg=t["card"], fg=t["text3"],
                             font=("Helvetica", 10)).pack(side="right")

        if not any_found:
            tk.Label(pad, text="No flagged submissions. 🎉",
                     bg=t["bg"], fg=t["text3"], font=("Helvetica", 12)).pack(anchor="w")

    # ── SETTINGS ────────────────────────────────────────────────────────────
    def _show_settings(self):
        t = get_theme()
        user = get_current_user()
        self._page_header(self._content, "Settings ⚙", "Account and preferences")

        pad = tk.Frame(self._content, bg=t["bg"])
        pad.pack(fill="both", expand=True, padx=32, pady=28)

        card = tk.Frame(pad, bg=t["card"], padx=28, pady=24)
        card.pack(anchor="nw")

        tk.Label(card, text="Account Info", bg=t["card"], fg=t["text"],
                 font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(0, 12))

        for label, val in [
            ("Username", user.get("username", "")),
            ("Email", user.get("email", "")),
            ("SR/Employee Code", user.get("sr_code", "")),
            ("Role", user.get("role", "").capitalize()),
        ]:
            row = tk.Frame(card, bg=t["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label + ":", bg=t["card"], fg=t["text2"],
                     font=("Helvetica", 11), width=18, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=t["card"], fg=t["text"],
                     font=("Helvetica", 11)).pack(side="left")

    def _logout(self):
        from controllers.auth_controller import logout_user
        logout_user()
        if self._on_logout:
            self._on_logout()

    def _refresh_theme(self):
        self._build()
