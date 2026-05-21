from app.models.domain_models import Citation, DocumentChunk


def excerpt(text: str, limit: int = 360) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3].rstrip() + "..."


def citation_from_chunk(chunk: DocumentChunk, score: float) -> Citation:
    return Citation(
        document_id=chunk.document_id,
        chunk_id=chunk.id,
        title=chunk.title,
        source=chunk.source,
        excerpt=excerpt(chunk.text),
        score=round(float(score), 4),
    )
