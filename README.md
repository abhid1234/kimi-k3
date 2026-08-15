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

### Frontend revamp — risk elevation (2026-08-09)

The plan visualization gained a signature element: a **risk-elevation strip**
drawn above the step rail. The plan is rendered as terrain — x is step order,
y is risk severity — so the route literally climbs into peaks where the plan
gets dangerous, in the style of a reaction-coordinate energy diagram. Design
decisions:

- **One signature, everything else quiet.** The strip carries the excitement;
  the step rail, aux sections, and composer keep their existing simplicity.
- **Structure encodes information.** Peak height maps to the same low/medium/high
  severities as the step badges; the shaded area under the trail and the
  HIGH/MED/LOW gridlines make the shape readable at a glance.
- **Two-way sync.** Hovering or keyboard-focusing a waypoint highlights its step
  card (and vice versa); Enter/Space on a waypoint jumps to the step. Waypoints
  are real focusable controls with per-step `aria-label`s, and the strip has a
  text summary for assistive tech.
- **Compare mode gets mini strips**, so three strategies read as three visibly
  different risk terrains next to the winner highlight.
- **Motion is an orchestrated moment, not ambience**: the trail draws in once
  (~0.9s), waypoints pop staggered, step cards follow — all disabled under
  `prefers-reduced-motion`.
- **Demo mode for testability**: `/?demo=plan` and `/?demo=compare` render
  bundled sample data through the real render path with zero API calls, clearly
  labelled ("Sample data — nothing was sent to the API"). Used for screenshots
  and demos when the upstream model account is unavailable.

Frontend contract tests live in `tests/test_frontend.py` (controls, labels,
a11y basics, risk badge coverage, strip presence, unchanged `/api/plan` payload
shape). New screenshots:

| | |
|---|---|
| `07-plan-risk-elevation.png` | Plan output with the risk-elevation strip (desktop) |
| `08-compare-risk-profiles.png` | Compare mode with per-variant mini risk profiles |
| `09-mobile-risk-elevation.png` | Mobile layout (390px) with the strip |

### Launch polish pass — premium hero + Action Plan Pack (2026-08-15)

Frontend-only pass. **No backend contract, DB schema, or planner logic changed** —
`/api/plan` accepts and returns exactly the same shapes.

**What changed**

1. **Hero rebuilt.** The old hero centred the wordmark, health chip and runtime
   config in one floating cluster above a 56px gap, which read as stretched and
   flat across wide viewports. It is now a proper top bar (wordmark hard left,
   live status hard right) over a tightened centre stack: kicker → headline →
   value proposition → CTA pair → proof chips. Bigger, tighter display type
   (0.9 line-height), a deeper background with a masked engineering grid, and a
   solid high-contrast primary CTA instead of the low-contrast translucent one.
2. **New: Action Plan Pack.** A briefing card above every plan showing **plan
   strength** (0–100 with an animated meter and strong/solid/thin grade),
   **risk mix** (low/medium/high proportions across the steps), and **"do these
   first"** — the top three moves as cards, plus one-click *Copy pack*. All of it
   is derived client-side from the response `/api/plan` already returns; no new
   endpoint, no extra call.
3. **Plan strength scoring rewritten.** The previous formula
   (`40 + steps * 12 + …`) saturated at five steps, so effectively every plan
   scored 100/100 and compare mode produced tied winners. Scoring now weights
   depth (20), section coverage (30), per-step specificity (15), risk literacy
   (15) and stated confidence (20) to exactly 100, so scores actually spread.
4. **New: "See a sample plan" CTA.** Renders bundled sample data through the real
   render path with zero API calls and seeds the composer, so a cold visitor sees
   a full plan instantly without spending budget.
