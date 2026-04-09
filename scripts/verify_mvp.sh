#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_PORT=8010
FRONTEND_PORT=3110
API_BASE="http://127.0.0.1:${BACKEND_PORT}"
WEB_BASE="http://127.0.0.1:${FRONTEND_PORT}"

BACK_PID=""
FRONT_PID=""

cleanup() {
  if [[ -n "$FRONT_PID" ]] && kill -0 "$FRONT_PID" 2>/dev/null; then
    kill "$FRONT_PID" >/dev/null 2>&1 || true
    wait "$FRONT_PID" 2>/dev/null || true
  fi
  if [[ -n "$BACK_PID" ]] && kill -0 "$BACK_PID" 2>/dev/null; then
    kill "$BACK_PID" >/dev/null 2>&1 || true
    wait "$BACK_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT

check_status() {
  local expected="$1"
  local url="$2"
  local code
  code="$(curl -s -o /dev/null -w "%{http_code}" "$url")"
  if [[ "$code" != "$expected" ]]; then
    echo "[FAIL] $url -> expected $expected, got $code"
    exit 1
  fi
  echo "[OK]   $url -> $code"
}

check_post() {
  local expected="$1"
  local url="$2"
  local payload="$3"
  local code
  code="$(curl -s -o /dev/null -w "%{http_code}" -X POST "$url" -H "Content-Type: application/json" -d "$payload")"
  if [[ "$code" != "$expected" ]]; then
    echo "[FAIL] $url (POST) -> expected $expected, got $code"
    exit 1
  fi
  echo "[OK]   $url (POST) -> $code"
}

echo "[1/5] Running backend tests"
if [[ ! -x "$BACKEND_DIR/.venv/bin/pytest" ]]; then
  echo "[FAIL] backend virtualenv pytest not found at backend/.venv/bin/pytest"
  exit 1
fi
(cd "$BACKEND_DIR" && ./.venv/bin/pytest)

echo "[2/5] Building frontend"
(cd "$FRONTEND_DIR" && NEXT_PUBLIC_API_URL="$API_BASE" npm run build)

echo "[3/5] Starting backend"
(
  cd "$BACKEND_DIR"
  ./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT" >/tmp/gs_verify_backend.log 2>&1
) &
BACK_PID="$!"
sleep 2

echo "[4/5] API smoke checks"
check_status 200 "$API_BASE/health"
check_status 200 "$API_BASE/api/v1/public/home"
check_status 200 "$API_BASE/api/v1/public/units"
check_status 200 "$API_BASE/api/v1/public/equips"
check_status 200 "$API_BASE/api/v1/public/tierlists"
check_status 200 "$API_BASE/api/v1/public/bosses"
check_status 200 "$API_BASE/api/v1/public/modes"
check_status 200 "$API_BASE/api/v1/public/guides"
check_status 200 "$API_BASE/api/v1/public/ai-presets"
check_status 200 "$API_BASE/api/v1/public/progression-paths"
check_status 200 "$API_BASE/api/v1/admin/overview"

check_post 200 "$API_BASE/api/v1/public/team-builder/recommend" '{"mode":"CREST_PALACE","boss_id":"boss_crest_nova_ashdrake","desired_style":"SUSTAIN","roster":{"unit_ids":["unit_hart","unit_cestina","unit_vox","unit_fen"],"equip_ids":["equip_true_flambardo"]}}'
check_post 200 "$API_BASE/api/v1/public/team-builder/classify" '{"unit_ids":["unit_hart","unit_vox","unit_fen","unit_cestina"]}'
check_post 200 "$API_BASE/api/v1/public/bosses/ashdrake-crest-nova/solve" '{"desired_style":"SUSTAIN","roster":{"unit_ids":["unit_hart","unit_cestina","unit_vox","unit_fen"],"equip_ids":["equip_true_flambardo"]}}'

echo "[5/5] Starting frontend and checking routes"
(
  cd "$FRONTEND_DIR"
  NEXT_PUBLIC_API_URL="$API_BASE" npm run start -- --hostname 127.0.0.1 --port "$FRONTEND_PORT" >/tmp/gs_verify_frontend.log 2>&1
) &
FRONT_PID="$!"
sleep 5

check_status 200 "$WEB_BASE/"
check_status 200 "$WEB_BASE/units"
check_status 200 "$WEB_BASE/equips"
check_status 200 "$WEB_BASE/tierlists"
check_status 200 "$WEB_BASE/bosses"
check_status 200 "$WEB_BASE/comps"
check_status 200 "$WEB_BASE/team-builder"
check_status 200 "$WEB_BASE/modes"
check_status 200 "$WEB_BASE/guides"
check_status 200 "$WEB_BASE/ai-presets"
check_status 200 "$WEB_BASE/progression"
check_status 200 "$WEB_BASE/admin"
check_status 200 "$WEB_BASE/search?q=hart"

echo "All checks passed."
