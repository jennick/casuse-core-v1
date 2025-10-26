#!/usr/bin/env bash
set -euo pipefail
SMOKE_BASE=${SMOKE_BASE:-http://localhost:9000} python agent/cli.py smoke
