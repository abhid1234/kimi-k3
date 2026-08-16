# Demo video — script + shot list

Two cuts. The 60-second one is the post/embed. The 20-second silent loop is what
autoplays on X and LinkedIn, where most people never unmute.

**Record against `?demo=plan` and `?demo=compare`, not a live run.** Demo routes render
bundled sample data through the real render path with zero API calls, so nothing in the
recording can be broken by the daily cap, a slow generation, or an upstream blip. The UI
is identical.

Capture at 1440×900, 2x. Hide bookmarks bar and any personal tabs before recording.

---

## Cut A — 60 seconds (voiceover)

| Time | Shot | Voiceover |
|---|---|---|
| 0:00–0:05 | Hero, static. Cursor still. | "Kimi K3 turns one sentence into a plan you can actually run." |
| 0:05–0:12 | Type a real goal into the composer. Don't paste — typing reads as real. | "You give it a goal and your constraints." |
| 0:12–0:18 | Click Generate. Skeleton loader resolves into the plan. | "It comes back ordered, with the reasoning attached to every step." |
| 0:18–0:30 | Slow scroll to the Action Plan Pack. Pause on the strength meter, then the risk mix. | "Every plan gets scored — depth, coverage, specificity, and how seriously it treated risk. This one's a 93, not a 100. The score is allowed to disagree with you." |
| 0:30–0:40 | Hover across the risk-elevation strip; steps highlight in sync. | "Risk is drawn as terrain. The dangerous stretch of the plan is a peak you can see, instead of the fourth bullet in a list." |
| 0:40–0:50 | Click **Compare 3 variants**. Three columns land with visibly different strips. | "Same goal, three strategies — current constraints, speed-first, risk-minimized. Three different risk profiles, side by side." |
| 0:50–0:57 | Back to the pack. Click **Copy pack**. Button flips to "Copied". | "And the first three moves copy out as a briefing in one click." |
| 0:57–1:00 | Hero, static. URL on screen. | "Link's below. It's free, and there's a demo mode that doesn't touch the API." |

**Voiceover notes:** flat delivery beats enthusiastic. No "super excited". Say "93, not a
100" with a small pause before it — it's the line people will quote.

---

## Cut B — 20-second silent loop (captions burned in)

No voiceover. Motion carries it. Caption card ≤ 6 words, bottom third, high contrast.

| Time | Shot | Caption |
|---|---|---|
| 0:00–0:03 | Hero. | `Goal in. Route out.` |
| 0:03–0:07 | Generate → plan lands. | `One sentence → ordered plan` |
| 0:07–0:12 | Pack: meter fills, risk mix. | `Scored. 93, not 100.` |
| 0:12–0:16 | Hover the risk terrain. | `Risk you can see` |
| 0:16–0:20 | Compare: three strips. | `Three strategies, side by side` |

Loop cleanly: end frame ≈ start frame, so cut back to the hero on the last beat.

---

## If you'd rather not record

`docs/screenshots/12-hero-premium-desktop.png`, `13-action-plan-pack.png` and
`14-hero-premium-mobile.png` carry the launch on their own. A 3-image post with the
score-bug story as the copy works without any video at all — the hook is the writing,
not the motion.

---

## Frames worth grabbing as stills

- The pack with the meter mid-fill (~40% through the animation) — best single image of the product
- The compare row, all three strips visible at once — best image of the *idea*
- The mobile hero — proves it isn't desktop-only

Pull these from the recording rather than re-screenshotting; the animation frames look better than the static state.
