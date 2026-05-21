from app.models.domain_models import Citation, ComplianceFinding, RiskLevel
from app.services.llm_service import build_llm_client


class ComplianceAgent:
    def __init__(self) -> None:
        self.llm = build_llm_client()

    def answer(self, query: str, risk_level: RiskLevel, citations: list[Citation], recommendations: list[str]) -> tuple[str, list[ComplianceFinding]]:
        if not citations:
            answer = "No matching policy evidence was found. Ingest policy documents before making a compliance decision."
            return answer, [
                ComplianceFinding(
                    control="Policy evidence",
                    status="insufficient_evidence",
                    risk_level=RiskLevel.medium,
                    evidence=[],
                    rationale="The knowledge base does not contain relevant policy chunks for this request.",
                    recommendation="Ingest the applicable policy, procedure, or regulatory document.",
                )
            ]

        status = "needs_review" if risk_level in {RiskLevel.medium, RiskLevel.high} else "likely_compliant"
        rationale = "Retrieved evidence was compared against the request using local semantic and lexical scoring."
        answer = self.llm.generate_compliance_answer(query, risk_level, citations, recommendations)
        if not answer:
            answer = self._local_answer(query, risk_level, status, rationale, citations, recommendations)
        finding = ComplianceFinding(
            control="Applicable policy requirements",
            status=status,
            risk_level=risk_level,
            evidence=citations[:3],
            rationale=rationale,
            recommendation=recommendations[0] if recommendations else "Document the decision and retain evidence.",
        )
        return answer, [finding]

    @staticmethod
    def _local_answer(
        query: str,
        risk_level: RiskLevel,
        status: str,
        rationale: str,
        citations: list[Citation],
        recommendations: list[str],
    ) -> str:
        evidence_sentences = []
        for citation in citations[:2]:
            evidence_sentences.append(f"{citation.title} says: {citation.excerpt}")
        recommendation_text = " ".join(recommendations[:2]) if recommendations else "Keep an audit trail for the decision."

        if risk_level == RiskLevel.high:
            decision = "This should not be approved without formal compliance review."
        elif risk_level == RiskLevel.medium:
            decision = "This can proceed only after the missing evidence or control requirements are clarified."
        else:
            decision = "This appears acceptable if the cited policy conditions are followed."

        return (
            f"{status.replace('_', ' ').title()}. {decision} "
            f"The request was: {query.strip()} "
            f"{' '.join(evidence_sentences)} "
            f"{rationale} Recommended next steps: {recommendation_text}"
        )
