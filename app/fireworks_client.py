from __future__ import annotations

import json
import os
import re
from typing import Any, List

import httpx

from .schemas import PlanResponse


FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
FIREWORKS_TIMEOUT_SECONDS = 30.0

_EXTERNAL_SERVICE_HINTS = {
    "openai",
    "anthropic",
    "google",
    "aws",
    "azure",
    "gcp",
    "supabase",
    "firebase",
    "stripe",
    "twilio",
    "sendgrid",
    "github",
    "slack",
    "n8n",
    "zapier",
    "notion",
    "airtable",
    "figma",
    "huggingface",
    "grok",
    "llama",
    "chatgpt",
    "claude",
    "perplexity",
}


def _is_built_in_only(constraints: str | None) -> bool:
    if not constraints:
        return False
    normalized = constraints.lower()
    return "built-in" in normalized or "builtin" in normalized or "internal api" in normalized


def _clean_service_mentions(text: str) -> tuple[str, int]:
    cleaned = text
    hits = 0
    for term in sorted(_EXTERNAL_SERVICE_HINTS):
        pattern = re.compile(rf"\b{re.escape(term)}\b", flags=re.I)
        if pattern.search(cleaned):
            hits += 1
            replacement = "internal API" if term not in {"llama", "chatgpt", "gpt", "grok"} else "internal model"
            cleaned = pattern.sub(replacement, cleaned)
    return cleaned, hits


def _enforce_constraints(parsed: dict[str, Any], constraints: str | None) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(parsed, dict):
        return parsed, []

    warnings: list[str] = []

    if _is_built_in_only(constraints):
        safe_prefix = "Use only built-in platform capabilities and existing system inputs."

        risks = parsed.get("risks")
        if isinstance(risks, list):
            for idx, risk in enumerate(risks):
                if isinstance(risk, str):
                    cleaned, hits = _clean_service_mentions(risk)
                    if hits:
                        warnings.append(f"risk[{idx}] contained {hits} external reference(s)")
                    risks[idx] = cleaned

        next_actions = parsed.get("next_actions")
        if isinstance(next_actions, list):
            for idx, action in enumerate(next_actions):
                if isinstance(action, str):
                    cleaned, hits = _clean_service_mentions(action)
                    if hits:
                        warnings.append(f"next_actions[{idx}] contained {hits} external reference(s)")
                    next_actions[idx] = cleaned

        plan = parsed.get("plan")
        if isinstance(plan, list):
            for step in plan:
                if not isinstance(step, dict):
                    continue
                for field in ("action", "why"):
                    value = step.get(field)
                    if isinstance(value, str):
                        cleaned, hits = _clean_service_mentions(value)
                        if hits:
                            warnings.append(f"plan[{step.get('step', '?')}].{field} contained {hits} external reference(s)")
                        step[field] = cleaned

        assumptions = parsed.get("assumptions")
        if isinstance(assumptions, list):
            for idx, assumption in enumerate(assumptions):
                if isinstance(assumption, str):
                    cleaned, hits = _clean_service_mentions(assumption)
                    if hits:
                        warnings.append(f"assumptions[{idx}] contained {hits} external reference(s)")
                    assumptions[idx] = cleaned
            parsed["assumptions"] = assumptions

        parsed["risks"] = risks if isinstance(risks, list) else parsed.get("risks", [])
        parsed["next_actions"] = next_actions if isinstance(next_actions, list) else parsed.get("next_actions", [])
        parsed["summary"] = f"{safe_prefix} {str(parsed.get('summary', '')).strip()}"
        if warnings and isinstance(parsed.get("risks"), list):
            parsed["risks"].append("Adjusted to avoid external service references per constraints.")

    return parsed, warnings


def _normalize_level(value: Any, *, default: str = "low") -> str:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"low", "medium", "high"}:
            return lowered
        if any(token in lowered for token in {"high", "severe", "critical", "major", "catastrophic"}):
            return "high"
        if any(token in lowered for token in {"medium", "moderate", "elevated", "significant"}):
            return "medium"
    return default


def _sanitize_list_field(value: Any, *, limit: int | None = None) -> list[str]:
    if not isinstance(value, list):
        return []

    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        normalized = item.strip()
        if normalized:
            result.append(normalized)

    if limit is not None and len(result) > limit:
        return result[:limit]
    return result


def _sanitize_plan_steps(plan: Any, *, max_steps: int = 12) -> list[dict[str, Any]]:
    if not isinstance(plan, list):
        return []

    sanitized: list[dict[str, Any]] = []
    valid_idx = 0
    for idx, step in enumerate(plan):
        if not isinstance(step, dict):
            continue
        valid_idx += 1

        action = step.get("action", f"Execute next action for step {idx + 1}")
        why = step.get("why", "Proceed with this step.")
        sequence_no = valid_idx

        risk = step.get("risk", "low")
        if isinstance(risk, str):
            risk = _normalize_level(risk, default="low")
        else:
            risk = "low"

        sanitized.append(
            {
                "step": sequence_no,
                "action": str(action).strip() or f"Execute next action for step {sequence_no}",
                "why": str(why).strip() or "Proceed with this step.",
                "risk": risk,
            }
        )

    if not sanitized:
        sanitized = [
            {
                "step": 1,
                "action": "Start with a small next action and validate progress.",
                "why": "Create a concrete first signal.",
                "risk": "low",
            }
        ]

    return sanitized[:max_steps]


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
 - plan: array of objects {step:int, action:string, why:string, risk:"low"|"medium"|"high"}
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

    model = os.environ.get("FIREWORKS_MODEL", "accounts/fireworks/models/gpt-oss-120b").strip()
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

    # Normalize output before strict shape validation.
    if isinstance(parsed, dict):
        if isinstance(parsed.get("confidence"), str):
            parsed["confidence"] = _normalize_level(parsed.get("confidence"), default="low")

        plan = parsed.get("plan")
        parsed["assumptions"] = _sanitize_list_field(parsed.get("assumptions"), limit=12)
        parsed["risks"] = _sanitize_list_field(parsed.get("risks"), limit=12)
        parsed["next_actions"] = _sanitize_list_field(parsed.get("next_actions"), limit=6)
        parsed["summary"] = str(parsed.get("summary", "Execution plan ready.")).strip() or "Execution plan ready."
        parsed["plan"] = _sanitize_plan_steps(plan)

        parsed, _ = _enforce_constraints(parsed, constraints)

    try:
        return PlanResponse.model_validate(parsed)
    except Exception as exc:
        raise RuntimeError(f"Model output schema mismatch: {exc}") from exc
