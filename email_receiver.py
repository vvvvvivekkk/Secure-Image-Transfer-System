import os
import imaplib
import email
from email.header import decode_header
from email.message import Message
from typing import List, Tuple


def _decode_mime_filename(filename: str | None) -> str:
    if not filename:
        return ""

    parts = decode_header(filename)
    decoded: list[str] = []
    for value, encoding in parts:
        if isinstance(value, bytes):
            decoded.append(value.decode(encoding or "utf-8", errors="replace"))
        else:
            decoded.append(value)
    return "".join(decoded)


def _extract_rfc822_bytes(msg_data: list[object]) -> bytes | None:
    for item in msg_data:
        if isinstance(item, tuple) and len(item) >= 2 and isinstance(item[1], (bytes, bytearray)):
            return bytes(item[1])
    return None


def _get_candidate_filename(part: Message) -> str:
    # get_filename handles Content-Disposition filename and RFC2231 values.
    filename = _decode_mime_filename(part.get_filename())
    if filename:
        return filename

    # Some senders only set the Content-Type 'name' parameter.
    name = part.get_param("name", header="Content-Type")
    if isinstance(name, str):
        return _decode_mime_filename(name)

    return ""


def download_encrypted_files(
    user_email: str,
    password: str,
    imap_server: str = "imap.gmail.com",
    mailbox: str = "INBOX",
    download_dir: str = "downloads",
) -> List[Tuple[str, str]]:
    """
    Connect to an IMAP server and download `.enc` attachments from the mailbox.

    Returns a list of tuples: (attachment_filename, saved_path).
    """
    os.makedirs(download_dir, exist_ok=True)

    mail = imaplib.IMAP4_SSL(imap_server)
    try:
        mail.login(user_email, password)
        status, _ = mail.select(mailbox)
        if status != "OK":
            raise RuntimeError(f"Unable to select mailbox {mailbox}.")

        status, data = mail.search(None, "ALL")
        if status != "OK":
            raise RuntimeError("Failed to search mailbox.")

        attachments_info: List[Tuple[str, str]] = []

        for num in data[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            raw_email = _extract_rfc822_bytes(msg_data)
            if raw_email is None:
                continue

            msg = email.message_from_bytes(raw_email)

            for part in msg.walk():
                if part.is_multipart():
                    continue

                filename = _get_candidate_filename(part)
                if not filename or not filename.lower().endswith(".enc"):
                    continue

                payload = part.get_payload(decode=True)
                if payload is None:
                    continue

                safe_name = os.path.basename(filename)
                save_path = os.path.join(download_dir, safe_name)

                # Avoid overwriting existing files by appending a counter.
                base, ext = os.path.splitext(save_path)
                counter = 1
                while os.path.exists(save_path):
                    save_path = f"{base}_{counter}{ext}"
                    counter += 1

                with open(save_path, "wb") as f:
                    f.write(payload)

                attachments_info.append((safe_name, save_path))

        return attachments_info
    finally:
        try:
            mail.logout()
        except Exception:
            pass

