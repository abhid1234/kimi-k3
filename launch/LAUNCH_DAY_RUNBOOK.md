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

## Settled — no decisions left, just one action

**Name is K3 Planner.** "Kimi" is out of every shipped surface. The repo path and URL keep
the `kimi-k3` slug on purpose — changing a working deploy URL hours before launch isn't
worth it. If anyone asks: *"K3 is a project codename; it runs gpt-oss-120b on Fireworks.
The old slug is just the repo path."*

**Repo → public: this one is on you.** Settings → General → Danger Zone → Change
visibility. There's no API for it. A full-history secret scan came back clean (26 commits,
no keys or tokens, only `.env.example` ever committed), so it's safe to publish — but do it
**before** you post, or every repo link in the copy 404s.

**Budget stays at $5/day for 5 days.** $25 total exposure, not being raised.

---

## During the launch

- **The cap will probably trip on day one, and that's fine.** $5/day at ~$0.02 a run is
  roughly 250 generations. A thread that lands burns that in an afternoon. You've chosen
  not to raise it — so treat the trip as expected, not as an incident.
- **When it trips:** it fails clean — 429 with a plain message, not a crash. Pin a reply
  with `?demo=plan`, which never calls the API and renders the identical UI. Resets at
  **midnight UTC**, so day two opens with a fresh $5.
- **Across 5 days that's $25 total.** If day one converts well and you want more live
  runs on day two, raising `KIMI_DAILY_BUDGET_USD` is a one-line env change plus a
  redeploy — decide it on the data, not in advance.
- **If Fireworks goes down:** same move. The demo links keep working; the error state
  keeps people's input and offers a real retry.
- **Reply to everything for the first two hours.** Early replies drive the thread more
  than the posting time does.

---

## After

- Record the final production URL and the day's run count in `FACTS.md`
- Note which post did the work — thread, LinkedIn, or the blog — and fold it into `monica/VOICE.md`
- Screenshot the run history after a real day of traffic; it's the best proof the thing gets used
