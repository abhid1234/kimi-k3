import tempfile
import unittest
from pathlib import Path

from app.storage import get_conn, ensure_schema, get_daily_spend, list_runs, write_run


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "runs.db"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_write_and_list_runs(self) -> None:
        run_id = write_run(
            goal="Test goal",
            constraints=None,
            context=None,
            tone="clear",
            status="success",
            model="x",
            latency_ms=12,
            cost_usd=0.1,
            response_json={"summary": "ok", "assumptions": [], "plan": [], "risks": [], "next_actions": [], "confidence": "high"},
            raw_output='{"summary":"ok"}',
            error=None,
            path=self.db_path,
        )
        self.assertIsInstance(run_id, int)
        rows = list_runs(limit=10, path=self.db_path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], run_id)
        self.assertEqual(rows[0]["status"], "success")

    def test_daily_spend(self) -> None:
        write_run(
            goal="Test goal 1",
            constraints=None,
            context=None,
            tone="clear",
            status="success",
            model="x",
            latency_ms=10,
            cost_usd=1.5,
            response_json={"summary": "ok", "assumptions": [], "plan": [], "risks": [], "next_actions": [], "confidence": "high"},
            raw_output='{"summary":"ok"}',
            error=None,
            path=self.db_path,
        )
        write_run(
            goal="Test goal 2",
            constraints=None,
            context=None,
            tone="clear",
            status="failed",
            model="x",
            latency_ms=10,
            cost_usd=0.7,
            response_json=None,
            raw_output=None,
            error="boom",
            path=self.db_path,
        )

        with get_conn(self.db_path) as conn:
            ensure_schema(conn)
            spend = get_daily_spend(conn)
        self.assertAlmostEqual(spend, 2.2, places=6)

    def test_schema_ensure(self) -> None:
        with get_conn(self.db_path) as conn:
            ensure_schema(conn)
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='runs'").fetchone()
            self.assertIsNotNone(rows)
            cols = [row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()]
            self.assertIn("cost_usd", cols)


if __name__ == "__main__":
    unittest.main()
