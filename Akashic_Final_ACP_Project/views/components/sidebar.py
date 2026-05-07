"""
Sidebar navigation component — theme toggle removed (now top-right switch in main)
"""
import tkinter as tk
from views.components.theme import get_theme, toggle_theme, on_theme_change


class Sidebar(tk.Frame):
    def __init__(self, parent, menu_items, on_logout, active_key=None, **kwargs):
        t = get_theme()
        super().__init__(parent, bg=t["bg2"], width=t["sidebar_w"], **kwargs)
        self.pack_propagate(False)

        self._menu_items = menu_items
        self._on_logout = on_logout
        self._active_key = active_key or (menu_items[0][0] if menu_items else None)
        self._btn_refs = {}
        self._on_nav_callbacks = []

        on_theme_change(self._refresh)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        t = get_theme()
        self.configure(bg=t["bg2"])

        # Logo area
        logo_frame = tk.Frame(self, bg=t["bg2"], pady=0)
        logo_frame.pack(fill="x", padx=16, pady=(20, 4))

        logo_dot = tk.Frame(logo_frame, bg=t["accent"], width=10, height=10)
        logo_dot.pack(side="left", pady=6)

        tk.Label(logo_frame, text="  AKASHIC", bg=t["bg2"], fg=t["text"],
                 font=("Helvetica", 15, "bold")).pack(side="left")

        # Divider
        tk.Frame(self, bg=t["border"], height=1).pack(fill="x", padx=16, pady=(8, 12))

        # Nav items
        nav_frame = tk.Frame(self, bg=t["bg2"])
        nav_frame.pack(fill="both", expand=True)

        for key, label, icon in self._menu_items:
            self._make_nav_btn(nav_frame, key, label, icon)

        # Bottom: logout only (theme toggle moved to top-right)
        bottom = tk.Frame(self, bg=t["bg2"])
        bottom.pack(fill="x", padx=10, pady=12)

        tk.Frame(bottom, bg=t["border"], height=1).pack(fill="x", pady=(0, 10))

        # Logout button — dark bg, light contrasting text
        tk.Button(
            bottom, text="⎋  Logout",
            bg="#2a1020", fg="#f87171",
            activebackground="#3a1830", activeforeground="#fca5a5",
            font=("Helvetica", 10, "bold"), relief="flat", bd=0,
            cursor="hand2", padx=10, pady=8,
            command=self._on_logout
        ).pack(fill="x")

    def _make_nav_btn(self, parent, key, label, icon):
        t = get_theme()
        is_active = key == self._active_key

        bg = t["accent_glow"] if is_active else t["bg2"]
        fg = t["accent"] if is_active else t["text2"]
        lw = 3 if is_active else 0

        container = tk.Frame(parent, bg=t["bg2"])
        container.pack(fill="x", padx=8, pady=2)

        # Active indicator bar
        indicator = tk.Frame(container, bg=t["accent"] if is_active else t["bg2"], width=lw)
        indicator.pack(side="left", fill="y")

        btn = tk.Button(
            container,
            text=f"  {icon}  {label}",
            bg=bg, fg=fg,
            activebackground=t["card_hover"],
            activeforeground=t["accent"],
            font=("Helvetica", 11, "bold" if is_active else "normal"),
            relief="flat", bd=0,
            anchor="w", padx=12, pady=9,
            cursor="hand2",
            command=lambda k=key: self._on_nav(k)
        )
        btn.pack(fill="x")
        self._btn_refs[key] = (container, btn, indicator)

    def _on_nav(self, key):
        self._active_key = key
        self._build()
        for cb in self._on_nav_callbacks:
            cb(key)

    def on_navigate(self, callback):
        self._on_nav_callbacks.append(callback)

    def set_active(self, key):
        self._active_key = key
        self._build()

    def _refresh(self):
        self._build()


def _is_dark():
    from config import THEMES
    from views.components.theme import get_theme
    return get_theme() == THEMES["dark"]
