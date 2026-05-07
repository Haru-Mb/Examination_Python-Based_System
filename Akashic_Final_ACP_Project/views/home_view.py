"""
Home / Landing page view — with gradient canvas background, dark mode switch top-right
"""
import tkinter as tk
from views.components.theme import get_theme, on_theme_change, toggle_theme


def _is_dark():
    from config import THEMES
    return get_theme() == THEMES["dark"]


class HomeView(tk.Frame):
    def __init__(self, parent, on_get_started=None):
        t = get_theme()
        super().__init__(parent, bg=t["bg"])
        self._on_get_started = on_get_started
        on_theme_change(self.refresh_theme)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        t = get_theme()
        bg = t["bg"]
        self.configure(bg=bg)

        # ── Full-canvas background with gradient/mesh ──────────────────────
        canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=bg)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._canvas = canvas

        def _draw_bg(event=None):
            canvas.delete("all")
            w = canvas.winfo_width() or 1280
            h = canvas.winfo_height() or 780

            if _is_dark():
                base_col  = "#0D0F14"
                blob1_col = "#0f2042"
                blob2_col = "#1a0f38"
                blob3_col = "#0a1a30"
                grid_col  = "#151925"
                dot_col   = "#1e2a40"
            else:
                base_col  = "#F4F6FB"
                blob1_col = "#dde8fa"
                blob2_col = "#e8ddf8"
                blob3_col = "#d6edf5"
                grid_col  = "#e8ecf5"
                dot_col   = "#cdd6ea"

            canvas.create_rectangle(0, 0, w, h, fill=base_col, outline="")

            # Dot-grid overlay
            step, r = 32, 1
            for gx in range(0, w + step, step):
                for gy in range(0, h + step, step):
                    canvas.create_oval(gx-r, gy-r, gx+r, gy+r, fill=dot_col, outline="")

            # Radial blobs
            _draw_radial_blob(canvas, int(w*.15), int(h*.2),  int(min(w,h)*.38), blob1_col, base_col, 10)
            _draw_radial_blob(canvas, int(w*.85), int(h*.8),  int(min(w,h)*.32), blob2_col, base_col, 10)
            _draw_radial_blob(canvas, int(w*.5),  int(h*.45), int(min(w,h)*.22), blob3_col, base_col, 8)

            # Diagonal lines
            for i in range(-20, 40):
                x0 = i * 80
                canvas.create_line(x0, 0, x0 + h, h, fill=grid_col, width=1)

        canvas.bind("<Configure>", _draw_bg)
        self.after(30, _draw_bg)

        # ── Dark-mode toggle — top right ───────────────────────────────────
        # Use a real bg color so tkinter doesn't error
        toggle_outer = tk.Frame(self, bg=t["card"], padx=2, pady=2)
        toggle_outer.place(relx=1.0, x=-16, y=14, anchor="ne")
        self._toggle_outer = toggle_outer
        self._toggle_btn_ref = [None]

        def _make_toggle():
            if self._toggle_btn_ref[0]:
                self._toggle_btn_ref[0].destroy()
            t2 = get_theme()
            lbl = "☀  Light" if _is_dark() else "☾  Dark"
            btn = tk.Button(
                toggle_outer, text=lbl,
                bg=t2["card"], fg=t2["text"],
                activebackground=t2["accent"], activeforeground="#FFFFFF",
                font=("Helvetica", 10, "bold"), relief="flat", bd=0,
                padx=14, pady=6, cursor="hand2",
                command=lambda: [toggle_theme(), _make_toggle()]
            )
            btn.pack()
            self._toggle_btn_ref[0] = btn

        _make_toggle()
        self._make_toggle = _make_toggle

        # ── Center content — use real bg color (matches canvas base) ───────
        outer = tk.Frame(self, bg=bg)
        outer.place(relx=0.5, rely=0.5, anchor="center")

        # Accent badge
        badge = tk.Frame(outer, bg=t["accent_glow"], padx=16, pady=6)
        badge.pack(pady=(0, 18))
        tk.Label(badge, text="Philippine Academic Examination System",
                 bg=t["accent_glow"], fg=t["accent"],
                 font=("Helvetica", 11, "bold")).pack()

        # Main headline
        tk.Label(outer, text="AKASHIC",
                 bg=bg, fg=t["text"],
                 font=("Helvetica", 64, "bold")).pack()

        tk.Label(outer,
                 text="Secure Exams. Real-time Scoring. Philippine CHED Grading.",
                 bg=bg, fg=t["text2"],
                 font=("Helvetica", 14)).pack(pady=(6, 32))

        # CTA button
        tk.Button(
            outer, text="Get Started  →",
            bg=t["accent"], fg="#FFFFFF",
            activebackground=t["accent2"], activeforeground="#FFFFFF",
            font=("Helvetica", 14, "bold"), relief="flat", bd=0,
            padx=32, pady=14, cursor="hand2",
            command=self._on_get_started
        ).pack()

        # Feature pills
        pills_row = tk.Frame(outer, bg=bg)
        pills_row.pack(pady=(36, 0))

        for icon, label in [("🔒","Anti-Cheat"),("🏆","Leaderboards"),("📊","PH Grading"),("⚡","Timed Quizzes")]:
            pill = tk.Frame(pills_row, bg=t["card"], padx=14, pady=8)
            pill.pack(side="left", padx=8)
            tk.Label(pill, text=f"{icon}  {label}",
                     bg=t["card"], fg=t["text"],
                     font=("Helvetica", 11)).pack()

    def refresh_theme(self, t=None):
        self._build()


def _draw_radial_blob(canvas, cx, cy, radius, inner_col, outer_col, steps=10):
    ic = _hex_to_rgb(inner_col)
    oc = _hex_to_rgb(outer_col)
    for i in range(steps, 0, -1):
        ratio = i / steps
        r = int(radius * ratio)
        blend = tuple(int(ic[j] * (1 - ratio) + oc[j] * ratio) for j in range(3))
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#%02x%02x%02x" % blend, outline="")


def _hex_to_rgb(hex_col):
    hex_col = hex_col.lstrip("#")
    return tuple(int(hex_col[i:i+2], 16) for i in (0, 2, 4))
