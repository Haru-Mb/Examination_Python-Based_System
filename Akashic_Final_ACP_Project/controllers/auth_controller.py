"""
Auth controller — login, register, session management
"""
from models.user_model import (
    get_user_by_login, create_user,
    username_exists, email_exists, srcode_exists, update_last_login
)
from utils.session_manager import set_session, clear_session
from utils.validator import validate_email, validate_password


def login_user(identifier: str, password: str) -> dict:
    user = get_user_by_login(identifier, password)
    if not user:
        return {"ok": False, "error": "Invalid credentials. Please try again."}
    update_last_login(user["id"])
    set_session(user)
    return {"ok": True, "user": user}


def register_user(username: str, email: str, sr_code: str,
                  password: str, role: str) -> dict:
    # Validate
    if username_exists(username):
        return {"ok": False, "error": "Username already taken."}
    if email_exists(email):
        return {"ok": False, "error": "Email already registered."}
    if srcode_exists(sr_code):
        return {"ok": False, "error": "SR Code / Employee ID already used."}
    if not validate_email(email):
        return {"ok": False, "error": "Invalid email format."}

    pw_check = validate_password(password)
    if not pw_check["ok"]:
        return {"ok": False, "error": pw_check["error"]}

    result = create_user(username, email, sr_code, password, role)
    return result


def logout_user():
    clear_session()
