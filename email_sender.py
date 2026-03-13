import os
import smtplib
from email.message import EmailMessage
from typing import Optional


def _format_file_size(size_bytes: int) -> str:
    """Return a human-readable file size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def _build_email_body(
    filename: str,
    encryption_password: str,
    file_size_str: str,
) -> tuple[str, str]:
    """Build both plain-text and HTML versions of the email body.

    Returns (plain_text, html_text).
    """
    plain_text = (
        "🔒 Encrypted Image File\n\n"
        "Please find the encrypted image file attached.\n"
        "Use the provided password to decrypt it.\n\n"
        f"📁 File: {filename}\n"
        f"🔑 Encryption Password: {encryption_password}\n"
        f"📎 File Size: {file_size_str}\n\n"
        "📋 Instructions:\n"
        "1. Save the attached file\n"
        "2. Use the Image Encryption App to decrypt\n"
        "3. Enter the password provided above\n"
        "4. Your original image will be restored\n\n"
        "⚠️ Important:\n"
        "• Keep this password secure\n"
        "• Do not share via unsecured channels\n"
        "• The password is required for decryption\n\n"
        "This email was sent automatically by Image Encryption System."
    )

    html_text = f"""\
<html>
<body style="margin:0; padding:0; background-color:#1a1a2e; font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#1a1a2e; padding:30px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background-color:#16213e; border-radius:12px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.4);">
          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #0f3460, #533483); padding:28px 32px;">
              <h1 style="margin:0; color:#e9d44c; font-size:22px; font-weight:700;">
                🔒 Encrypted Image File
              </h1>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:28px 32px; color:#d4d4d8;">
              <p style="margin:0 0 20px; font-size:15px; line-height:1.6; color:#a1a1aa;">
                Please find the encrypted image file attached.<br>
                Use the provided password to decrypt it.
              </p>

              <!-- File Details Card -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background-color:#1a1a2e; border-radius:8px; margin-bottom:24px;">
                <tr>
                  <td style="padding:18px 20px;">
                    <p style="margin:0 0 10px; font-size:14px; color:#d4d4d8;">
                      📁 <strong>File:</strong> {filename}
                    </p>
                    <p style="margin:0 0 10px; font-size:14px; color:#d4d4d8;">
                      🔑 <strong>Encryption Password:</strong>
                      <span style="background-color:#0f3460; padding:3px 10px; border-radius:4px;
                                   font-family:monospace; color:#e9d44c; letter-spacing:0.5px;">
                        {encryption_password}
                      </span>
                    </p>
                    <p style="margin:0; font-size:14px; color:#d4d4d8;">
                      📎 <strong>File Size:</strong> {file_size_str}
                    </p>
                  </td>
                </tr>
              </table>

              <!-- Instructions -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background-color:#1a1a2e; border-radius:8px; margin-bottom:24px;">
                <tr>
                  <td style="padding:18px 20px;">
                    <p style="margin:0 0 12px; font-size:14px; font-weight:700; color:#e9d44c;">
                      📋 Instructions:
                    </p>
                    <p style="margin:0 0 6px; font-size:14px; color:#d4d4d8;">1. Save the attached file</p>
                    <p style="margin:0 0 6px; font-size:14px; color:#d4d4d8;">2. Use the Image Encryption App to decrypt</p>
                    <p style="margin:0 0 6px; font-size:14px; color:#d4d4d8;">3. Enter the password provided above</p>
                    <p style="margin:0;       font-size:14px; color:#d4d4d8;">4. Your original image will be restored</p>
                  </td>
                </tr>
              </table>

              <!-- Warning -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background-color:#1a1a2e; border-left:4px solid #e9d44c; border-radius:4px;">
                <tr>
                  <td style="padding:14px 18px;">
                    <p style="margin:0 0 8px; font-size:14px; font-weight:700; color:#e9d44c;">
                      ⚠️ Important:
                    </p>
                    <p style="margin:0 0 4px; font-size:13px; color:#a1a1aa;">• Keep this password secure</p>
                    <p style="margin:0 0 4px; font-size:13px; color:#a1a1aa;">• Do not share via unsecured channels</p>
                    <p style="margin:0;       font-size:13px; color:#a1a1aa;">• The password is required for decryption</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:18px 32px; border-top:1px solid #2a2a4a;">
              <p style="margin:0; font-size:12px; color:#6b7280; font-style:italic;">
                This email was sent automatically by Image Encryption System.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return plain_text, html_text


def send_email(
    sender_email: str,
    password: str,
    receiver_email: str,
    file_path: str,
    encryption_password: str = "",
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 465,
    subject: Optional[str] = None,
    body: Optional[str] = None,
) -> None:
    """
    Send an email with the given encrypted file attached using SMTP over SSL.

    The email includes a rich HTML body showing the file name, encryption
    password, file size, decryption instructions, and security warnings.

    Raises smtplib.SMTPException or OSError on network/authentication errors.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Attachment not found: {file_path}")

    filename = os.path.basename(file_path)
    file_size_str = _format_file_size(os.path.getsize(file_path))

    if subject is None:
        subject = "Encrypted Image File"

    # Build rich email body (both plain-text fallback and HTML)
    if body is None and encryption_password:
        plain_body, html_body = _build_email_body(filename, encryption_password, file_size_str)
    elif body is not None:
        plain_body = body
        html_body = None
    else:
        plain_body = (
            "This email contains an AES-encrypted image file.\n"
            "Use the shared secret key in your Secure Image Transfer application to decrypt it."
        )
        html_body = None

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(plain_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

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
