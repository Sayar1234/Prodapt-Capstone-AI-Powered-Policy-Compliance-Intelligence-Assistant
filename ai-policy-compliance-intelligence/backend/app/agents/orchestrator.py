from hashlib import sha256
import logging
from typing import Any, Literal, TypedDict

from app.agents.tools import build_agent_tools
from app.database.redis import cache
from app.models.domain_models import Citation, ComplianceFinding, RiskLevel
from app.models.response_models import ComplianceCheckResponse
from app.security.guardrails import screen_user_text

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import END, START, StateGraph
except ModuleNotFoundError:
    END = "__end__"
    START = "__start__"
    StateGraph = None


class ComplianceGraphState(TypedDict, total=False):
    query: str
    top_k: int
    policy_type: str | None
    include_recommendations: bool
    is_allowed: bool
    guardrail_hits: list[str]
    citations: list[dict[str, Any]]
    risk_level: str
    risk_score: float
    risk_rationale: str
    recommendations: list[str]
    answer: str
    findings: list[dict[str, Any]]


class ComplianceOrchestrator:
    def __init__(self) -> None:
        self.tools = build_agent_tools()
        self.graph = self._build_graph()

    async def check(self, query: str, top_k: int = 6, policy_type: str | None = None, include_recommendations: bool = True) -> ComplianceCheckResponse:
        cache_key = self._cache_key(query, top_k, policy_type, include_recommendations)
        cached = await self._cache_get(cache_key)
        if cached:
            return ComplianceCheckResponse.model_validate(cached)

        state: ComplianceGraphState = {
            "query": query,
            "top_k": top_k,
            "policy_type": policy_type,
            "include_recommendations": include_recommendations,
        }
        result = await self._invoke_graph(state)
        response = self._response_from_state(result)
        await self._cache_set(cache_key, response.model_dump(mode="json"), ttl=300)
        return response

    @staticmethod
    async def _cache_get(key: str) -> object | None:
        try:
            return await cache.get(key)
        except Exception as exc:
            logger.warning("Compliance cache read failed; continuing without cache: %s", exc)
            return None

    @staticmethod
    async def _cache_set(key: str, value: object, ttl: int) -> None:
        try:
            await cache.set(key, value, ttl=ttl)
        except Exception as exc:
            logger.warning("Compliance cache write failed; continuing without cache: %s", exc)

    def _build_graph(self):
        if StateGraph is None:
            return None
        builder = StateGraph(ComplianceGraphState)
        builder.add_node("guardrails", self._guardrails_node)
        builder.add_node("blocked_response", self._blocked_response_node)
        builder.add_node("retrieve_evidence", self._retrieve_node)
        builder.add_node("assess_risk", self._risk_node)
        builder.add_node("recommend_actions", self._recommendation_node)
        builder.add_node("synthesize_answer", self._synthesis_node)

        builder.add_edge(START, "guardrails")
        builder.add_conditional_edges(
            "guardrails",
            self._route_after_guardrails,
            {"blocked": "blocked_response", "allowed": "retrieve_evidence"},
        )
        builder.add_edge("blocked_response", END)
        builder.add_edge("retrieve_evidence", "assess_risk")
        builder.add_edge("assess_risk", "recommend_actions")
        builder.add_edge("recommend_actions", "synthesize_answer")
        builder.add_edge("synthesize_answer", END)
        return builder.compile()

    async def _invoke_graph(self, state: ComplianceGraphState) -> ComplianceGraphState:
        if self.graph is not None:
            return await self.graph.ainvoke(state)

        current = self._guardrails_node(state)
        state.update(current)
        if self._route_after_guardrails(state) == "blocked":
            state.update(self._blocked_response_node(state))
            return state
        for node in (self._retrieve_node, self._risk_node, self._recommendation_node, self._synthesis_node):
            state.update(node(state))
        return state

    @staticmethod
    def _guardrails_node(state: ComplianceGraphState) -> ComplianceGraphState:
        ok, hits = screen_user_text(state["query"])
        return {"is_allowed": ok, "guardrail_hits": hits}

    @staticmethod
    def _route_after_guardrails(state: ComplianceGraphState) -> Literal["allowed", "blocked"]:
        return "allowed" if state.get("is_allowed") else "blocked"

    @staticmethod
    def _blocked_response_node(state: ComplianceGraphState) -> ComplianceGraphState:
        hits = state.get("guardrail_hits", [])
        return {
            "risk_level": RiskLevel.high.value,
            "citations": [],
            "findings": [],
            "recommendations": ["Rephrase the request as a policy compliance question."],
            "answer": f"Request blocked by safety guardrails: {', '.join(hits)}",
        }

    def _retrieve_node(self, state: ComplianceGraphState) -> ComplianceGraphState:
        citations = self.tools["retrieve_policy_evidence"].invoke(
            {
                "query": state["query"],
                "top_k": state.get("top_k", 6),
                "policy_type": state.get("policy_type"),
            }
        )
        return {"citations": citations}

    def _risk_node(self, state: ComplianceGraphState) -> ComplianceGraphState:
        risk = self.tools["assess_policy_risk"].invoke(
            {"query": state["query"], "citations": state.get("citations", [])}
        )
        return risk

    def _recommendation_node(self, state: ComplianceGraphState) -> ComplianceGraphState:
        recommendations = []
        if state.get("include_recommendations", True):
            recommendations = self.tools["recommend_compliance_actions"].invoke(
                {"risk_level": state.get("risk_level", RiskLevel.medium.value), "query": state["query"]}
            )
        return {"recommendations": recommendations}

    def _synthesis_node(self, state: ComplianceGraphState) -> ComplianceGraphState:
        synthesized = self.tools["synthesize_compliance_answer"].invoke(
            {
                "query": state["query"],
                "risk_level": state.get("risk_level", RiskLevel.medium.value),
                "citations": state.get("citations", []),
                "recommendations": state.get("recommendations", []),
            }
        )
        return synthesized

    @staticmethod
    def _response_from_state(state: ComplianceGraphState) -> ComplianceCheckResponse:
        return ComplianceCheckResponse(
            query=state["query"],
            answer=state.get("answer", ""),
            risk_level=RiskLevel(state.get("risk_level", RiskLevel.medium.value)),
            findings=[ComplianceFinding.model_validate(item) for item in state.get("findings", [])],
            citations=[Citation.model_validate(item) for item in state.get("citations", [])],
            recommendations=state.get("recommendations", []),
        )

    @staticmethod
    def _cache_key(query: str, top_k: int, policy_type: str | None, include_recommendations: bool) -> str:
        raw = f"{query}|{top_k}|{policy_type or ''}|{include_recommendations}"
        return f"compliance:{sha256(raw.encode('utf-8')).hexdigest()}"
