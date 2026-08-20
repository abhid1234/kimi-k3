import os
import unittest
from fastapi.testclient import TestClient

from app import main


class ConfigEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(main.app)

    def tearDown(self) -> None:
        self.client.close()
        os.environ.pop("KIMI_DAILY_BUDGET_USD", None)
        os.environ.pop("KIMI_ESTIMATED_COST_USD", None)
        os.environ.pop("FIREWORKS_MODEL", None)

    def test_defaults(self) -> None:
        os.environ.pop("KIMI_DAILY_BUDGET_USD", None)
        os.environ.pop("KIMI_ESTIMATED_COST_USD", None)
        os.environ.pop("FIREWORKS_MODEL", None)

        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["model"], "accounts/fireworks/models/kimi-k3")
        self.assertGreater(data["daily_budget_usd"], 0)
        self.assertIn("runtime_version", data)

    def test_respects_runtime_env(self) -> None:
        os.environ["KIMI_DAILY_BUDGET_USD"] = "12.5"
        os.environ["KIMI_ESTIMATED_COST_USD"] = "0.05"
        os.environ["FIREWORKS_MODEL"] = "accounts/fireworks/models/test-model"

        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["model"], "accounts/fireworks/models/test-model")
        self.assertEqual(data["daily_budget_usd"], 12.5)
        self.assertEqual(data["estimated_cost_usd"], 0.05)
        self.assertTrue(data["hard_cap_enabled"])


if __name__ == "__main__":
    unittest.main()
