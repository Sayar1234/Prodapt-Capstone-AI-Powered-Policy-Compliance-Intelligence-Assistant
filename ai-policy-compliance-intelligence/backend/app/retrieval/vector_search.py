from app.database.mongodb import store
from app.database.weaviate import vector_index
from app.models.domain_models import DocumentChunk
from app.retrieval.filters import filter_chunks


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(left * right for left, right in zip(a, b))
    left_norm = sum(left * left for left in a) ** 0.5
    right_norm = sum(right * right for right in b) ** 0.5
    denom = left_norm * right_norm
    return 0.0 if denom == 0 else dot / denom


def vector_search(query: str, top_k: int, policy_type: str | None = None) -> list[tuple[DocumentChunk, float]]:
    if hasattr(vector_index, "search"):
        results = vector_index.search(query, top_k, policy_type)
        if results or not policy_type:
            return results
        return vector_index.search(query, top_k, None)

    chunks = filter_chunks(store.list_chunks(), policy_type)
    if not chunks and policy_type:
        chunks = store.list_chunks()
    query_embedding = vector_index.embed(query)
    scored = [(chunk, cosine(query_embedding, vector_index.embed(chunk.text))) for chunk in chunks]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]
