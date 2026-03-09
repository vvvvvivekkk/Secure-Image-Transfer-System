import os
from typing import Tuple

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


BLOCK_SIZE = AES.block_size


def _pkcs7_pad(data: bytes) -> bytes:
    """Apply PKCS7 padding to data."""
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len


def _pkcs7_unpad(data: bytes) -> bytes:
    """Remove PKCS7 padding from data."""
    if not data:
        raise ValueError("Invalid padding: empty data.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding length.")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Invalid padding bytes.")
    return data[:-pad_len]


def encrypt_image(image_path: str, key: bytes) -> str:
    """
    Encrypt an image file using AES-256-CBC.

    The function:
    - reads the raw image file bytes (no transformation to preserve quality),
    - encrypts them with a fresh IV,
    - stores IV + ciphertext in a `.enc` file next to the original.

    Returns the path to the encrypted file.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as f:
        plaintext = f.read()

    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = _pkcs7_pad(plaintext)
    ciphertext = cipher.encrypt(padded)

    enc_path = image_path + ".enc"
    with open(enc_path, "wb") as f:
        # Store IV + ciphertext
        f.write(iv + ciphertext)

    return enc_path


def decrypt_image(encrypted_file: str, key: bytes, output_path: str) -> str:
    """
    Decrypt an encrypted `.enc` file produced by `encrypt_image`.

    The function:
    - reads IV + ciphertext from the file,
    - decrypts and unpads,
    - writes raw bytes to `output_path`.

    Returns the path to the decrypted image.
    """
    if not os.path.isfile(encrypted_file):
        raise FileNotFoundError(f"Encrypted file not found: {encrypted_file}")

    with open(encrypted_file, "rb") as f:
        data = f.read()

    if len(data) <= BLOCK_SIZE:
        raise ValueError("Encrypted file too short to contain IV and data.")

    iv = data[:BLOCK_SIZE]
    ciphertext = data[BLOCK_SIZE:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = cipher.decrypt(ciphertext)
    plaintext = _pkcs7_unpad(padded_plaintext)

    with open(output_path, "wb") as f:
        f.write(plaintext)

    return output_path

