import os

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


BLOCK_SIZE = AES.block_size
MAGIC = b"SITS1"
ALLOWED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".gif",
    ".tiff",
    ".webp",
}


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


def _normalize_image_extension(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image extension: {ext or '(none)'}")
    return ext


def _build_plaintext_payload(image_path: str, image_bytes: bytes) -> bytes:
    # Embed original extension in encrypted payload so decryption can restore it.
    ext = _normalize_image_extension(image_path)
    ext_bytes = ext.encode("ascii")
    if len(ext_bytes) > 255:
        raise ValueError("Image extension metadata is too long.")
    return MAGIC + bytes([len(ext_bytes)]) + ext_bytes + image_bytes


def _parse_plaintext_payload(plaintext: bytes) -> tuple[str | None, bytes]:
    # Backward-compatible parser: legacy files had only raw image bytes.
    if not plaintext.startswith(MAGIC):
        return None, plaintext

    header_index = len(MAGIC)
    if len(plaintext) <= header_index:
        raise ValueError("Corrupted encrypted payload: missing extension length.")

    ext_len = plaintext[header_index]
    ext_start = header_index + 1
    ext_end = ext_start + ext_len
    if ext_len == 0 or ext_end > len(plaintext):
        raise ValueError("Corrupted encrypted payload: invalid extension metadata.")

    ext_bytes = plaintext[ext_start:ext_end]
    try:
        ext = ext_bytes.decode("ascii").lower()
    except UnicodeDecodeError as exc:
        raise ValueError("Corrupted encrypted payload: invalid extension encoding.") from exc

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Corrupted encrypted payload: unsupported embedded extension.")

    return ext, plaintext[ext_end:]


def _enforce_output_extension(output_path: str, ext: str | None) -> str:
    if not ext:
        return output_path
    base, current_ext = os.path.splitext(output_path)
    if current_ext.lower() == ext.lower():
        return output_path
    return base + ext


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
        image_bytes = f.read()

    plaintext = _build_plaintext_payload(image_path, image_bytes)

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
    if len(ciphertext) == 0 or len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Encrypted file is corrupted: invalid ciphertext length.")

    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext = _pkcs7_unpad(padded_plaintext)
    except ValueError as exc:
        raise ValueError(
            "Decryption failed: incorrect key or corrupted encrypted file."
        ) from exc

    embedded_ext, image_bytes = _parse_plaintext_payload(plaintext)
    final_output_path = _enforce_output_extension(output_path, embedded_ext)

    with open(final_output_path, "wb") as f:
        f.write(image_bytes)

    return final_output_path

