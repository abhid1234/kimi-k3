import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import date
from typing import Any


def default_db_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "runs.db"


@contextmanager
def get_conn(path: Path | str | None = None):
    db_path = Path(path) if path else default_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            goal TEXT NOT NULL,
            constraints TEXT,
            context TEXT,
            tone TEXT,
            status TEXT NOT NULL,
            model TEXT NOT NULL,
            latency_ms INTEGER NOT NULL,
            cost_usd REAL NOT NULL DEFAULT 0.0,
            response_json TEXT,
            raw_output TEXT,
            error TEXT
        )
        """
    )
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(runs)").fetchall()}
    if "cost_usd" not in existing:
        conn.execute("ALTER TABLE runs ADD COLUMN cost_usd REAL NOT NULL DEFAULT 0.0")
    conn.commit()


def write_run(
    goal: str,
    constraints: str | None,
    context: str | None,
    tone: str | None,
    status: str,
    model: str,
    latency_ms: int,
    cost_usd: float,
    response_json: dict[str, Any] | None,
    raw_output: str | None,
    error: str | None,
    path: Path | str | None = None,
) -> int:
    with get_conn(path) as conn:
        ensure_schema(conn)
        cur = conn.execute(
            """
            INSERT INTO runs (goal, constraints, context, tone, status, model, latency_ms, cost_usd, response_json, raw_output, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                goal,
                constraints,
                context,
                tone,
                status,
                model,
                latency_ms,
                cost_usd,
                json.dumps(response_json) if response_json is not None else None,
                raw_output,
                error,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_runs(limit: int = 20, path: Path | str | None = None) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    with get_conn(path) as conn:
        ensure_schema(conn)
        cur = conn.execute(
            """
            SELECT id, created_at, goal, status, model, latency_ms, error
            FROM runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in cur.fetchall()]


def get_daily_spend(conn: sqlite3.Connection, day: str | None = None) -> float:
    if day is None:
        day = date.today().isoformat()
    query = """
        SELECT COALESCE(SUM(cost_usd), 0.0) AS spend
        FROM runs
        WHERE status IN ('success', 'failed')
          AND date(created_at) = date(?)
    """
    row = conn.execute(query, (day,)).fetchone()
    return float(row["spend"] if row and row["spend"] is not None else 0.0)
