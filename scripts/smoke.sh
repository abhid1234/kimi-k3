#!/usr/bin/env bash
set -euo pipefail

# Smoke test Kimi K3 API endpoints against a target URL.
# Usage:
#   BASE_URL=https://kimi-k3-ashy.vercel.app scripts/smoke.sh
#   [optional] BASE_URL defaults to http://127.0.0.1:8000

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PLAN_PAYLOAD='{"goal":"Draft a 14-day launch plan for a side AI tool","constraints":"Only use built-in APIs","context":"solo founder","tone":"confident"}'
PLAN_PAYLOAD_CANONICAL='{"goal":"Draft a 14-day launch plan for a side AI tool","constraints":"Only use built-in APIs","context":"solo founder","tone":"concise"}'

echo "==> Health"
curl -fsSL "$BASE_URL/api/health"
echo

echo "==> Last 5 runs"
curl -fsSL "$BASE_URL/api/runs?limit=5"
echo

post_plan() {
  local label="$1"
  local payload="$2"
  local tmp header status
  tmp=$(mktemp)
  header=$(mktemp)

  echo "==> $label"
  echo "Payload: $payload"
  curl -sS -D "$header" -X POST \
    -H "content-type: application/json" \
    -d "$payload" \
    "$BASE_URL/api/plan" \
    -o "$tmp"
  echo
  if sed -n '1p' "$header" | grep -q "HTTP/"; then
    status=$(sed -n '1p' "$header" | awk '{print $2}')
  else
    status="unknown"
  fi
  cat "$tmp"
  echo
  if [ "$status" != "unknown" ] && [ "${status:0:1}" != "2" ]; then
    if [ "$status" = "422" ]; then
      echo "⚠️ 422 tone validation error: this deployment may be using an older schema."
    elif grep -q "Model output schema mismatch" "$tmp"; then
      echo "⚠️ response schema mismatch: model output not matching contract."
    else
      echo "⚠️ status=$status for /api/plan"
    fi
  fi
  rm -f "$tmp" "$header"
}

post_plan "Generate plan (tone alias)" "$PLAN_PAYLOAD"
post_plan "Generate plan (canonical tone)" "$PLAN_PAYLOAD_CANONICAL"

echo "==> Runtime config"
curl -sS -D - "$BASE_URL/api/config" | sed -n '1,60p'
echo

echo "==> Budget guard"
curl -sS -D - -X POST \
  -H "content-type: application/json" \
  -d "{\"goal\":\"Budget check\",\"constraints\":\"Only use built-in APIs\",\"context\":\"capacity test\",\"tone\":\"short\"}" \
  "$BASE_URL/api/plan" | sed -n '1,80p' || true
echo

echo "Smoke complete"
