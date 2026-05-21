import unittest

from app.ingestion.pipeline import ingest_text
from app.retrieval.hybrid_search import hybrid_search
from tests.helpers import reset_local_store


class IngestionRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_local_store()

    def tearDown(self) -> None:
        reset_local_store()

    def test_ingest_and_search(self) -> None:
        result = ingest_text(
            title="Security Policy",
            text="Privileged access requires approval and multi factor authentication before use.",
            source="unit-test",
            policy_type="security",
        )
        self.assertEqual(result.chunks_created, 1)
        citations = hybrid_search("Does privileged access need approval?", top_k=3, policy_type="security")
        self.assertTrue(citations)
        self.assertEqual(citations[0].title, "Security Policy")


if __name__ == "__main__":
    unittest.main()
