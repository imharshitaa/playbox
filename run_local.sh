#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/.local_logs"

mkdir -p "$LOG_DIR"

echo "Starting Playbox labs (local, no Docker)"

# Web
( cd "$ROOT_DIR/vuln_webapp" && python3 app.py ) >"$LOG_DIR/web.log" 2>&1 &

# API
( cd "$ROOT_DIR/vuln_api" && python3 api.py ) >"$LOG_DIR/api.log" 2>&1 &

# AI
( cd "$ROOT_DIR/vuln_ai" && python3 app.py ) >"$LOG_DIR/ai.log" 2>&1 &

# Network (HTTP + TCP)
( cd "$ROOT_DIR/vuln_network" && python3 app.py ) >"$LOG_DIR/network.log" 2>&1 &

# Cloud app
( cd "$ROOT_DIR/vuln_cloud" && python3 app.py ) >"$LOG_DIR/cloud.log" 2>&1 &

# Gateway (nginx via docker is not available locally)

echo "Launched services. Logs in $LOG_DIR"

echo "Ports:"

echo "- Web: http://localhost:8000"

echo "- API: http://localhost:5000"

echo "- AI: http://localhost:8080"

echo "- Network HTTP: http://localhost:9101"

echo "- Cloud App: http://localhost:9100"

echo "- Network TCP: localhost:9001"

cat <<'EOT'
Note: The unified /labs/... gateway runs on nginx via Docker. For local runs,
access each service directly by its port, or use a local reverse proxy.
EOT
