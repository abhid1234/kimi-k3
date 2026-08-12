from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, field_validator


class PlanRequest(BaseModel):
    goal: str = Field(..., min_length=10, max_length=2000)
    constraints: str | None = Field(default=None, max_length=1000)
    context: str | None = Field(default=None, max_length=2000)
    tone: str = "clear"

    @field_validator("tone")
    @classmethod
    def normalize_tone(cls, value: str) -> str:
        if not isinstance(value, str):
            return "clear"

        normalized = value.strip().lower()
        tone_aliases = {
            "concise": "concise",
            "short": "concise",
            "brief": "concise",
            "executive": "executive",
            "business": "executive",
            "confident": "clear",
            "confidently": "clear",
            "professional": "executive",
            "formal": "executive",
            "friendly": "clear",
            "chatty": "clear",
            "simple": "clear",
            "clear": "clear",
        }
        return tone_aliases.get(normalized, "clear")


class PlanStep(BaseModel):
    step: int
    action: str
    why: str
    risk: str = "low"

    @field_validator("risk")
    @classmethod
    def normalize_risk(cls, value: str) -> str:
        if not isinstance(value, str):
            return "low"
        lowered = value.strip().lower()
        if lowered in {"low", "medium", "high"}:
            return lowered
        if any(token in lowered for token in {"high", "severe", "critical", "major", "catastrophic"}):
            return "high"
        if any(token in lowered for token in {"medium", "moderate", "elevated", "significant"}):
            return "medium"
        return "low"


class PlanResponse(BaseModel):
    summary: str
    assumptions: list[str] = []
    plan: list[PlanStep]
    risks: list[str] = []
    next_actions: list[str] = []
    confidence: str | None = "low"

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value: str) -> str:
        if not isinstance(value, str):
            return "low"
        lowered = value.strip().lower()
        if lowered in {"low", "medium", "high"}:
            return lowered
        if any(token in lowered for token in {"high", "severe", "critical", "major", "catastrophic"}):
            return "high"
        if any(token in lowered for token in {"medium", "moderate", "elevated", "significant"}):
            return "medium"
        return "low"

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip() or ""

    @field_validator("assumptions", mode="before")
    @classmethod
    def normalize_assumptions(cls, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]

    @field_validator("risks", mode="before")
    @classmethod
    def normalize_risks(cls, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]

    @field_validator("next_actions", mode="before")
    @classmethod
    def normalize_next_actions(cls, value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]


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
