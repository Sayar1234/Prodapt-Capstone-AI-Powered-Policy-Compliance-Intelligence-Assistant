from app.evaluation.metrics import average_score, citation_coverage, groundedness_score, keyword_recall
from app.models.response_models import ComplianceCheckResponse


def evaluate_response(response: ComplianceCheckResponse, expected_terms: list[str] | None = None) -> dict[str, float]:
    return {
        "citation_coverage": citation_coverage(response.citations),
        "average_retrieval_score": average_score(response.citations),
        "keyword_recall": keyword_recall(response.answer, expected_terms or []),
        "citation_groundedness": groundedness_score(response.answer, response.citations),
    }


def passes_quality_gate(scores: dict[str, float]) -> bool:
    return (
        scores["citation_coverage"] >= (1 / 3)
        and scores["average_retrieval_score"] >= 0.0
        and scores["keyword_recall"] >= 0.5
        and scores["citation_groundedness"] >= 0.05
    )
