"""Input validation utilities"""
import re


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email.strip()))


def validate_password(password: str):
    if len(password) < 8:
        return {"ok": False, "error": "Password must be at least 8 characters."}
    if not re.search(r"[A-Z]", password):
        return {"ok": False, "error": "Password must contain an uppercase letter."}
    if not re.search(r"[0-9]", password):
        return {"ok": False, "error": "Password must contain a number."}
    return {"ok": True, "error": ""}


def validate_sr_code(sr_code: str) -> bool:
    # Accept formats like 2021-12345 or just numeric
    return bool(re.match(r"^[\w\-]{5,20}$", sr_code.strip()))


def validate_username(username: str) -> tuple:
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 30:
        return False, "Username must be at most 30 characters."
    if not re.match(r"^[a-zA-Z0-9_\.]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and dots."
    return {"ok": True, "error": ""}
