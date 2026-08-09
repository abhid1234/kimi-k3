import os
import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app import main
from app.schemas import PlanResponse
from app.storage import get_conn, write_run


@contextmanager
def _conn_context(path: Path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class MainBudgetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "runs.db"
        self.conn_patcher = patch("app.main.get_conn", new=lambda path=None: _conn_context(self.db_path))
        self.conn_patcher.start()
        self.client = TestClient(main.app)
        os.environ["KIMI_DAILY_BUDGET_USD"] = "0.05"
        os.environ["KIMI_ESTIMATED_COST_USD"] = "0.03"

    def tearDown(self) -> None:
        self.conn_patcher.stop()
        self.client.close()
        self.tmpdir.cleanup()
        os.environ.pop("KIMI_DAILY_BUDGET_USD", None)
        os.environ.pop("KIMI_ESTIMATED_COST_USD", None)

    def test_blocks_when_daily_budget_exceeded(self) -> None:
        write_run(
            goal="Seed historical run",
            constraints=None,
            context=None,
            tone="clear",
            status="success",
            model="x",
            latency_ms=1,
            cost_usd=0.03,
            response_json={"summary": "seed", "assumptions": [], "plan": [], "risks": [], "next_actions": [], "confidence": "low"},
            raw_output='{"summary":"seed"}',
            error=None,
            path=self.db_path,
        )

        response = self.client.post(
            "/api/plan",
            json={
                "goal": "Build a concrete and testable plan for an AI side project",
                "constraints": "No external dependencies",
                "context": "solo founder",
                "tone": "clear",
            },
        )
        self.assertEqual(response.status_code, 429)
        self.assertIn("Daily testing cap reached", response.json()["detail"])

    @patch("app.main.generate_plan")
    def test_success_includes_budget_metadata(self, generate_plan_mock: AsyncMock) -> None:
        generate_plan_mock.return_value = PlanResponse(
            summary="Go to first milestone",
            assumptions=["Assume coding capacity"],
            plan=[{"step": 1, "action": "Start", "why": "init", "risk": "low"}],
            risks=["none"],
            next_actions=["Ship"],
            confidence="medium",
        )
        response = self.client.post(
            "/api/plan",
            json={
                "goal": "Build a concrete and testable plan for an AI side project",
                "constraints": "No external dependencies",
                "context": "solo founder",
                "tone": "clear",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["daily_budget_usd"], 0.05)
        self.assertAlmostEqual(data["cost_usd"], 0.03)
        self.assertTrue(data["daily_spend_usd"] >= data["cost_usd"])


if __name__ == "__main__":
    unittest.main()
