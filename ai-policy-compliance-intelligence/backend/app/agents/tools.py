from typing import Any

from pydantic import BaseModel, Field

from app.agents.compliance_agent import ComplianceAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.risk_agent import RiskAgent
from app.models.domain_models import Citation, RiskLevel

try:
    from langchain_core.tools import StructuredTool
except ModuleNotFoundError:
    StructuredTool = None


class RetrievalToolInput(BaseModel):
    query: str
    top_k: int = Field(default=6, ge=1, le=20)
    policy_type: str | None = None


class RiskToolInput(BaseModel):
    query: str
    citations: list[dict[str, Any]] = Field(default_factory=list)


class RecommendationToolInput(BaseModel):
    risk_level: str
    query: str


class ComplianceSynthesisToolInput(BaseModel):
    query: str
    risk_level: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class LocalStructuredTool:
    def __init__(self, func):
        self.func = func

    def invoke(self, tool_input: dict[str, Any]) -> Any:
        return self.func(**tool_input)


def _structured_tool(func, name: str, description: str, args_schema: type[BaseModel]):
    if StructuredTool is None:
        return LocalStructuredTool(func)
    return StructuredTool.from_function(
        func=func,
        name=name,
        description=description,
        args_schema=args_schema,
    )


def build_agent_tools() -> dict[str, Any]:
    retrieval_agent = RetrievalAgent()
    risk_agent = RiskAgent()
    recommendation_agent = RecommendationAgent()
    compliance_agent = ComplianceAgent()

    def retrieve_policy_evidence(query: str, top_k: int = 6, policy_type: str | None = None) -> list[dict[str, Any]]:
        """Retrieve cited policy evidence relevant to a compliance query."""
        return [
            citation.model_dump(mode="json")
            for citation in retrieval_agent.search(query=query, top_k=top_k, policy_type=policy_type)
        ]

    def assess_policy_risk(query: str, citations: list[dict[str, Any]]) -> dict[str, Any]:
        """Assess compliance risk from the user query and retrieved policy citations."""
        parsed = [Citation.model_validate(citation) for citation in citations]
        risk_level, score, rationale = risk_agent.assess(query, parsed)
        return {"risk_level": risk_level.value, "risk_score": score, "risk_rationale": rationale}

    def recommend_compliance_actions(risk_level: str, query: str) -> list[str]:
        """Generate recommended compliance actions based on risk level."""
        return recommendation_agent.recommend(RiskLevel(risk_level), query)

    def synthesize_compliance_answer(
        query: str,
        risk_level: str,
        citations: list[dict[str, Any]],
        recommendations: list[str],
    ) -> dict[str, Any]:
        """Generate the final compliance answer and structured findings."""
        parsed = [Citation.model_validate(citation) for citation in citations]
        answer, findings = compliance_agent.answer(query, RiskLevel(risk_level), parsed, recommendations)
        return {
            "answer": answer,
            "findings": [finding.model_dump(mode="json") for finding in findings],
        }

    return {
        "retrieve_policy_evidence": _structured_tool(
            retrieve_policy_evidence,
            "retrieve_policy_evidence",
            "Retrieve cited policy evidence relevant to a compliance query.",
            RetrievalToolInput,
        ),
        "assess_policy_risk": _structured_tool(
            assess_policy_risk,
            "assess_policy_risk",
            "Assess compliance risk from the query and retrieved policy citations.",
            RiskToolInput,
        ),
        "recommend_compliance_actions": _structured_tool(
            recommend_compliance_actions,
            "recommend_compliance_actions",
            "Recommend compliance next steps based on risk level.",
            RecommendationToolInput,
        ),
        "synthesize_compliance_answer": _structured_tool(
            synthesize_compliance_answer,
            "synthesize_compliance_answer",
            "Synthesize a final compliance answer and structured findings.",
            ComplianceSynthesisToolInput,
        ),
    }
