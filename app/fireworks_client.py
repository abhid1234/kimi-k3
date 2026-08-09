from __future__ import annotations

import json
import os
import re
from typing import Any, List

import httpx

from .schemas import PlanResponse


FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORKS_TIMEOUT_SECONDS = 30.0


def _extract_json(text: str) -> str:
    # Fireworks responses sometimes wrap JSON in markdown fences or include comments.
    if not text:
        return text
    text = text.strip()
    fence_match = re.search(r"```json\s*(.*?)```", text, flags=re.S | re.I)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def _build_system_prompt() -> str:
    return """You are a deterministic planning engine.
Return ONLY a single JSON object with these exact keys:
- summary: short human summary
- assumptions: array of strings
- plan: array of objects {step:int, action:string, why:string, risk:string}
- risks: array of strings
- next_actions: array of strings
- confidence: one of [low, medium, high]

Do not include markdown, explanations, code, or any extra keys.

If the request is unsafe or conflicts with policy, set summary to 'Blocked', keep arrays empty, and set confidence to low.
""".strip()


def _build_user_prompt(goal: str, constraints: str | None, context: str | None, tone: str | None) -> str:
    c = constraints.strip() if constraints else "No extra constraints"
    ctx = context.strip() if context else "No additional context"
    tone_val = tone.strip() if tone else "clear"

    return f"""Goal: {goal}

Context: {ctx}
Constraints: {c}

Output style: {tone_val}.

Generate a practical, actionable plan that can be followed in order.
"""


async def generate_plan(
    goal: str,
    constraints: str | None = None,
    context: str | None = None,
    tone: str | None = None,
    timeout_s: float = 30.0,
) -> PlanResponse:
    api_key = os.environ.get("FIREWORKS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("FIREWORKS_API_KEY is not configured")

    model = os.environ.get("FIREWORKS_MODEL", "accounts/fireworks/models/llama-v3p3-70b-instruct").strip()
    temperature = float(os.environ.get("FIREWORKS_TEMPERATURE", "0.2"))
    max_tokens = int(os.environ.get("FIREWORKS_MAX_TOKENS", "1800"))

    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": _build_system_prompt()},
            {"role": "user", "content": _build_user_prompt(goal, constraints, context, tone)},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=timeout_s or FIREWORKS_TIMEOUT_SECONDS) as client:
        resp = await client.post(FIREWORKS_URL, headers=headers, json=payload)

    if resp.status_code >= 400:
        raise RuntimeError(f"Fireworks API error {resp.status_code}: {resp.text[:300]}")

    body = resp.json()
    choices: List[Any] = body.get("choices", [])
    if not choices:
        raise RuntimeError("No completion choices returned")

    raw = str(choices[0].get("message", {}).get("content", "")).strip()
    raw = _extract_json(raw)

    if not raw:
        raise RuntimeError("Empty completion from model")

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model output is not valid JSON: {exc}") from exc

    # Ensure strict shape and coerce keys.
    try:
        return PlanResponse.model_validate(parsed)
    except Exception as exc:
        raise RuntimeError(f"Model output schema mismatch: {exc}") from exc
