import os
import smtplib
from email.message import EmailMessage
from typing import Optional


def send_email(
    sender_email: str,
    password: str,
    receiver_email: str,
    file_path: str,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 465,
    subject: Optional[str] = None,
    body: Optional[str] = None,
) -> None:
    """
    Send an email with the given encrypted file attached using SMTP over SSL.

    Raises smtplib.SMTPException or OSError on network/authentication errors.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Attachment not found: {file_path}")

    if subject is None:
        subject = "Secure Encrypted Image"
    if body is None:
        body = (
            "This email contains an AES-encrypted image file.\n"
            "Use the shared secret key in your Secure Image Transfer application to decrypt it."
        )

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        data = f.read()
    msg.add_attachment(
        data,
        maintype="application",
        subtype="octet-stream",
        filename=filename,
    )

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, password)
        server.send_message(msg)

