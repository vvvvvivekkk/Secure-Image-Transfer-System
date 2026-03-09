import base64
import os
import hashlib


def generate_key() -> str:
    """
    Generate a fresh 256-bit key and return it as URL-safe base64.

    This representation is convenient for copy/paste and storage.
    """
    raw_key = os.urandom(32)
    return base64.urlsafe_b64encode(raw_key).decode("utf-8")


def hash_key(password: str) -> bytes:
    """
    Derive a 256-bit AES key from a user-provided password using SHA-256.

    Returned value is exactly 32 bytes suitable for AES-256.
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
    # Encode to bytes and hash
    return hashlib.sha256(password.encode("utf-8")).digest()

