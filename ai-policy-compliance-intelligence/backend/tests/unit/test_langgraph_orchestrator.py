import unittest

from app.agents.orchestrator import ComplianceOrchestrator, StateGraph
from app.agents.tools import build_agent_tools
from app.ingestion.pipeline import ingest_text
from tests.helpers import reset_local_store


class LangGraphOrchestratorTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        reset_local_store()

    def tearDown(self) -> None:
        reset_local_store()

    def test_agent_tools_are_invokable(self) -> None:
        tools = build_agent_tools()
        self.assertIn("retrieve_policy_evidence", tools)
        self.assertTrue(hasattr(tools["retrieve_policy_evidence"], "invoke"))

    async def test_orchestrator_runs_graph_workflow(self) -> None:
        ingest_text(
            title="Access Policy",
            text="Privileged access requires manager approval and multi factor authentication.",
            source="unit-test",
            policy_type="security",
        )
        orchestrator = ComplianceOrchestrator()
        response = await orchestrator.check(
            "Does privileged access require approval?",
            top_k=3,
            policy_type="security",
        )
        self.assertTrue(response.citations)
        self.assertIn(response.risk_level.value, {"low", "medium", "high"})

    def test_langgraph_dependency_detected_when_installed(self) -> None:
        if StateGraph is None:
            self.skipTest("langgraph is not installed in this environment")
        orchestrator = ComplianceOrchestrator()
        self.assertIsNotNone(orchestrator.graph)


if __name__ == "__main__":
    unittest.main()
