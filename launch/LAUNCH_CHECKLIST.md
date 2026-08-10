# Kimi K3 — Launch Checklist (v1)

## Status
- [x] Backend API implemented (`/api/plan`, `/api/health`, `/api/runs`)
- [x] Frontend polished with route/terrain visual + compare mode + demo mode
- [x] Local persistence with write-safe budget controls
- [x] Runtime hardening for malformed model output
- [x] Vercel serverless compatibility fixed (`KIMI_DB_PATH` writable path)

## Launch-blocking checks
- [ ] Smoke run against live API key on deploy URL (POST `/api/plan`)
- [ ] Run `/api/health` and `/api/runs` on the final URL
- [ ] Confirm daily budget gate behavior (`$5/day` enforced)
- [ ] Confirm tone alias compatibility (`tone=confident` works)
- [ ] Record final production URL and screenshot set
- [ ] Final social copy approved (X + Substack)

## Non-blocking quality to finish
- [ ] Verify `.env` and Vercel env examples in onboarding docs are clear
- [ ] Add deployment command cheatsheet for one-click publish
- [ ] Add launch artifact links (`FACTS`, `README`, posts)

## Target launch state (tomorrow)
- Public repo exists and CI/docs are clean
- Production URL is accessible and stable
- One-page public-facing launch post and short X teaser prepared
