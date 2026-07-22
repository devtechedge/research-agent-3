from email.message import EmailMessage
import smtplib

from .config import settings


def send_email(recipient: str, subject: str, body: str) -> None:
    if settings.simulation_mode:
        print(f"[simulation] Email queued to {recipient}: {subject}")
        return

    if not settings.email_user or not settings.email_app_password:
        raise RuntimeError("EMAIL_USER and EMAIL_APP_PASSWORD must be set for live email delivery")

    message = EmailMessage()
    message["From"] = settings.email_user
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.email_user, settings.email_app_password)
        server.send_message(message)
