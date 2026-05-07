"""
Theme management — light/dark toggle, design tokens
"""
import tkinter as tk
from tkinter import ttk
from config import THEMES

_current_mode = "dark"
_observers = []


def get_theme() -> dict:
    return THEMES[_current_mode]


def toggle_theme():
    global _current_mode
    _current_mode = "light" if _current_mode == "dark" else "dark"
    for cb in _observers:
        try:
            cb()
        except Exception:
            pass


def on_theme_change(callback):
    _observers.append(callback)


def apply_ttk_theme(root) -> ttk.Style:
    t = get_theme()
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=t["bg"],
        foreground=t["text"],
        fieldbackground=t["bg2"],
        bordercolor=t["border"],
        darkcolor=t["bg2"],
        lightcolor=t["bg3"],
        troughcolor=t["bg2"],
        selectbackground=t["accent"],
        selectforeground="#FFFFFF",
        font=("Helvetica", 11),
    )
    style.configure("TFrame", background=t["bg"])
    style.configure("TLabel", background=t["bg"], foreground=t["text"])
    style.configure("TButton",
        background=t["accent"],
        foreground="#FFFFFF",
        borderwidth=0,
        relief="flat",
        padding=(12, 6),
        font=("Helvetica", 11, "bold"),
    )
    style.map("TButton",
        background=[("active", t["accent2"]), ("pressed", t["accent2"]), ("disabled", t["bg3"])],
        foreground=[("active", "#FFFFFF"), ("pressed", "#FFFFFF"), ("disabled", t["text3"])],
    )
    style.configure("TEntry",
        fieldbackground=t["bg2"],
        foreground=t["text"],
        insertcolor=t["text"],
        bordercolor=t["border"],
        relief="flat",
        padding=8,
    )
    style.configure("TCombobox",
        fieldbackground=t["bg2"],
        foreground=t["text"],
        background=t["bg2"],
        selectbackground=t["accent"],
        arrowcolor=t["text2"],
    )
    style.configure("Vertical.TScrollbar",
        background=t["bg2"],
        troughcolor=t["bg"],
        arrowcolor=t["text3"],
        borderwidth=0,
        relief="flat",
    )
    style.configure("Horizontal.TScrollbar",
        background=t["bg2"],
        troughcolor=t["bg"],
        arrowcolor=t["text3"],
        borderwidth=0,
        relief="flat",
    )
    return style
