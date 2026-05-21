import re
from pathlib import Path


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def safe_filename(name: str) -> str:
    stem = Path(name).stem.strip() or "document"
    suffix = Path(name).suffix.lower()
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)[:120]
    return f"{safe}{suffix}"
