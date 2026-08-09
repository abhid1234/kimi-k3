# Kimi K3 Planner

Kimi K3 is a lightweight planning service that turns a goal into an ordered,
actionable plan using the Fireworks API, with a simple FastAPI UI and persistent
run history in SQLite.

## UI

The playground UI (`static/index.html`, no build step) is a single-page composer +
output workspace: goal/constraints/context/tone composer with sample prompts,
a risk-annotated route-rail plan view, 3-variant compare mode, run history with
one-click reuse, and explicit loading/empty/error/budget states. Screenshots in
[`docs/screenshots/`](docs/screenshots/):

| | |
|---|---|
| `01-hero-composer-empty.png` | Hero, composer, empty + history states (desktop) |
| `02-error-state.png` | Upstream-error state with retry |
| `03-loading-skeleton.png` | Skeleton loading state |
| `04-plan-output.png` | Full plan output (route rail, budget meter) |
| `05-compare-variants.png` | 3-variant compare with winner highlight |
| `06-mobile.png` | Mobile layout (390px) |

`04`/`05` show representative plan data rendered through the real render path
(captured while the Fireworks account was suspended, so no live generation).

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then set FIREWORKS_API_KEY
uvicorn app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000` for the browser UI
- `http://127.0.0.1:8000/openapi` for API docs

## Endpoints

- `GET /` serves the UI.
- `GET /api/health` returns `{ "status": "ok" }`.
- `POST /api/plan` accepts goal/constraints/context/tone and returns the generated plan.
- Budget controls: set `KIMI_DAILY_BUDGET_USD` and `KIMI_ESTIMATED_COST_USD` in env to cap usage per UTC day.
- `GET /api/runs` returns recent saved runs.

## Data

Runs are stored in `data/runs.db` with schema:
`goal`, `constraints`, `context`, `tone`, `status`, `model`, `latency_ms`,
`response_json`, `raw_output`, `error`.

## Launch plan (recommended)

This service is designed to be launch-ready with:

1. Environment configured (`FIREWORKS_API_KEY` required in runtime).
2. SQLite writeable data directory (`data/` auto-created).
3. A single process command for local, Docker, or hosted deploys.

### Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # set FIREWORKS_API_KEY
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Local smoke test (after install)

```bash
python3 -m unittest discover -s tests -v
python3 - <<'PY'
import urllib.request, json
print(json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/health').read())["status"])
PY
```

### Docker run

```bash
docker build -t kimi-k3 .
docker run --rm -p 8000:8000 --env-file .env -v "$PWD/data:/app/data" kimi-k3
```

### Vercel deploy (full playground)

This project can be deployed on Vercel using the project-level `vercel.json` entry:

1. Install and login to Vercel CLI on your machine:
   ```bash
   npm i -g vercel
   vercel login
   ```
2. From `kimi-k3` root, push once (it will auto-detect the serverless entry in `api/index.py`):
   ```bash
   cd /Users/abhijitdas/Documents/Personal\ projects/kimi-k3
   vercel
   ```
3. Set environment variables in Vercel (Project Settings → Environment Variables):
   - `FIREWORKS_API_KEY` (required)
   - `FIREWORKS_MODEL` (default is `accounts/fireworks/models/llama-v3p3-70b-instruct`)
   - `FIREWORKS_TEMPERATURE` (optional)
   - `FIREWORKS_MAX_TOKENS` (optional)
   - `KIMI_DAILY_BUDGET_USD` (default `5`)
   - `KIMI_ESTIMATED_COST_USD` (default `0.02`)

4. Redeploy after env changes:
   ```bash
   vercel --prod
   ```

5. Verify after deploy:
   - `/api/health` returns `{ "status": "ok" }`
   - open `/` and run one generation with an example
   - verify budget cap behavior at /api/plan when exceeded

### Tomorrow launch checklist (minimum)

- [ ] Deploy target is set (Railway/Render/Fly/Vercel-compatible platform).
- [ ] Set env var: `FIREWORKS_API_KEY`.
- [ ] Optional tuning envs: `FIREWORKS_MODEL`, `FIREWORKS_TEMPERATURE`, `FIREWORKS_MAX_TOKENS`.
- [ ] Budget controls:
  - `KIMI_DAILY_BUDGET_USD` (default `5`) to enforce daily spend ceiling.
  - `KIMI_ESTIMATED_COST_USD` (default `0.02`) to estimate cost per generation call.
  - On cap hit, `POST /api/plan` returns HTTP 429 with user-facing message (e.g. “Daily testing cap reached. ... try again tomorrow.”).
- [ ] Set startup command to `uvicorn app.main:app --host 0.0.0.0 --port 10000`.
- [ ] Run endpoint checks:
  - `GET /api/health` returns ok.
  - `POST /api/plan` succeeds with real API key.
  - `GET /api/runs?limit=5` returns recent run rows.

## Known behavior

- If `FIREWORKS_API_KEY` is missing, plan generation returns a 502 with a clear error and records a failed run.
- If the model returns malformed output (JSON/prompt-shape issues), requests are rejected with a clear validation error.
