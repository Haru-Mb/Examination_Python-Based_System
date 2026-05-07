"""
Akashik Examination System
Entry point — bootstraps the app, manages page routing
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_NAME, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
)
from models.database import init_db
from views.components.theme import get_theme, apply_ttk_theme, on_theme_change, toggle_theme
from views.home_view import HomeView
from views.auth_view import AuthView


def _is_dark():
    from config import THEMES
    return get_theme() == THEMES["dark"]


class AkashikApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        init_db()
        self._style = apply_ttk_theme(self)
        t = get_theme()
        self.configure(bg=t["bg"])

        on_theme_change(self._on_theme_changed)

        self._page = None
        self._topbar = None
        self._show_home()
        self._center()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_theme_changed(self):
        apply_ttk_theme(self)
        t = get_theme()
        self.configure(bg=t["bg"])
        if self._page and hasattr(self._page, 'refresh_theme'):
            self._page.refresh_theme(t)
        if self._topbar:
            self._refresh_topbar()

    def _clear(self):
        if self._topbar:
            self._topbar.place_forget()
            self._topbar.destroy()
            self._topbar = None
        if self._page:
            self._page.pack_forget()
            self._page.destroy()
            self._page = None

    def _add_topbar_toggle(self):
        """Adds a dark/light mode toggle switch in the top-right corner of the window."""
        if self._topbar:
            self._topbar.destroy()

        t = get_theme()
        is_dark = _is_dark()

        bar = tk.Frame(self, bg=t["bg2"], padx=8, pady=4)
        bar.place(relx=1.0, x=-12, y=10, anchor="ne")
        self._topbar = bar

        lbl = "☀  Light Mode" if is_dark else "☾  Dark Mode"

        toggle_btn = tk.Button(
            bar, text=lbl,
            bg=t["card"], fg=t["text"],
            activebackground=t["accent"], activeforeground="#FFFFFF",
            font=("Helvetica", 10, "bold"), relief="flat", bd=0,
            padx=12, pady=5, cursor="hand2",
            command=toggle_theme
        )
        toggle_btn.pack()

    def _refresh_topbar(self):
        self._add_topbar_toggle()

    def _show_home(self):
        self._clear()
        t = get_theme()
        self.configure(bg=t["bg"])
        self._page = HomeView(self, on_get_started=self._show_auth)
        self._page.pack(fill="both", expand=True)
        # Home view has its own embedded toggle

    def _show_auth(self):
        self._clear()
        t = get_theme()
        self.configure(bg=t["bg"])
        self._page = AuthView(
            self,
            on_login_success=self._on_login,
            on_back=self._show_home
        )
        self._page.pack(fill="both", expand=True)
        self._add_topbar_toggle()

    def _on_login(self, user):
        self._clear()
        t = get_theme()
        self.configure(bg=t["bg"])

        if user.get("role") == "student":
            from views.student_dashboard_view import StudentDashboard
            self._page = StudentDashboard(self, on_logout=self._show_home)
        else:
            from views.professor_dashboard_view import ProfessorDashboard
            self._page = ProfessorDashboard(self, on_logout=self._show_home)

        self._page.pack(fill="both", expand=True)
        self._add_topbar_toggle()


def main():
    try:
        app = AkashikApp()
        app.mainloop()
    except Exception as e:
        print(f"Startup Error: {e}")


if __name__ == "__main__":
    main()
