import smtplib
from email.message import EmailMessage

from flask import current_app


def send_email(to, subject, body):
    cfg = current_app.config
    if not cfg["MAIL_USERNAME"] or not cfg["MAIL_PASSWORD"]:
        if current_app.debug:
            current_app.logger.warning(
                "Mail not configured. Email would have been sent to %s:\n%s", to, body
            )
            return
        raise RuntimeError("Mail is not configured")

    msg = EmailMessage()
    msg["From"] = cfg["MAIL_USERNAME"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    if cfg["MAIL_PORT"] == 465:
        server = smtplib.SMTP_SSL(cfg["MAIL_SERVER"], 465, timeout=15)
    else:
        server = smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=15)
        server.starttls()

    with server:
        server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
        server.send_message(msg)
