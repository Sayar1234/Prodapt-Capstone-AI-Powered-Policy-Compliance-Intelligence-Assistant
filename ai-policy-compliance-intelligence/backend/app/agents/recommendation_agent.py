from app.models.domain_models import RiskLevel


class RecommendationAgent:
    def recommend(self, risk_level: RiskLevel, query: str) -> list[str]:
        base = [
            "Map the request to an explicit policy control owner.",
            "Attach evidence from the current policy set before approval.",
        ]
        if risk_level == RiskLevel.high:
            return [
                "Escalate to compliance/legal review before implementation.",
                "Create a mitigation plan with due dates and accountable owners.",
                "Require executive sign-off for residual risk acceptance.",
            ] + base
        if risk_level == RiskLevel.medium:
            return [
                "Request clarifying evidence for ambiguous policy obligations.",
                "Add compensating controls and monitor them in the next review cycle.",
            ] + base
        return ["Proceed with standard approval workflow and keep an audit trail."] + base