5. **Failure UX.** A failed run now keeps your request visible ("Your request is
   saved" — goal, tone, whether constraints/context were kept) and **Retry this
   request** re-sends the exact failed payload instead of rebuilding it from the
   form.
6. **Bug — hidden states leaked.** `.output-tools { display: flex }` overrode the
   `hidden` attribute's `display: none`, so *Copy as Markdown / Copy share link /
   View raw JSON* were visible on the empty, loading and error states — and after
   a failure following a success they would copy the stale plan. `[hidden]` is now
   enforced globally; `#runMeta` and `#compareResult` had the same exposure.
7. **Bug — missing currency unit.** The runtime chip read `5.00/day cap`; now
   `$5.00/day cap`, and the redundant trailing `· cap on` is dropped.
8. **Bug — share mode lost on "First 3 actions."** `runActionFirst()` set
   `shareMode = "action"` and then called `runSingle()`, which immediately reset it
   to `"single"`, so those share links came back in the wrong mode. Mode is now
   passed through explicitly.
9. **Responsive.** Verified with no horizontal overflow at 390px and 360px; the
   hero bar stacks, CTAs go full-width, and the pack collapses to one column.

**What's new to test**

| Check | How |
|---|---|
| Hero on desktop | Load `/` at ≥1200px — wordmark left, status right, no centred cluster |
| Hero on mobile | Load `/` at 390px — stacked bar, full-width CTAs, no sideways scroll |
| Action Plan Pack | Click **See a sample plan** — strength meter animates, risk mix + 3 move cards |
| Copy pack | Click **Copy pack** in the pack — clipboard gets a plain-text briefing |
| Score spread | Run **Compare 3 variants** — the three scores should differ, not all read 100 |
| Failure UX | Kill network / hit the cap — error card keeps your goal and **Retry this request** re-sends it |
| Hidden states | On a fresh load the copy/share/raw buttons must **not** be visible |
| Budget guard | Unchanged — cap still returns 429 with the user-facing message |
| Demo routes | `/?demo=plan` and `/?demo=compare` still render with zero API calls |
| Share links | **Copy share link**, open it — composer rehydrates; `?auto=1` runs it |

New screenshots:

| | |
|---|---|
| `12-hero-premium-desktop.png` | Rebuilt hero (desktop) |
| `13-action-plan-pack.png` | Plan output with the Action Plan Pack |
| `14-hero-premium-mobile.png` | Rebuilt hero (390px) |

Captured in a sandbox without webfont access, so the display face falls back to
system sans; production loads Archivo.

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

### Smoke checks (local or deployed)

```bash
BASE_URL=http://127.0.0.1:8000 scripts/smoke.sh
# if testing prod:
BASE_URL=https://kimi-k3-ashy.vercel.app scripts/smoke.sh
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
   - `FIREWORKS_MODEL` (default is `accounts/fireworks/models/gpt-oss-120b`)
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

### One-click style publish cheatsheet

```bash
cd "/Users/abhijitdas/Documents/Personal projects/kimi-k3"
vercel --prod
```

Optional pre-flight before publish:

```bash
scripts/smoke.sh  # validate against your current local BASE_URL first
```

### Launch steps (quick)

```bash
cd "/Users/abhijitdas/Documents/Personal projects/kimi-k3"

# 1. tests must be green (35 checks: schema, budget, storage, frontend contract)
python3 -m pytest tests/ -q          # or: python3 -m unittest discover -s tests

# 2. eyeball it locally, no API spend needed
uvicorn app.main:app --reload
#    open http://127.0.0.1:8000 and click "See a sample plan"

# 3. ship
vercel --prod

# 4. verify the live deploy
BASE_URL=https://kimi-k3-ashy.vercel.app scripts/smoke.sh
```

Step 4 should print `{"status":"ok"}` for health, a plan JSON body for both
`/api/plan` calls, and the runtime config line. A `422` on `/api/plan` means the
production alias is pointing at an older deploy — re-alias and re-run.

**Demo links to have open when you launch:**

- `https://kimi-k3-ashy.vercel.app/` — the hero
- `https://kimi-k3-ashy.vercel.app/?demo=plan` — full plan + Action Plan Pack, zero API spend
- `https://kimi-k3-ashy.vercel.app/?demo=compare` — three strategies side by side, zero API spend

The `?demo=` links never call the model, so they cannot be broken by the daily
budget cap or an upstream outage mid-demo.

### Tomorrow launch checklist (minimum)

Launch artifacts live in [`launch/`](launch/):
- `launch/LAUNCH_CHECKLIST.md`
- `launch/FACTS.md`
- `launch/X_TWEET.md`
- `launch/SUBSTACK_DRAFT.md`
- `launch/README.md`

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
- Tone input is normalized (`confident`, `short`, `business`) to one of `clear`, `concise`, `executive`.
- If the model returns malformed output (JSON/prompt-shape issues), requests are rejected with a clear validation error.
