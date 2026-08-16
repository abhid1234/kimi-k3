from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pydantic import ValidationError

from .fireworks_client import generate_plan
from .schemas import PlanRequest, RunResponse
from .storage import get_conn, ensure_schema, list_runs, write_run, get_daily_spend


ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
DATA_DIR = Path(os.environ.get("KIMI_DB_PATH", str(ROOT / "data" / "runs.db"))).parent


class AppConfig(BaseModel):
    model: str
    daily_budget_usd: float
    estimated_cost_usd: float
    hard_cap_enabled: bool
    runtime_version: str

app = FastAPI(title="K3 Planner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        ensure_schema(conn)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _get_runtime_config() -> dict[str, float | str | bool]:
    daily_budget_usd = float(os.environ.get("KIMI_DAILY_BUDGET_USD", "5.0"))
    estimated_cost_usd = float(os.environ.get("KIMI_ESTIMATED_COST_USD", "0.02"))
    model = os.environ.get("FIREWORKS_MODEL", "accounts/fireworks/models/gpt-oss-120b").strip() or "accounts/fireworks/models/gpt-oss-120b"
    return {
        "model": model,
        "daily_budget_usd": daily_budget_usd,
        "estimated_cost_usd": estimated_cost_usd,
        "hard_cap_enabled": daily_budget_usd > 0,
    }


@app.get("/api/config", response_model=AppConfig)
def config() -> AppConfig:
    cfg = _get_runtime_config()
    return AppConfig(
        model=cfg["model"],
        daily_budget_usd=cfg["daily_budget_usd"],
        estimated_cost_usd=cfg["estimated_cost_usd"],
        hard_cap_enabled=cfg["hard_cap_enabled"],
        runtime_version="kimi-k3-v1",
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/api/plan", response_model=RunResponse)
async def create_plan(payload: PlanRequest) -> RunResponse:
    cfg = _get_runtime_config()
    model = cfg["model"]
    daily_budget_usd = float(cfg["daily_budget_usd"])
    estimated_cost_usd = float(cfg["estimated_cost_usd"])
    if daily_budget_usd <= 0:
        raise HTTPException(status_code=500, detail="KIMI_DAILY_BUDGET_USD must be greater than 0")
    if estimated_cost_usd <= 0:
        raise HTTPException(status_code=500, detail="KIMI_ESTIMATED_COST_USD must be greater than 0")

    today = datetime.now(timezone.utc).date().isoformat()
    started_at = time.perf_counter()

    with get_conn() as conn:
        ensure_schema(conn)
        spent_today = get_daily_spend(conn, day=today)

    projected_spend = spent_today + estimated_cost_usd
    if projected_spend > daily_budget_usd:
        raise HTTPException(
            status_code=429,
            detail=(
                "Daily testing cap reached. Due to high demand, the daily quota is full for today. "
                f"Try again tomorrow. Budget: ${daily_budget_usd:.2f}/day."
            ),
        )

    try:
        parsed = await generate_plan(
            goal=payload.goal,
            constraints=payload.constraints,
            context=payload.context,
            tone=payload.tone,
            timeout_s=40.0,
        )
    except HTTPException:
        raise
    except ValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid model response. Please try again.",
        ) from exc
    except Exception as exc:
        error_message = str(exc)
        if "Model output schema mismatch" in error_message:
            user_message = (
                "Model output could not be parsed into the expected schema. "
                "Please retry with the same request."
            )
        elif "Fireworks API error" in error_message:
            user_message = error_message
        else:
            user_message = error_message

        latency_ms = int((time.perf_counter() - started_at) * 1000)
        run_id = write_run(
            goal=payload.goal,
            constraints=payload.constraints,
            context=payload.context,
            tone=payload.tone,
            status="failed",
            model=model,
            latency_ms=latency_ms,
            cost_usd=estimated_cost_usd,
            response_json=None,
            raw_output=None,
            error=user_message,
        )
        raise HTTPException(status_code=502, detail=user_message) from exc

    latency_ms = int((time.perf_counter() - started_at) * 1000)
    run_id = write_run(
        goal=payload.goal,
        constraints=payload.constraints,
        context=payload.context,
        tone=payload.tone,
        status="success",
        model=model,
        latency_ms=latency_ms,
        cost_usd=estimated_cost_usd,
        response_json=parsed.model_dump(),
        raw_output=parsed.model_dump_json(),
        error=None,
    )
    return RunResponse(
        id=run_id,
        status="success",
        data=parsed,
        raw_output=parsed.model_dump_json(),
        model=model,
        latency_ms=latency_ms,
        cost_usd=estimated_cost_usd,
        budget_cap_hit=projected_spend >= daily_budget_usd,
        daily_budget_usd=daily_budget_usd,
        daily_spend_usd=round(projected_spend, 4),
    )


@app.get("/api/runs")
def runs(limit: int = 20) -> list[dict]:
    if limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be greater than 0")
    if limit > 100:
        limit = 100
    return list_runs(limit=limit)
