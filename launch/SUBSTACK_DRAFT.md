# Substack Draft: Why we built Kimi K3

I got tired of “AI planners” that answer in prose but never show me where risk is actually concentrated.

So I built **Kimi K3**: a practical planning assistant that outputs an ordered route with visible risk elevation.

## What it does
- Converts a goal into actionable steps
- Surfaces assumptions, risks, and next actions
- Shows risk as a terrain-style strip so risky portions are visually obvious
- Lets you compare 3 variants side-by-side
- Stores recent runs so you can learn from previous attempts
- Keeps cost under control with a daily spend gate

## Why this is launch-ready
- Hardened output validation to handle model quirks
- Stable API contract and tests
- Deploy path works on Vercel with serverless-safe SQLite path
- Demo mode means people can test visuals even when API keys are unavailable

## Launch intent
This is intended as an internal and external demonstration project first. The goal is to make planning feel tactile, not theoretical.
