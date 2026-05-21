from app.core.config import get_settings
from app.models.domain_models import DocumentChunk, PolicyDocument


def chunk_text(text: str, size: int | None = None, overlap: int | None = None) -> list[str]:
    settings = get_settings()
    size = size or settings.chunk_size
    overlap = overlap if overlap is not None else settings.chunk_overlap
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def build_chunks(document: PolicyDocument) -> list[DocumentChunk]:
    return [
        DocumentChunk(
            document_id=document.id,
            title=document.title,
            text=text,
            chunk_index=index,
            policy_type=document.policy_type,
            source=document.source,
            metadata=document.metadata,
        )
        for index, text in enumerate(chunk_text(document.text))
    ]
