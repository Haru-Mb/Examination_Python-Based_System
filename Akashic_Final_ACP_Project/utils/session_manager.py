"""Session management"""
import secrets
import datetime
from models.database import get_connection
from config import SESSION_TIMEOUT_MINUTES

_current_session = {"user": None, "token": None}


def login_session(user: dict) -> str:
    token = secrets.token_urlsafe(32)
    expires = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?,?,?)",
            (user["id"], token, expires.isoformat())
        )
        conn.commit()
    finally:
        conn.close()
    _current_session["user"] = user
    _current_session["token"] = token
    return token


def set_session(user: dict) -> str:
    """Alias for login_session"""
    return login_session(user)


def logout_session():
    token = _current_session.get("token")
    if token:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
            conn.commit()
        finally:
            conn.close()
    _current_session["user"] = None
    _current_session["token"] = None


def clear_session():
    """Alias for logout_session"""
    logout_session()


def get_current_user() -> object:
    return _current_session.get("user")


def update_session_user(user: dict):
    _current_session["user"] = user
