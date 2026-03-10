import os
import imaplib
import email
from email.header import decode_header
from email.message import Message
from typing import List, Tuple


def _default_download_dir() -> str:
    # Keep downloads inside the project folder regardless of process cwd.
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")


def _build_mailbox_candidates(preferred_mailbox: str) -> list[str]:
    candidates: list[str] = []

    def add(name: str) -> None:
        normalized = name.strip()
        if normalized and normalized not in candidates:
            candidates.append(normalized)

    add(preferred_mailbox)
    add("INBOX")
    add("[Gmail]/All Mail")
    add("[Gmail]/Sent Mail")
    add("Sent")
    add("Sent Items")
    return candidates


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
    download_dir: str | None = None,
    max_messages: int = 100,
    timeout_seconds: int = 30,
) -> List[Tuple[str, str]]:
    """
    Connect to an IMAP server and download `.enc` attachments from the mailbox.

    Returns a list of tuples: (attachment_filename, saved_path).
    """
    resolved_download_dir = download_dir or _default_download_dir()
    os.makedirs(resolved_download_dir, exist_ok=True)

    # Use a bounded timeout so the GUI does not appear to hang indefinitely.
    try:
        mail = imaplib.IMAP4_SSL(imap_server, timeout=timeout_seconds)
    except TypeError:
        # Backward compatibility for Python builds without timeout parameter.
        mail = imaplib.IMAP4_SSL(imap_server)
    try:
        mail.login(user_email, password)
        attachments_info: List[Tuple[str, str]] = []

        seen_message_ids: set[bytes] = set()
        for candidate_mailbox in _build_mailbox_candidates(mailbox):
            status, _ = mail.select(candidate_mailbox)
            if status != "OK":
                continue

            status, data = mail.search(None, "ALL")
            if status != "OK" or not data or not data[0]:
                continue

            message_ids = data[0].split()
            if max_messages > 0:
                # Only scan newest messages to keep download checks responsive.
                message_ids = message_ids[-max_messages:]

            # Iterate newest-first so recent attachments are found quickly.
            for num in reversed(message_ids):
                if num in seen_message_ids:
                    continue
                seen_message_ids.add(num)

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
                    save_path = os.path.join(resolved_download_dir, safe_name)

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

