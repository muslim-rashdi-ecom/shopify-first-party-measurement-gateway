import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from measurement_gateway import EventValidationError, MeasurementGateway


FIXTURE = Path(__file__).parents[1] / "fixtures" / "purchase.json"


class MeasurementGatewayTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.gateway = MeasurementGateway()

    def test_accepts_consent_authorized_purchase(self):
        decision = self.gateway.ingest(self.payload)
        self.assertEqual(decision.status, "accepted")
        self.assertEqual(decision.channels, ("ga4", "meta", "tiktok", "google_ads"))
        self.assertEqual(decision.payloads["meta"]["data"][0]["event_id"], "demo-order-1001")

    def test_duplicate_event_is_not_forwarded_twice(self):
        self.gateway.ingest(self.payload)
        decision = self.gateway.ingest(self.payload)
        self.assertEqual(decision.status, "duplicate")
        self.assertEqual(decision.channels, ())

    def test_advertising_channels_require_consent(self):
        payload = {**self.payload, "event_id": "analytics-only-1", "consent": {"analytics_storage": True}}
        decision = self.gateway.ingest(payload)
        self.assertEqual(decision.status, "accepted")
        self.assertEqual(decision.channels, ("ga4",))

    def test_all_denied_is_blocked(self):
        payload = {**self.payload, "event_id": "blocked-1", "consent": {}}
        decision = self.gateway.ingest(payload)
        self.assertEqual(decision.status, "blocked")
        self.assertEqual(decision.payloads, None)

    def test_raw_pii_is_rejected_at_boundary(self):
        payload = {**self.payload, "properties": {"email": "customer@example.com"}}
        with self.assertRaises(EventValidationError):
            self.gateway.ingest(payload)


if __name__ == "__main__":
    unittest.main()
