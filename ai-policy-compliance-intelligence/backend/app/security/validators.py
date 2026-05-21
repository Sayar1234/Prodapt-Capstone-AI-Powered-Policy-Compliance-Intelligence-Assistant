from pathlib import Path

from app.core.config import get_settings
from app.core.constants import SUPPORTED_EXTENSIONS
from app.core.exceptions import ValidationAppError


def validate_upload(filename: str, size: int | None = None) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValidationAppError(f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}")
    if size is not None:
        max_bytes = get_settings().max_upload_mb * 1024 * 1024
        if size > max_bytes:
            raise ValidationAppError(f"File exceeds {get_settings().max_upload_mb} MB limit")


def sanitize_policy_type(policy_type: str | None) -> str:
    value = (policy_type or "general").strip().lower()
    return "".join(ch for ch in value if ch.isalnum() or ch in {"_", "-"}) or "general"
