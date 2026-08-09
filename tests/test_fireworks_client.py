import json
import os
import unittest
from unittest.mock import patch

from app.fireworks_client import generate_plan


class DummyResp:
    def __init__(self, status_code: int, text: str, payload: dict) -> None:
        self.status_code = status_code
        self.text = text
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class DummyClient:
    def __init__(self, *, response_payload: dict) -> None:
        self._payload = response_payload
        self.post_calls = []

    async def __aenter__(self) -> "DummyClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        return None

    async def post(self, url, headers=None, json=None):  # noqa: A002
        self.post_calls.append((url, headers, json))
        return DummyResp(200, "ok", self._payload)


class FireworksClientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        os.environ["FIREWORKS_API_KEY"] = "test-key"

    @patch("app.fireworks_client.httpx.AsyncClient", autospec=True)
    async def test_generate_plan_happy_path(self, mock_client):  # type: ignore[override]
        payload = {
            "summary": "Do it in 3 steps.",
            "assumptions": ["Assumption A"],
            "plan": [
                {"step": 1, "action": "Define scope", "why": "focus", "risk": "low"}
            ],
            "risks": ["Risk A"],
            "next_actions": ["Start now"],
            "confidence": "high",
        }
        instance = DummyClient(
            response_payload={"choices": [{"message": {"content": json.dumps(payload)}}]}
        )
        mock_client.return_value = instance

        result = await generate_plan("Build a product plan", constraints="low budget", context="solo", tone="clear")
        self.assertEqual(result.summary, "Do it in 3 steps.")
        self.assertEqual(result.plan[0].step, 1)

    @patch("app.fireworks_client.httpx.AsyncClient", autospec=True)
    async def test_generate_plan_accepts_markdown_fenced_json(self, mock_client):  # type: ignore[override]
        raw = """```json
{"summary":"Do it in 3 steps.","assumptions":["A"],"plan":[{"step":1,"action":"Define scope","why":"focus","risk":"low"}],"risks":["R"],"next_actions":["Start"],"confidence":"high"}
```"""
        instance = DummyClient(response_payload={"choices": [{"message": {"content": raw}}]})
        mock_client.return_value = instance

        result = await generate_plan("Build a product plan", constraints="low budget", context="solo", tone="clear")
        self.assertEqual(result.summary, "Do it in 3 steps.")

    @patch("app.fireworks_client.httpx.AsyncClient", autospec=True)
    async def test_generate_plan_normalizes_risk_and_confidence(self, mock_client):  # type: ignore[override]
        payload = {
            "summary": "Launch in 14 days.",
            "assumptions": ["Mature MVP mindset"],
            "plan": [
                {"step": 1, "action": "Publish landing", "why": "early signal", "risk": "Landing page may get low CTR"},
                {"step": 2, "action": "Run onboarding", "why": "activation", "risk": "High chance of user churn"},
            ],
            "risks": ["risk text"],
            "next_actions": ["Ship"],
            "confidence": "critical",
        }
        instance = DummyClient(response_payload={"choices": [{"message": {"content": json.dumps(payload)}}]})
        mock_client.return_value = instance

        result = await generate_plan("Build a 14-day launch plan", constraints="none", context="solo founder", tone="clear")
        self.assertEqual(result.plan[0].risk, "low")
        self.assertEqual(result.plan[1].risk, "high")
        self.assertEqual(result.confidence, "low")


if __name__ == "__main__":
    unittest.main()
