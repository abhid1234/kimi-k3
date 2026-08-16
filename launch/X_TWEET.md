# Social copy — X thread + LinkedIn

Voice rules applied (`monica/VOICE.md`): lead with the point, have a take, specific over
vague, no hype, no hashtags, at most one emoji, end on a takeaway not a CTA.
Char counts are per-post and all land under 260.

---

## X thread (7 posts)

**1/ — hook, works standalone** *(232 chars)*

> I built a quality score for AI-generated plans. It returned 100/100 for every plan.
>
> Not a model problem. My formula saturated at five steps, and every plan has five steps.
>
> A metric that never disagrees with you is decoration.

**2/** *(216 chars)*

> Worse: compare mode ranks 3 strategies by that same score.
>
> All three tied at 100. So the "highest score" badge was just picking whichever request came back first.
>
> I'd built a ranking that ranked nothing.

**3/** *(243 chars)*

> Rebalanced to five components summing to 100:
>
> depth 20
> section coverage 30
> per-step specificity 15
> risk literacy 15
> stated confidence 20
>
> Same sample plan now scores 93. It can disagree with me. That's the point of having it.

**4/** *(238 chars)*

> Risk literacy is the input I'd defend hardest.
>
> If a model rates all six steps "low", it didn't think about risk — it filled a required field. Uniform ratings get penalised.
>
> Naming the dangerous step is the thing you wanted.

**5/** *(247 chars)*

> The tool: goal in, ordered plan out. Every step risk-rated and drawn as terrain, so the dangerous stretch is a visible peak instead of the fourth bullet in a list.
>
> $5/day hard cap so a public demo can't be bill-bombed.
>
> kimi-k3-ashy.vercel.app

**6/** *(228 chars)*

> Second bug, same flavour: a CSS display rule overrode the hidden attribute, so "Copy plan" stayed live during errors — and copied the *previous* plan. Silently.
>
> Failure paths are where trust dies. Nobody tests them.

**7/ — takeaway, no CTA** *(249 chars)*

> The pattern: the model output was fine both times. Both bugs were in the surfaces I built around it — the score, the error state.
>
> If you ship LLM features, go check what your "confidence" indicator is computed from. I'd bet some are constants.

---

## LinkedIn *(203 words)*

> I built a quality score for AI-generated plans. It returned 100/100 for every plan.
>
> The formula was `40 + (steps × 12) + bonuses`. Five steps hits the ceiling, and every plan the model returns has five or more steps. So the meter read perfect, every time, forever.
>
> It got worse downstream. My compare mode generates three strategies for the same goal and ranks them by that score — so all three tied, and the "highest score" badge was landing on whichever request finished first. A ranking that ranked nothing.
>
> A metric that always returns the same number isn't a weak metric. It's decoration. And it's everywhere in AI products right now: confidence bars at a fixed width, quality badges computed from nothing. They look like instrumentation and function as reassurance.
>
> I rebalanced it across five weighted components — depth, section coverage, per-step specificity, risk literacy, and stated confidence. The one I'd defend hardest is risk literacy: if a model rates every step "low", it didn't assess risk, it filled a required field.
>
> The same sample plan now scores 93 instead of 100. It can disagree with me, which is the only reason to show it at all.
>
> Worth an audit: whatever confidence indicator your product shows users — what is it actually computed from?

---

## Notes for posting

- **Link placement:** the URL sits in post 5, mid-thread, so the thread still ends on the
  takeaway rather than a CTA. If reach matters more than form, move it to a reply on post 7.
- **Don't lead with the product.** The score bug is the hook; the tool is the evidence.
  Leading with "I built a tool" buries it.
- **If someone asks which model it runs:** `gpt-oss-120b` on Fireworks. Answer plainly.
  The product is **K3 Planner** — "Kimi" is off every shipped surface. The URL still reads
  `kimi-k3-ashy` because that's the repo slug and changing a working deploy URL on launch
  day isn't worth it. One line, no defensiveness: *"K3 is a project codename; it runs
  gpt-oss-120b. The slug is just the repo path."*
- **When the daily cap trips** (likely on day one — $5/day is ~250 runs): reply with
  `?demo=plan`. Identical UI, no API call. Resets midnight UTC.
- **Reply-bait to have ready:** people will ask how risk severity is decided. Answer: the
  model assigns it per step; the frontend normalizes anything off-enum to low/medium/high,
  and uniform ratings cost you points in the score.
