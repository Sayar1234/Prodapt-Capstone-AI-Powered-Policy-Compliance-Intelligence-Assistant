import unittest

from app.ingestion.pipeline import ingest_text
from app.retrieval.hybrid_search import hybrid_search
from tests.helpers import reset_local_store


class PolicyTypeFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_local_store()

    def tearDown(self) -> None:
        reset_local_store()

    def test_search_falls_back_when_selected_policy_type_has_no_documents(self) -> None:
        ingest_text(
            title="Privacy Policy",
            text="Customer personal data requires privacy approval and encryption before vendor sharing.",
            source="unit-test",
            policy_type="privacy",
        )

        citations = hybrid_search(
            "Can customer personal data be shared without encryption?",
            top_k=3,
            policy_type="security",
        )

        self.assertTrue(citations)
        self.assertEqual(citations[0].title, "Privacy Policy")


if __name__ == "__main__":
    unittest.main()
