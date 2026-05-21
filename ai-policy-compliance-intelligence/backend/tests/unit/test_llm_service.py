import unittest
from unittest.mock import MagicMock, patch

from app.models.domain_models import Citation, RiskLevel
from app.services.llm_service import OpenRouterClient


class OpenRouterClientTests(unittest.TestCase):
    def test_openrouter_returns_content(self) -> None:
        client = OpenRouterClient()
        client.api_key = "test-key"
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Use approval evidence."}}]}
        mock_response.raise_for_status.return_value = None

        mock_http_client = MagicMock()
        mock_http_client.__enter__.return_value.post.return_value = mock_response
        mock_http_client.__exit__.return_value = None

        with patch("app.services.llm_service.httpx.Client", return_value=mock_http_client):
            answer = client.generate_compliance_answer(
                "Can we proceed?",
                RiskLevel.low,
                [Citation(document_id="d", chunk_id="c", title="Policy", source="test", excerpt="Approval required.", score=1.0)],
                ["Document approval."],
            )

        self.assertEqual(answer, "Use approval evidence.")

    def test_missing_key_falls_back_to_none(self) -> None:
        client = OpenRouterClient()
        client.api_key = None
        self.assertIsNone(client.generate_compliance_answer("q", RiskLevel.low, [], []))


if __name__ == "__main__":
    unittest.main()
