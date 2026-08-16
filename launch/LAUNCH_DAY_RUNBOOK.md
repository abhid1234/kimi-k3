# Launch day runbook

Order of operations for the next few hours. Everything above the line is blocking.

---

## Pre-flight (blocking — do not post until these pass)

Run from `/Users/abhijitdas/Documents/Personal projects/kimi-k3`:

```bash
# 1. tests green (35 checks)
python3 -m pytest tests/ -q

# 2. live smoke against the deployed URL  ← NOT yet run by anyone
BASE_URL=https://kimi-k3-ashy.vercel.app scripts/smoke.sh
```

Smoke should print `{"status":"ok"}` for health, a plan JSON body for **both** `/api/plan`
calls, and the runtime config line. Then by hand:

- [ ] `https://kimi-k3-ashy.vercel.app/` loads, health chip reads **api live**
- [ ] Runtime chip reads **$5.00/day cap** — with the dollar sign
- [ ] One real generation end to end, with a goal you'd actually use
- [ ] `?demo=plan` and `?demo=compare` both render with no API call
- [ ] Open the site on your phone — the hero should stack, no sideways scroll
- [ ] Copy a share link, open it in a private window, confirm the composer rehydrates

**Failure modes and what they mean:**

| Symptom | Cause | Fix |
|---|---|---|
| `422` on `/api/plan` | Production alias points at an older deploy | Redeploy, re-alias, re-run smoke |
| `502` with "FIREWORKS_API_KEY is not configured" | Env var missing on Vercel | Set it in Project Settings → Environment Variables, redeploy |
| `429` immediately | Daily cap already consumed | Raise `KIMI_DAILY_BUDGET_USD` or wait for midnight UTC |
| Health chip reads **api unreachable** | Function cold-start or deploy broken | Check Vercel deploy logs before posting anything |

---

## Sequence once pre-flight is green

1. **Merge the polish PR** — `abhid1234/kimi-k3#1`, currently a draft. Undraft, merge, let Vercel redeploy.
2. **Re-run smoke** after the redeploy. The pre-flight above tested the *old* build if you ran it before merging.
3. **Publish the Substack post** (`SUBSTACK_DRAFT.md`). It's the anchor — everything else links to it.
4. **Post the X thread** (`X_TWEET.md`). Link sits in post 5.
5. **Post to LinkedIn** ~30–60 min after X, not simultaneously. Different audience, different peak.
6. **Pin the thread** on X for the day.

Post the blog before the socials. If the thread lands and the post isn't up, the traffic has nowhere to go.

---

## Decide before you post

**The repo is currently private.** `LAUNCH_CHECKLIST.md` assumes "public repo exists" as
the target state. Either flip it to public before launch or cut every repo reference from
the copy — a dead GitHub link in a launch thread is worse than no link.

**The name.** The project is "Kimi K3"; it runs `gpt-oss-120b` on Fireworks. Kimi K3 is
also a real Moonshot model. Somebody will ask. Have the answer ready and don't get
defensive about it — `X_TWEET.md` has the one-liner.

---

## During the launch

- **Watch the cap.** $5/day at ~$0.02 a run is roughly 250 generations. A thread that
  lands can burn that in an afternoon. If you want headroom, raise
  `KIMI_DAILY_BUDGET_USD` *before* posting, not after it trips.
- **If the cap trips mid-day:** it fails clean — 429 with a plain message, not a crash.
  Point people at `?demo=plan`, which never calls the API. That's exactly what it's for.
- **If Fireworks goes down:** same move. The demo links keep working; the error state
  keeps people's input and offers a real retry.
- **Reply to everything for the first two hours.** Early replies drive the thread more
  than the posting time does.

---

## After

- Record the final production URL and the day's run count in `FACTS.md`
- Note which post did the work — thread, LinkedIn, or the blog — and fold it into `monica/VOICE.md`
- Screenshot the run history after a real day of traffic; it's the best proof the thing gets used
