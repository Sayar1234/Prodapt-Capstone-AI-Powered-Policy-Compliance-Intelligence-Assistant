from app.models.domain_models import Citation
from app.retrieval.reranker import rerank
from app.retrieval.vector_search import vector_search
from app.utils.citation_utils import citation_from_chunk


def hybrid_search(query: str, top_k: int = 6, policy_type: str | None = None) -> list[Citation]:
    candidates = vector_search(query, max(top_k * 3, top_k), policy_type)
    return [citation_from_chunk(chunk, score) for chunk, score in rerank(query, candidates)[:top_k]]
