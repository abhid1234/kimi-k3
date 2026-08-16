# Kimi K3 — Launch Checklist (v2)

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
- [ ] **Decide: make the repo public, or strip repo links from all launch copy**
- [ ] Final social copy approved (blog + X + LinkedIn)

## Decisions needed from Abhi
- [ ] **Repo visibility.** Currently private. Public-repo links in copy will 404.
- [ ] **The name.** "Kimi K3" runs `gpt-oss-120b`, not Moonshot's Kimi K3. Ship as-is with
      the plain answer ready, or rename before launch. Renaming means the URL too.
- [ ] **Cap headroom.** $5/day ≈ 250 runs. Raise it before posting if you expect the
      thread to land, not after it trips.
- [ ] **Video.** Script is ready in `VIDEO_SCRIPT.md`. No video file has reached this
      session — record it, or run the launch on the three screenshots.

## Known gaps, accepted for v1
- Run history is ephemeral in production (SQLite on `/tmp`, lost on cold start)
- No CI configured — tests run locally only
- No auth or rate limiting per user; the daily cap is the only spend control

## Target launch state
- Production URL accessible and stable, smoke green against it
- Blog published before the socials go out
- Demo links (`?demo=plan`, `?demo=compare`) verified as the fallback if the cap trips
