# Kimi K3 Project Facts (Evidence-backed)

## Product
- Name: Kimi K3 Planner
- Problem: Turn a goal into a structured, risk-aware execution plan in one shot
- Target user: Founders, operators, solo builders who want fast, ordered action plans
- Core UX: goal/constraints/context composer + plan rail + risk strip + compare lane + run history

## Technical stack
- Runtime: FastAPI
- Frontend: single static `static/index.html`
- Model: Fireworks hosted model API
- Persistence: SQLite (`data/runs.db` by default, `/tmp/kimi-k3-runs.db` on Vercel)

## Current verified behavior
- `GET /api/health` returns `{ "status": "ok" }`
- `POST /api/plan` validates request and writes a run record
- Budget guard enforces a daily spend cap before calling model
- Malformed model output (invalid JSON, long risk text, missing fields) is sanitized before schema validation
- Unknown tone values are mapped to supported tones (`clear`, `concise`, `executive`)

## Evidence references
- Backend tests: `tests/test_main_budget.py`, `tests/test_storage.py`, `tests/test_fireworks_client.py`, `tests/test_schemas.py`, `tests/test_frontend.py`
- UI screenshots: `docs/screenshots/*.png`

## Known constraints / risks
- Fireworks API account state can still block all calls if the account is suspended or over quota
- External model availability can change model alias names; default remains configurable via `FIREWORKS_MODEL`
