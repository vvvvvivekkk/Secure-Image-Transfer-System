from typing import Optional

from encryptor import decrypt_image as _core_decrypt_image


def decrypt_image(encrypted_file: str, key: bytes, output_path: Optional[str] = None) -> str:
    """
    Public decryption API.

    Delegates to the core decrypt function in `encryptor` to keep
    encryption/decryption logic centralized.
    """
    if output_path is None:
        if not encrypted_file.lower().endswith(".enc"):
            output_path = encrypted_file + ".dec"
        else:
            output_path = encrypted_file[:-4]  # strip ".enc"

    return _core_decrypt_image(encrypted_file, key, output_path)

