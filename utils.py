import logging
import os
from typing import Optional

from PIL import Image


LOG_FILE = "secure_image_transfer.log"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def is_valid_image(path: str) -> bool:
    """
    Validate that the file at `path` is a readable image using Pillow.

    This does not modify the file; it only attempts to load metadata.
    """
    if not os.path.isfile(path):
        return False
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def ensure_dir(path: str) -> None:
    """Create a directory if it does not already exist."""
    os.makedirs(path, exist_ok=True)


def resource_path(relative: str) -> str:
    """
    Resolve resource paths in a way that works for both source and PyInstaller.
    """
    try:
        base_path = os.sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative)

