from app.models.domain_models import Citation
from app.retrieval.hybrid_search import hybrid_search


class RetrievalAgent:
    def search(self, query: str, top_k: int = 6, policy_type: str | None = None) -> list[Citation]:
        return hybrid_search(query=query, top_k=top_k, policy_type=policy_type)
