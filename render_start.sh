#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$ROOT_DIR/.render_logs"

mkdir -p "$LOG_DIR"

echo "Starting Playbox services for Render"

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

# Gateway (must run in foreground)
exec python3 "$ROOT_DIR/run_gateway_local.py"
