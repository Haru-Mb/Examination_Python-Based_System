"""Email service - stub for development"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_ENABLED


def send_verification_email(to_email: str, username: str, token: str) -> bool:
    if not EMAIL_ENABLED:
        print(f"[EMAIL STUB] Verification email to {to_email}, token: {token}")
        return True
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Akashik — Verify Your Account"
        msg["From"] = EMAIL_USER
        msg["To"] = to_email
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
          <h2 style="color:#4F8EF7">Akashik</h2>
          <p>Hi <b>{username}</b>, welcome to Akashik!</p>
          <p>Your verification code is:</p>
          <div style="background:#1E2330;color:#4F8EF7;padding:16px 24px;border-radius:8px;
                      font-size:24px;letter-spacing:4px;text-align:center">{token[:8].upper()}</div>
          <p style="color:#666;font-size:13px;margin-top:24px">
            If you didn't create this account, you can ignore this email.
          </p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def send_welcome_email(to_email: str, username: str) -> bool:
    if not EMAIL_ENABLED:
        print(f"[EMAIL STUB] Welcome email to {to_email}")
        return True
    return True
