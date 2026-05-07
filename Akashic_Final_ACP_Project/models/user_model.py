"""User model"""
import hashlib
import secrets
from models.database import get_connection


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{h}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, h = stored.split(":", 1)
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == h
    except Exception:
        return False


def create_user(username, email, sr_code, password, role) -> dict:
    conn = get_connection()
    try:
        token = secrets.token_urlsafe(32)
        conn.execute(
            """INSERT INTO users (username,email,sr_code,password_hash,role,verification_token,is_verified)
               VALUES (?,?,?,?,?,?,?)""",
            (username, email, sr_code, hash_password(password), role, token, 1)
        )
        conn.commit()
        return {"ok": True, "token": token}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def get_user_by_login(identifier, password) -> object:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE username=? OR email=?",
            (identifier, identifier)
        ).fetchone()
        if row and verify_password(password, row["password_hash"]):
            return dict(row)
        return None
    finally:
        conn.close()


def get_user_by_id(uid) -> object:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_profile(uid, nickname=None, bio=None, photo=None):
    conn = get_connection()
    try:
        if nickname is not None:
            conn.execute("UPDATE users SET nickname=? WHERE id=?", (nickname, uid))
        if bio is not None:
            conn.execute("UPDATE users SET bio=? WHERE id=?", (bio, uid))
        if photo is not None:
            conn.execute("UPDATE users SET profile_photo=? WHERE id=?", (photo, uid))
        conn.commit()
    finally:
        conn.close()


def verify_user(token):
    conn = get_connection()
    try:
        row = conn.execute("SELECT id FROM users WHERE verification_token=?", (token,)).fetchone()
        if row:
            conn.execute("UPDATE users SET is_verified=1, verification_token=NULL WHERE id=?", (row["id"],))
            conn.commit()
            return True
        return False
    finally:
        conn.close()


def username_exists(username):
    conn = get_connection()
    try:
        return conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone() is not None
    finally:
        conn.close()


def email_exists(email):
    conn = get_connection()
    try:
        return conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone() is not None
    finally:
        conn.close()


def srcode_exists(sr_code):
    conn = get_connection()
    try:
        return conn.execute("SELECT 1 FROM users WHERE sr_code=?", (sr_code,)).fetchone() is not None
    finally:
        conn.close()


def update_last_login(uid):
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET last_login=CURRENT_TIMESTAMP WHERE id=?", (uid,))
        conn.commit()
    finally:
        conn.close()
