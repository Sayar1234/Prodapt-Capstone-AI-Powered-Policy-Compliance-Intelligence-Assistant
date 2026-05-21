from app.utils.document_utils import normalize_text


def clean_document_text(text: str) -> str:
    return normalize_text(text)
