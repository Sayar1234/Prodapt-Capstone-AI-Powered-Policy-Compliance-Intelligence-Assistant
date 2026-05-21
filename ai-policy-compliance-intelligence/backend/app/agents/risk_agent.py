from app.core.config import get_settings
from app.core.constants import HIGH_RISK_TERMS, MEDIUM_RISK_TERMS, RISK_KEYWORDS
from app.models.domain_models import Citation, RiskLevel


class RiskAgent:
    def assess(self, scenario: str, citations: list[Citation]) -> tuple[RiskLevel, float, str]:
        text = f"{scenario} {' '.join(c.excerpt for c in citations)}".lower()
        category_hits = sum(1 for words in RISK_KEYWORDS.values() for word in words if word in text)
        high_hits = sum(1 for term in HIGH_RISK_TERMS if term in text)
        medium_hits = sum(1 for term in MEDIUM_RISK_TERMS if term in text)
        negation_hits = sum(1 for term in ["without", "bypass", "avoid", "skip", "unapproved"] if term in text)

        evidence_boost = min(0.12, len(citations) * 0.03)
        score = min(
            1.0,
            (category_hits * 0.08)
            + (high_hits * 0.18)
            + (medium_hits * 0.08)
            + (negation_hits * 0.12)
            + evidence_boost,
        )
        settings = get_settings()
        if score >= settings.risk_threshold_high:
            level = RiskLevel.high
        elif score >= settings.risk_threshold_medium:
            level = RiskLevel.medium
        else:
            level = RiskLevel.low
        rationale = (
            f"Risk score {score:.2f} from {category_hits} policy-category signal(s), "
            f"{high_hits} high-risk signal(s), {medium_hits} medium-risk signal(s), "
            f"and {len(citations)} retrieved evidence citation(s)."
        )
        return level, score, rationale
