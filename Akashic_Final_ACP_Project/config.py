"""
Akashik Configuration
"""
import os
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "akashik.db")
 
# App Info
APP_NAME = "Akashik"
APP_VERSION = "1.0.0"
 
# Window
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 700
WINDOW_DEFAULT_WIDTH = 1280
WINDOW_DEFAULT_HEIGHT = 780
 
# Email (configure with real SMTP for production)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = ""  # Set your email
EMAIL_PASS = ""  # Set your app password
EMAIL_ENABLED = False  # Set True when email credentials are configured
 
# Session
SESSION_TIMEOUT_MINUTES = 120
 
# Grading (Philippine CHED System)
GRADE_TRANSMUTATION = {
    (99, 100): ("1.00", "Excellent"),
    (96, 98):  ("1.25", "Excellent"),
    (93, 95):  ("1.50", "Very Good"),
    (90, 92):  ("1.75", "Very Good"),
    (87, 89):  ("2.00", "Good"),
    (84, 86):  ("2.25", "Good"),
    (81, 83):  ("2.50", "Satisfactory"),
    (78, 80):  ("2.75", "Satisfactory"),
    (75, 77):  ("3.00", "Passing"),
    (0,  74):  ("5.00", "Failed"),
}
 
# Class code
CLASS_CODE_MIN_LEN = 9
CLASS_CODE_MAX_LEN = 11
 
# Themes
THEMES = {
    "dark": {
        "bg":           "#0D0F14",
        "bg2":          "#13161E",
        "bg3":          "#1A1E29",
        "card":         "#1E2330",
        "card_hover":   "#252B3B",
        "border":       "#2A3045",
        "accent":       "#4F8EF7",
        "accent2":      "#7B5CF5",
        "accent_glow":  "#1a2a4a",
        "success":      "#34D399",
        "warning":      "#FBBF24",
        "danger":       "#F87171",
        "text":         "#E8EAF0",
        "text2":        "#9AA3B8",
        "text3":        "#5C6480",
        "sidebar_w":    220,
    },
    "light": {
        "bg":           "#F4F6FB",
        "bg2":          "#EBEEF7",
        "bg3":          "#E2E7F4",
        "card":         "#FFFFFF",
        "card_hover":   "#F0F4FF",
        "border":       "#C8D0E0",
        "accent":       "#2563EB",
        "accent2":      "#5B21B6",
        "accent_glow":  "#dce8fa",
        "success":      "#059669",
        "warning":      "#D97706",
        "danger":       "#DC2626",
        "text":         "#0F1221",   # near-black — max contrast on white
        "text2":        "#374060",   # dark slate — readable on light bg
        "text3":        "#6B7494",   # medium — used for hints/placeholders
        "sidebar_w":    220,
    }
}
 