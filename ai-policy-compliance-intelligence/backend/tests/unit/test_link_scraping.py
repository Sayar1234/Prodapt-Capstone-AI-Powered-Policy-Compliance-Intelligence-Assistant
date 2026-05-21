import unittest
from unittest.mock import patch

from app.ingestion.pipeline import enrich_with_link_evidence
from app.utils.link_utils import extract_links


class LinkScrapingTests(unittest.TestCase):
    def test_extract_links_deduplicates_and_limits(self) -> None:
        text = "Read https://example.com/policy and https://example.com/policy. Also see https://example.org/a."
        self.assertEqual(extract_links(text, limit=1), ["https://example.com/policy"])

    def test_enrich_with_link_evidence_appends_successful_scrapes(self) -> None:
        with patch("app.ingestion.pipeline.ScrapingAgent") as agent_class:
            agent_class.return_value.scrape_many.return_value = [
                {
                    "url": "https://example.com/policy",
                    "title": "External Policy",
                    "text": "External vendors require encryption and privacy approval.",
                    "status": "ok",
                }
            ]
            enriched, scraped = enrich_with_link_evidence("See https://example.com/policy for details.")

        self.assertIn("Linked Evidence", enriched)
        self.assertIn("External vendors require encryption", enriched)
        self.assertEqual(scraped[0]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
