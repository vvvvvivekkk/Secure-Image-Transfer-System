import os
from typing import Dict


ENV_FILE = ".env"
EMAIL_SETTING_KEYS = (
    "SENDER_EMAIL",
    "SENDER_APP_PASSWORD",
    "RECEIVER_EMAIL",
)


def _parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        return None

    # Allow optional single or double quotes in values.
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
        value = value[1:-1]

    return key, value


def load_env(path: str = ENV_FILE) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not os.path.isfile(path):
        return values

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parsed = _parse_env_line(line)
            if parsed is None:
                continue
            key, value = parsed
            values[key] = value
    return values


def load_email_settings(path: str = ENV_FILE) -> Dict[str, str]:
    env_values = load_env(path)
    return {key: env_values.get(key, "") for key in EMAIL_SETTING_KEYS}


def save_email_settings(settings: Dict[str, str], path: str = ENV_FILE) -> None:
    merged = load_env(path)
    for key in EMAIL_SETTING_KEYS:
        merged[key] = settings.get(key, "").strip()

    lines = [
        "# Email settings for Secure Image Transfer System",
        f"SENDER_EMAIL={merged.get('SENDER_EMAIL', '')}",
        f"SENDER_APP_PASSWORD={merged.get('SENDER_APP_PASSWORD', '')}",
        f"RECEIVER_EMAIL={merged.get('RECEIVER_EMAIL', '')}",
        "",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
