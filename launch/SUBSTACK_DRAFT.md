# The quality score that always said 100

*I shipped a planning tool this week. The most useful thing I found in it was a bug in my own scoring.*

---

I built **K3 Planner** over a few weekends. You give it a goal — "launch a paid AI side project to 100 users in 30 days" — and it returns an ordered plan: steps, why each one matters, a risk rating on every step, the assumptions it made, and your first three moves.

Standard stuff. The part worth writing about is what I found while polishing it for launch.

## The meter that never disagreed

I'd built a "plan strength" score, 0–100, with a little meter under it. The formula was roughly:

```
40 + (steps × 12) + 10 if assumptions + 10 if risks + 10 if next actions
```

Five steps gets you to 100. Every plan the model produces has five or more steps. So every plan scored 100/100. Perfect, every time, forever.

It gets worse. Compare mode generates three strategies for the same goal and ranks them by that same score. All three tied at 100, so the "highest score" badge was effectively landing on whichever request came back first. I'd built a ranking that ranked nothing.

A metric that always returns the same number isn't a weak metric. It's decoration.

And this is everywhere in AI products right now. Confidence bars at a fixed width. "High confidence" badges computed from nothing. Quality indicators that exist because the design called for one, not because anything is being measured. They look like instrumentation and function as reassurance.

I shipped one in my own tool without noticing, which is the part that should bother me most.

## What replaced it

Five components, weighted to sum to exactly 100:

- **Depth (20)** — 5–8 steps is the runnable range. Three steps isn't a plan; fifteen is a wish list.
- **Section coverage (30)** — did it actually fill in assumptions, risks, next actions.
- **Specificity (15)** — proportion of steps whose reasoning is substantive rather than a restated title.
- **Risk literacy (15)** — how many distinct severity levels it used.
- **Stated confidence (20)** — what the model claims about itself.

Risk literacy is the one I'd defend hardest. If a model rates all six steps "low", it almost certainly didn't think about risk — it filled a required field. Uniform ratings get penalised. A plan that says "step 3 is high risk" scores better than one that shrugs, because naming the dangerous part is the thing you actually wanted.

The same sample plan now scores 93, not 100. It can disagree with me. That's the only reason to have it.

## The other bug: state that leaks

Second one, same flavour. A CSS rule (`display: flex`) was silently overriding the `hidden` attribute on the output toolbar. So *Copy as Markdown / Copy share link / View raw JSON* stayed visible on the empty state, the loading state, and the error state.

The empty state is cosmetic. The error state is not: generate a plan, then have the next one fail, and the copy button is still sitting there — and it copies the **previous** plan. Silently. You'd paste it into a doc and never know.

Nobody tests the failure path. It's where trust actually dies.

So the error state got rebuilt too. When a run fails now, the card keeps your request visible — your goal, your tone, whether constraints and context were preserved — and "Retry this request" re-sends that exact payload instead of quietly rebuilding it from whatever is in the form. If your run dies, you shouldn't also lose what you typed.

## What the thing actually does

- **Risk as terrain.** The plan is drawn as an elevation strip: x is step order, y is risk severity. The dangerous stretch of a plan is a visible peak instead of the fourth bullet in a list. Hover a peak, the step highlights.
- **Action Plan Pack.** Above every plan: strength score, the risk mix across steps, and the first three moves as cards. One click copies the lot as a briefing.
- **Compare three strategies.** Same goal through *current constraints*, *speed-first*, and *risk-minimized*. Three genuinely different risk terrains, side by side.
- **A hard budget cap.** $5/day. On the cap it returns a 429 with a plain message rather than a stack trace. A public demo that can be bill-bombed isn't a demo, it's a liability.

## What it isn't

It's a harness, not a model. It runs `gpt-oss-120b` hosted on Fireworks, and the interesting engineering is in the surfaces around the model: the schema validation that sanitizes malformed output before it reaches the UI, the spend gate, the error states, the scoring.

That's deliberate. The model was the easy part. Both bugs I found this week were in what I built around it.

## Try it

- **[kimi-k3-ashy.vercel.app](https://kimi-k3-ashy.vercel.app)** — bring a real goal
- **[/?demo=plan](https://kimi-k3-ashy.vercel.app/?demo=plan)** — full plan, no API call
- **[/?demo=compare](https://kimi-k3-ashy.vercel.app/?demo=compare)** — three strategies, no API call

The demo links render bundled sample data through the real render path, so they work regardless of the daily cap or upstream availability.

If you build with LLMs: go look at whatever quality or confidence indicator you're showing users, and check what it's computed from. I'd bet a meaningful share of them are constants.
