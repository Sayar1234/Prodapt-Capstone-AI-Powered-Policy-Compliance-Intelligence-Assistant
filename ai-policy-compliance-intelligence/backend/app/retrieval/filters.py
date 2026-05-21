from app.models.domain_models import DocumentChunk


def filter_chunks(chunks: list[DocumentChunk], policy_type: str | None = None) -> list[DocumentChunk]:
    if not policy_type:
        return chunks
    wanted = policy_type.lower()
    return [chunk for chunk in chunks if chunk.policy_type.lower() == wanted]
