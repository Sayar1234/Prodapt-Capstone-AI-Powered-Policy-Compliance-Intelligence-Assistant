import unittest

from app.agents.compliance_agent import ComplianceAgent
from app.agents.risk_agent import RiskAgent
from app.models.domain_models import Citation, RiskLevel


class RiskAndAnswerTests(unittest.TestCase):
    def test_sensitive_data_without_encryption_is_not_low_risk(self) -> None:
        citations = [
            Citation(
                document_id="d1",
                chunk_id="c1",
                title="Privacy Policy",
                source="unit",
                excerpt="Customer personal data requires encryption and privacy approval before vendor sharing.",
                score=0.9,
            )
        ]
        level, score, _ = RiskAgent().assess("Can personal data be shared with a vendor without encryption?", citations)
        self.assertIn(level, {RiskLevel.medium, RiskLevel.high})
        self.assertGreaterEqual(score, 0.42)

    def test_local_answer_is_readable_and_recommendation_based(self) -> None:
        citations = [
            Citation(
                document_id="d1",
                chunk_id="c1",
                title="Security Policy",
                source="unit",
                excerpt="Privileged access requires manager approval and MFA.",
                score=0.9,
            )
        ]
        answer, findings = ComplianceAgent().answer(
            "Can privileged access skip approval?",
            RiskLevel.high,
            citations,
            ["Escalate to compliance review before implementation."],
        )
        self.assertIn("This should not be approved", answer)
        self.assertIn("Security Policy says", answer)
        self.assertEqual(findings[0].risk_level, RiskLevel.high)


if __name__ == "__main__":
    unittest.main()
