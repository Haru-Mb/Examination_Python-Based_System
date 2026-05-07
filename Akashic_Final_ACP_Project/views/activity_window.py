"""
Activity Window — Kahoot-style timed quiz with countdown
"""
import tkinter as tk
from views.components.theme import get_theme
import controllers.student_controller as sc


class ActivityWindow(tk.Toplevel):
    def __init__(self, parent, data, submission_id, class_id=None, on_submit=None):
        super().__init__(parent)
        t = get_theme()
        self.configure(bg=t["bg"])

        test = data["test"]
        self._questions = data["questions"]
        self._sub_id = submission_id
        self._class_id = class_id
        self._on_submit = on_submit
        self._answers = {}
        self._current = 0
        self._time_per_q = 20  # seconds per question
        self._timer_id = None
        self._time_left = self._time_per_q

        self.title(f"⚡ Activity — {test['title']}")
        self.geometry("860x560")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._force_submit)

        self._build(t, test)

    def _build(self, t, test):
        # Header
        header = tk.Frame(self, bg=t["accent2"], padx=20, pady=12)
        header.pack(fill="x")
        tk.Label(header, text=f"⚡ {test['title']}", bg=t["accent2"], fg="#FFF",
                 font=("Helvetica", 14, "bold")).pack(side="left")

        self._timer_lbl = tk.Label(header, text="20", bg=t["accent2"], fg="#FFF",
                                   font=("Helvetica", 22, "bold"))
        self._timer_lbl.pack(side="right")
        tk.Label(header, text="sec  ", bg=t["accent2"], fg="#FFF",
                 font=("Helvetica", 11)).pack(side="right")

        # Progress bar
        self._prog_canvas = tk.Canvas(self, bg=t["bg3"], height=6, highlightthickness=0)
        self._prog_canvas.pack(fill="x")

        # Question area
        self._q_frame = tk.Frame(self, bg=t["bg"], padx=40, pady=24)
        self._q_frame.pack(fill="both", expand=True)

        self._show_question()

    def _show_question(self):
        for w in self._q_frame.winfo_children():
            w.destroy()
        t = get_theme()

        if self._current >= len(self._questions):
            self._force_submit()
            return

        q = self._questions[self._current]
        total = len(self._questions)

        # Progress bar
        pct = self._current / total
        self._prog_canvas.delete("all")
        w = self._prog_canvas.winfo_width() or 860
        self._prog_canvas.create_rectangle(0, 0, w * pct, 6, fill=t["accent"], outline="")

        tk.Label(self._q_frame,
                 text=f"Question {self._current + 1} of {total}",
                 bg=t["bg"], fg=t["text2"], font=("Helvetica", 10)).pack(anchor="w")

        tk.Label(self._q_frame, text=q["question_text"],
                 bg=t["bg"], fg=t["text"],
                 font=("Helvetica", 16, "bold"), wraplength=740, justify="left").pack(anchor="w", pady=(8, 24))

        # Options as big clickable buttons
        q_type = q["question_type"]
        COLORS = ["#4F8EF7", "#7B5CF5", "#34D399", "#FBBF24"]

        if q_type == "multiple_choice":
            options = [o.strip() for o in q.get("options", "").split("\n") if o.strip()]
            grid = tk.Frame(self._q_frame, bg=t["bg"])
            grid.pack(fill="x")
            for i, opt in enumerate(options):
                color = COLORS[i % len(COLORS)]
                btn = tk.Button(grid, text=opt, bg=color, fg="#FFF",
                                activebackground=color, activeforeground="#FFF",
                                font=("Helvetica", 13, "bold"), relief="flat", bd=0,
                                padx=20, pady=16, cursor="hand2",
                                command=lambda o=opt, qid=q["id"]: self._answer_mc(qid, o))
                col = i % 2
                row = i // 2
                btn.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
            grid.columnconfigure(0, weight=1)
            grid.columnconfigure(1, weight=1)

        elif q_type == "true_false":
            row = tk.Frame(self._q_frame, bg=t["bg"])
            row.pack()
            for val, color in [("True", COLORS[2]), ("False", COLORS[3])]:
                tk.Button(row, text=val, bg=color, fg="#FFF",
                          activebackground=color, activeforeground="#FFF",
                          font=("Helvetica", 16, "bold"), relief="flat", bd=0,
                          padx=40, pady=20, cursor="hand2",
                          command=lambda v=val.lower(), qid=q["id"]: self._answer_mc(qid, v)
                          ).pack(side="left", padx=12)

        else:
            var = tk.StringVar()
            txt = tk.Text(self._q_frame, bg=t["bg2"], fg=t["text"],
                          insertbackground=t["text"], relief="flat", bd=0,
                          font=("Helvetica", 13), width=60, height=4)
            txt.pack(anchor="w")
            tk.Button(self._q_frame, text="Submit Answer →",
                      bg=t["accent"], fg="#FFF",
                      activebackground=t["accent2"], activeforeground="#FFF",
                      font=("Helvetica", 12, "bold"), relief="flat", bd=0,
                      padx=16, pady=8, cursor="hand2",
                      command=lambda qid=q["id"]: self._answer_mc(
                          qid, txt.get("1.0", tk.END).strip())).pack(anchor="w", pady=(8, 0))

        # Start countdown
        self._restart_timer()

    def _answer_mc(self, question_id, value):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self._answers[question_id] = value
        self._current += 1
        if self._current >= len(self._questions):
            self._force_submit()
        else:
            self._time_left = self._time_per_q
            self._show_question()

    def _restart_timer(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self._time_left = self._time_per_q
        self._tick()

    def _tick(self):
        t = get_theme()
        self._timer_lbl.config(text=str(self._time_left))
        if self._time_left <= 5:
            self._timer_lbl.config(fg=t["danger"])
        else:
            self._timer_lbl.config(fg="#FFF")

        if self._time_left <= 0:
            # Auto-advance
            q = self._questions[self._current] if self._current < len(self._questions) else None
            if q:
                self._answers.setdefault(q["id"], "")
            self._current += 1
            if self._current >= len(self._questions):
                self._force_submit()
            else:
                self._show_question()
            return

        self._time_left -= 1
        self._timer_id = self.after(1000, self._tick)

    def _force_submit(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
        self.grab_release()
        result = sc.finish_test(self._sub_id, self._answers)
        self.destroy()
        if self._on_submit:
            self._on_submit(result)
