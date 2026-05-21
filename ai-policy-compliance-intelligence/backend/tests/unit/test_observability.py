import unittest

from app.observability.monitoring import metrics_response


class ObservabilityTests(unittest.TestCase):
    def test_metrics_response_returns_text(self) -> None:
        response = metrics_response()
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.media_type)


if __name__ == "__main__":
    unittest.main()
