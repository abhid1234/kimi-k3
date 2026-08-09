from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    goal: str = Field(..., min_length=10, max_length=2000)
    constraints: str | None = Field(default=None, max_length=1000)
    context: str | None = Field(default=None, max_length=2000)
    tone: Literal["clear", "concise", "executive"] = "clear"


class PlanStep(BaseModel):
    step: int
    action: str
    why: str
    risk: Literal["low", "medium", "high"] = "low"


class PlanResponse(BaseModel):
    summary: str
    assumptions: list[str]
    plan: list[PlanStep]
    risks: list[str]
    next_actions: list[str]
    confidence: Literal["low", "medium", "high"]


class RunResponse(BaseModel):
    id: int
    status: str
    data: PlanResponse | None = None
    raw_output: str | None = None
    model: str
    latency_ms: int
    cost_usd: float
    budget_cap_hit: bool = False
    daily_budget_usd: float | None = None
    daily_spend_usd: float | None = None
