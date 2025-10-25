#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://core.127.0.0.1.nip.io:10443}"

function check() {
  local url="$1"
  local expect="${2:-200}"
  echo "-> GET $url"
  code=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" || true)
  if [[ "$code" != "$expect" ]]; then
    echo "!! FAIL: $url (got $code, expected $expect)"
    exit 1
  fi
}

echo "=== Smoke test against $BASE_URL ==="
check "${BASE_URL}/" 200
check "${BASE_URL}/healthz" 200 || check "${BASE_URL}/api/healthz" 200 || true
check "${BASE_URL}/docs" 200 || true

echo "OK: smoke tests passed."
