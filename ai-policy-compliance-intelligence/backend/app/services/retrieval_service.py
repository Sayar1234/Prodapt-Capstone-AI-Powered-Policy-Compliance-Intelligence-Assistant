from app.agents.retrieval_agent import RetrievalAgent
from app.models.domain_models import Citation


class RetrievalService:
    def __init__(self) -> None:
        self.agent = RetrievalAgent()

    def search(self, query: str, top_k: int = 6, policy_type: str | None = None) -> list[Citation]:
        return self.agent.search(query, top_k, policy_type)
