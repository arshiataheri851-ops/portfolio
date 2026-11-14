"""Environment-configured SMTP delivery for SignalDesk."""
import os
import smtplib
from email.message import EmailMessage
from uuid import uuid4


def send_email(recipient: str, subject: str, body: str) -> str:
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("SMTP_FROM")
    if not host or not sender:
        raise RuntimeError("Outbound email is not configured; set SMTP_HOST and SMTP_FROM")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message["Message-ID"] = f"<{uuid4().hex}@{sender.split('@')[-1]}>"
    message.set_content(body)
    timeout = float(os.getenv("SMTP_TIMEOUT_SECONDS", "15"))
    try:
        client_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with client_class(host, port, timeout=timeout) as client:
            if not use_ssl:
                client.ehlo()
                client.starttls()
                client.ehlo()
            if username:
                client.login(username, password)
            client.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise RuntimeError("SMTP delivery failed") from exc
    return message["Message-ID"]
