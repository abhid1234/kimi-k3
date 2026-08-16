# Kimi K3 Project Facts (evidence-backed)

Every claim here is checkable against the code or a test. **Nothing in the launch copy
should assert anything that isn't on this page.** Updated 2026-08-16 after the launch
polish pass.

## Product
- Name: Kimi K3 Planner
- Problem: turn a goal into a structured, risk-aware execution plan in one shot
- Target user: founders, operators, solo builders who want fast, ordered action plans
- Core UX: goal/constraints/context composer → Action Plan Pack → risk-elevation strip →
  step rail → assumptions/risks/next actions; plus compare lane and run history

## Technical stack
- Runtime: FastAPI, deployed on Vercel via Mangum (`api/index.py`)
- Frontend: single static `static/index.html`, no build step
- Model: **`gpt-oss-120b`, hosted on Fireworks** (`FIREWORKS_MODEL`, configurable)
- Persistence: SQLite (`data/runs.db` by default, `/tmp/kimi-k3-runs.db` on Vercel)

> ⚠️ **Naming, stated plainly.** The project is called Kimi K3; it does **not** run
> Moonshot's Kimi K3 model. If asked, the answer is "it's a harness, not a model — it runs
> gpt-oss-120b on Fireworks." Do not let launch copy imply otherwise.

## Verified behavior
- `GET /api/health` returns `{ "status": "ok" }`
- `GET /api/config` returns model, daily budget, estimated per-run cost, cap state
- `POST /api/plan` validates the request and writes a run record
- Budget guard enforces the daily spend cap **before** calling the model; on the cap it
  returns HTTP 429 with a user-facing message
- Malformed model output (invalid JSON, long risk text, missing fields) is sanitized
  before schema validation
- Unknown tone values map to `clear` / `concise` / `executive`; risk and confidence
  values off-enum normalize to `low` / `medium` / `high`
- `?demo=plan` and `?demo=compare` render bundled sample data through the real render
  path with **zero API calls**

## Numbers safe to quote
- **35** automated tests pass (`pytest tests/ -q`)
- Daily cap: **$5.00**, at an estimated **$0.02** per run (~250 runs/day)
- Compare mode generates **3** strategies: *current constraints*, *speed-first*,
  *risk-minimized* — **not** "clear vs concise vs executive", which is the tone control
- Plan strength scores out of **100**, across five weighted components: depth 20,
  section coverage 30, specificity 15, risk literacy 15, stated confidence 20
- The bundled sample plan scores **93**

## The launch story (accurate version)
The pre-launch pass found four real bugs, all in the surfaces around the model:
1. Plan strength saturated at five steps — effectively every plan scored 100/100, and
   compare mode produced tied winners so the "highest score" badge was meaningless
2. A `display: flex` rule overrode the `hidden` attribute, leaving copy/share/raw
   controls live on empty, loading and error states — and copying a *stale* plan after a
   failure that followed a success
3. The runtime chip rendered the cap as `5.00/day` with no currency unit
4. "First 3 actions" reset share mode to `single`, so those share links reopened wrong

## Evidence references
- Tests: `tests/test_main_budget.py`, `test_storage.py`, `test_fireworks_client.py`,
  `test_schemas.py`, `test_frontend.py`
- Screenshots: `docs/screenshots/12-hero-premium-desktop.png`,
  `13-action-plan-pack.png`, `14-hero-premium-mobile.png`
- Polish pass: PR `abhid1234/kimi-k3#1`

## Known constraints / risks
- Fireworks account state can block all calls if suspended or over quota
- Model alias names can change upstream; default stays configurable via `FIREWORKS_MODEL`
- SQLite on Vercel lives at `/tmp`, which is ephemeral — **run history does not survive a
  cold start in production.** Don't claim durable history in launch copy
- The repo is currently **private**; any public repo link in launch copy will 404 until
  that changes
- No CI is configured in this repo — there are no automated checks on push

## Not verified
- The live smoke script has not been run against `https://kimi-k3-ashy.vercel.app` by
  anyone yet. It is the first blocking item in `LAUNCH_DAY_RUNBOOK.md`
