from app.models.domain_models import Citation

try:
    from deepeval.metrics import BaseMetric
    from deepeval.test_case import LLMTestCase
except ModuleNotFoundError:
    BaseMetric = object
    LLMTestCase = object


def citation_coverage(citations: list[Citation]) -> float:
    return 0.0 if not citations else min(1.0, len(citations) / 3)


def average_score(citations: list[Citation]) -> float:
    return 0.0 if not citations else sum(c.score for c in citations) / len(citations)


def keyword_recall(text: str, expected_terms: list[str]) -> float:
    if not expected_terms:
        return 1.0
    lowered = text.lower()
    hits = sum(1 for term in expected_terms if term.lower() in lowered)
    return hits / len(expected_terms)


def groundedness_score(answer: str, citations: list[Citation]) -> float:
    if not answer or not citations:
        return 0.0
    answer_terms = {term.strip(".,:;()[]{}").lower() for term in answer.split() if len(term) > 3}
    evidence_terms = {
        term.strip(".,:;()[]{}").lower()
        for citation in citations
        for term in citation.excerpt.split()
        if len(term) > 3
    }
    if not answer_terms:
        return 0.0
    return len(answer_terms & evidence_terms) / len(answer_terms)


class ComplianceKeywordRecallMetric(BaseMetric):
    def __init__(self, expected_terms: list[str], threshold: float = 0.6) -> None:
        self.expected_terms = expected_terms
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""
        self.error = None

    def measure(self, test_case: LLMTestCase) -> float:
        output = getattr(test_case, "actual_output", "") or ""
        self.score = keyword_recall(output, self.expected_terms)
        self.success = self.score >= self.threshold
        self.reason = f"Matched {self.score:.0%} of expected compliance terms."
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self) -> str:
        return "Compliance Keyword Recall"


class CitationGroundednessMetric(BaseMetric):
    def __init__(self, threshold: float = 0.15) -> None:
        self.threshold = threshold
        self.score = 0.0
        self.success = False
        self.reason = ""
        self.error = None

    def measure(self, test_case: LLMTestCase) -> float:
        output = getattr(test_case, "actual_output", "") or ""
        context = getattr(test_case, "retrieval_context", None) or []
        citations = [
            Citation(document_id="", chunk_id=str(index), title="", source="", excerpt=item, score=1.0)
            for index, item in enumerate(context)
        ]
        self.score = groundedness_score(output, citations)
        self.success = self.score >= self.threshold
        self.reason = f"{self.score:.0%} of answer terms were supported by retrieved context."
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self) -> str:
        return "Citation Groundedness"
