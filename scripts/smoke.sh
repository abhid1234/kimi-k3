#!/usr/bin/env bash
set -euo pipefail

# Smoke test Kimi K3 API endpoints against a target URL.
# Usage:
#   BASE_URL=https://kimi-k3-ashy.vercel.app scripts/smoke.sh
#   [optional] BASE_URL defaults to http://127.0.0.1:8000

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PLAN_PAYLOAD='{"goal":"Draft a 14-day launch plan for a side AI tool","constraints":"Only use built-in APIs","context":"solo founder","tone":"confident"}'

echo "==> Health"
curl -fsSL "$BASE_URL/api/health"
echo

echo "==> Last 5 runs"
curl -fsSL "$BASE_URL/api/runs?limit=5"
echo

echo "==> Generate plan (tone alias)"
echo "Payload: $PLAN_PAYLOAD"
curl -sS -D - -X POST \
  -H "content-type: application/json" \
  -d "$PLAN_PAYLOAD" \
  "$BASE_URL/api/plan" | sed -n '1,80p'
echo

echo "==> Budget guard"
curl -sS -D - -X POST \
  -H "content-type: application/json" \
  -d "{\"goal\":\"Budget check\",\"constraints\":\"Only use built-in APIs\",\"context\":\"capacity test\",\"tone\":\"short\"}" \
  "$BASE_URL/api/plan" | sed -n '1,80p' || true
echo

echo "Smoke complete"
