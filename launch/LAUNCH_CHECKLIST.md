# K3 Planner — Launch Checklist (v3)

Updated 2026-08-16 after the launch polish pass. Operational sequence lives in
`LAUNCH_DAY_RUNBOOK.md`; this is the state view.

## Done
- [x] Backend API implemented (`/api/plan`, `/api/health`, `/api/config`, `/api/runs`)
- [x] Frontend: risk-elevation strip, compare mode, demo mode, share links
- [x] Hero rebuilt for launch (top bar + tightened stack + CTA pair)
- [x] Action Plan Pack — strength score, risk mix, first three moves, copy-as-briefing
- [x] Plan strength scoring rebalanced (was saturating at 100 for every plan)
- [x] Failure UX — request preserved on error, retry re-sends the exact payload
- [x] Local persistence with write-safe budget controls
- [x] Runtime hardening for malformed model output
- [x] Vercel serverless compatibility (`KIMI_DB_PATH` writable path)
- [x] 35 automated tests passing
- [x] Responsive verified at 390px and 360px, no horizontal overflow
- [x] Launch copy written: blog, X thread, LinkedIn, video script

## Launch-blocking
- [ ] **Smoke run against the live URL** — `BASE_URL=https://kimi-k3-ashy.vercel.app scripts/smoke.sh`
      (never yet run by anyone; blocked from the cloud sandbox by network policy)
- [ ] One real generation end-to-end on the production URL
- [ ] Confirm the daily budget gate returns 429 on the deployed build
- [ ] Confirm tone alias compatibility (`tone=confident` → `clear`)
- [ ] Merge PR `#1` and re-run smoke **after** the redeploy
- [ ] **Flip the repo to public** — Settings → General → Danger Zone → Change visibility.
      No API for this; it has to be you. Secret scan is already clean.
- [ ] Final social copy approved (blog + X + LinkedIn)

## Decisions — all four closed 2026-08-16
- [x] **The name → K3 Planner.** "Kimi" dropped from every shipped surface. Repo path and
      deploy URL keep the `kimi-k3` slug (zero launch risk). Full rename rejected: the
      namespace is crowded and a URL swap hours before launch isn't worth it.
- [x] **Repo → public.** Full-history secret scan clean across 26 commits. One manual step
      left for Abhi (below) — there's no API for visibility changes.
- [x] **Budget → unchanged.** 5 days × $5/day = $25 total exposure. Cap is *not* being
      raised. When a day trips, the demo routes absorb the traffic; that's the design.
- [x] **Video → skip.** Launching on the three screenshots. `VIDEO_SCRIPT.md` stays in the
      kit for a post-launch cut if the thread earns one.

## Known gaps, accepted for v1
- Run history is ephemeral in production (SQLite on `/tmp`, lost on cold start)
- No CI configured — tests run locally only
- No auth or rate limiting per user; the daily cap is the only spend control

## Target launch state
- Production URL accessible and stable, smoke green against it
- Blog published before the socials go out
- Demo links (`?demo=plan`, `?demo=compare`) verified as the fallback if the cap trips
