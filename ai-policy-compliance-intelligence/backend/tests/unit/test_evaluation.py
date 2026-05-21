import unittest

from app.evaluation.evaluators import evaluate_response, passes_quality_gate
from app.evaluation.metrics import (
    CitationGroundednessMetric,
    ComplianceKeywordRecallMetric,
    average_score,
    citation_coverage,
    groundedness_score,
    keyword_recall,
)
from app.models.domain_models import Citation, RiskLevel
from app.models.response_models import ComplianceCheckResponse


class DummyTestCase:
    def __init__(self, actual_output: str, retrieval_context: list[str] | None = None) -> None:
        self.actual_output = actual_output
        self.retrieval_context = retrieval_context or []


class EvaluationMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.citations = [
            Citation(document_id="d1", chunk_id="c1", title="Policy", source="test", excerpt="Encryption requires approval.", score=0.9),
            Citation(document_id="d1", chunk_id="c2", title="Policy", source="test", excerpt="Vendors require privacy review.", score=0.6),
        ]

    def test_basic_scores(self) -> None:
        self.assertAlmostEqual(citation_coverage(self.citations), 2 / 3)
        self.assertAlmostEqual(average_score(self.citations), 0.75)
        self.assertEqual(keyword_recall("Approval and encryption are required", ["approval", "encryption"]), 1.0)
        self.assertGreater(groundedness_score("Encryption requires approval", self.citations), 0.1)

    def test_evaluate_response_quality_gate(self) -> None:
        response = ComplianceCheckResponse(
            query="Can we share data?",
            answer="Encryption and approval are required.",
            risk_level=RiskLevel.low,
            citations=self.citations,
            findings=[],
            recommendations=[],
        )
        scores = evaluate_response(response, ["encryption", "approval"])
        self.assertTrue(passes_quality_gate(scores))

    def test_deepeval_compatible_keyword_metric(self) -> None:
        metric = ComplianceKeywordRecallMetric(["approval", "encryption"])
        score = metric.measure(DummyTestCase("Approval requires encryption."))
        self.assertEqual(score, 1.0)
        self.assertTrue(metric.is_successful())

    def test_deepeval_compatible_groundedness_metric(self) -> None:
        metric = CitationGroundednessMetric(threshold=0.1)
        score = metric.measure(DummyTestCase("Approval requires encryption.", ["Encryption requires approval."]))
        self.assertGreaterEqual(score, 0.1)
        self.assertTrue(metric.is_successful())


if __name__ == "__main__":
    unittest.main()
