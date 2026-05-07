"""
Test Window — anti-cheat secured, one question at a time
"""
import tkinter as tk
from views.components.theme import get_theme
from views.components.modal import toast
import controllers.student_controller as sc


class TestWindow(tk.Toplevel):
    def __init__(self, parent, data, submission_id, on_submit=None):
        super().__init__(parent)
        t = get_theme()
        self.configure(bg=t["bg"])

        test = data["test"]
        self._questions = data["questions"]
        self._sub_id = submission_id
        self._on_submit = on_submit
        self._answers = {}
        self._current = 0
        self._flagged = False
        self._flag_reason = ""

        self.title(f"TEST — {test['title']}")
        self.geometry("900x620")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Anti-cheat: bind focus loss
        self.bind("<FocusOut>", self._on_focus_lost)

        self._build(t, test)

    def _build(self, t, test):
        # Top bar
        topbar = tk.Frame(self, bg=t["bg2"], padx=24, pady=10)
        topbar.pack(fill="x")

        tk.Label(topbar, text=f"🔒 {test['title']}", bg=t["bg2"], fg=t["text"],
                 font=("Helvetica", 13, "bold")).pack(side="left")

        self._progress_lbl = tk.Label(topbar, text="", bg=t["bg2"], fg=t["text2"],
                                      font=("Helvetica", 11))
        self._progress_lbl.pack(side="right")

        # Anti-cheat warning banner (hidden by default)
        self._warn_frame = tk.Frame(self, bg=t["danger"], padx=20, pady=8)
        self._warn_lbl = tk.Label(self._warn_frame,
                                  text="⚠ Warning: Focus lost — your submission has been flagged.",
                                  bg=t["danger"], fg="#FFF", font=("Helvetica", 11, "bold"))
        self._warn_lbl.pack()

        # Question area
        self._q_frame = tk.Frame(self, bg=t["bg"], padx=40, pady=30)
        self._q_frame.pack(fill="both", expand=True)

        # Navigation buttons
        nav = tk.Frame(self, bg=t["bg2"], padx=24, pady=12)
        nav.pack(fill="x", side="bottom")

        self._prev_btn = tk.Button(nav, text="← Previous",
                                   bg=t["accent"], fg="#FFFFFF",
                                   activebackground=t["accent2"], activeforeground="#FFFFFF",
                                   font=("Helvetica", 11), relief="flat", bd=0,
                                   padx=16, pady=8, cursor="hand2",
                                   command=self._prev)
        self._prev_btn.pack(side="left")

        self._next_btn = tk.Button(nav, text="Next →",
                                   bg=t["accent"], fg="#FFF",
                                   activebackground=t["accent2"], activeforeground="#FFF",
                                   font=("Helvetica", 11, "bold"), relief="flat", bd=0,
                                   padx=16, pady=8, cursor="hand2",
                                   command=self._next)
        self._next_btn.pack(side="left", padx=(8, 0))

        self._submit_btn = tk.Button(nav, text="Submit Test ✓",
                                     bg=t["success"], fg="#FFF",
                                     activebackground=t["success"], activeforeground="#FFF",
                                     font=("Helvetica", 11, "bold"), relief="flat", bd=0,
                                     padx=16, pady=8, cursor="hand2",
                                     command=self._submit)

        self._show_question()

    def _show_question(self):
        for w in self._q_frame.winfo_children():
            w.destroy()
        t = get_theme()

        if not self._questions:
            tk.Label(self._q_frame, text="No questions in this test.",
                     bg=t["bg"], fg=t["text"], font=("Helvetica", 13)).pack()
            return

        q = self._questions[self._current]
        total = len(self._questions)
        self._progress_lbl.config(text=f"Question {self._current + 1} of {total}")

        # Question number badge
        badge_row = tk.Frame(self._q_frame, bg=t["bg"])
        badge_row.pack(anchor="w", pady=(0, 12))
        tk.Frame(badge_row, bg=t["accent"], width=4).pack(side="left", fill="y", padx=(0, 10))
        tk.Label(badge_row, text=f"Q{self._current + 1}  •  {q['question_type'].replace('_', ' ').title()}  •  {q['points']}pt",
                 bg=t["bg"], fg=t["accent"], font=("Helvetica", 10, "bold")).pack(side="left")

        # Question text
        tk.Label(self._q_frame, text=q["question_text"],
                 bg=t["bg"], fg=t["text"],
                 font=("Helvetica", 14), wraplength=780, justify="left").pack(anchor="w", pady=(0, 20))

        # Answer area
        self._answer_var = tk.StringVar(value=self._answers.get(q["id"], ""))
        q_type = q["question_type"]

        if q_type == "multiple_choice":
            options = [o.strip() for o in q.get("options", "").split("\n") if o.strip()]
            for opt in options:
                rb = tk.Radiobutton(self._q_frame, text=opt,
                                    variable=self._answer_var, value=opt,
                                    bg=t["bg"], fg=t["text"],
                                    activebackground=t["bg"],
                                    selectcolor=t["accent"],
                                    font=("Helvetica", 12))
                rb.pack(anchor="w", pady=4)

        elif q_type == "true_false":
            for opt in ["True", "False"]:
                tk.Radiobutton(self._q_frame, text=opt,
                               variable=self._answer_var, value=opt.lower(),
                               bg=t["bg"], fg=t["text"],
                               activebackground=t["bg"],
                               selectcolor=t["accent"],
                               font=("Helvetica", 12)).pack(anchor="w", pady=4)

        elif q_type in ("short_answer", "essay"):
            h = 3 if q_type == "short_answer" else 7
            txt = tk.Text(self._q_frame, bg=t["bg2"], fg=t["text"],
                          insertbackground=t["text"], relief="flat", bd=0,
                          font=("Helvetica", 12), width=70, height=h)
            txt.pack(anchor="w")
            prev = self._answers.get(q["id"], "")
            if prev:
                txt.insert("1.0", prev)
            # Override answer_var for text widget
            self._answer_text_widget = txt

        # Nav state
        self._prev_btn.config(state="normal" if self._current > 0 else "disabled")
        if self._current == len(self._questions) - 1:
            self._next_btn.pack_forget()
            self._submit_btn.pack(side="left", padx=(8, 0))
        else:
            self._submit_btn.pack_forget()
            self._next_btn.pack(side="left", padx=(8, 0))

    def _save_current_answer(self):
        q = self._questions[self._current]
        q_type = q["question_type"]
        if q_type in ("short_answer", "essay"):
            if hasattr(self, "_answer_text_widget"):
                self._answers[q["id"]] = self._answer_text_widget.get("1.0", tk.END).strip()
        else:
            self._answers[q["id"]] = self._answer_var.get()

    def _next(self):
        self._save_current_answer()
        if self._current < len(self._questions) - 1:
            self._current += 1
            self._show_question()

    def _prev(self):
        self._save_current_answer()
        if self._current > 0:
            self._current -= 1
            self._show_question()

    def _on_focus_lost(self, event):
        if not self._flagged:
            self._flagged = True
            self._flag_reason = "Window focus lost during test"
            self._warn_frame.pack(fill="x", after=self.winfo_children()[0])

    def _on_close(self):
        # Force submit on close
        self._save_current_answer()
        self._submit()

    def _submit(self):
        self._save_current_answer()
        self.grab_release()
        result = sc.finish_test(self._sub_id, self._answers,
                                flagged=self._flagged, reason=self._flag_reason)
        self.destroy()
        if self._on_submit:
            self._on_submit(result)
