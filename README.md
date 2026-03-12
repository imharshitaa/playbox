# Playbox Vulnerable Lab Environment

WARNING: WARNING: This project is intentionally insecure. It is for learning, training, and testing only. Run inside an isolated VM or an offline Docker host. Do not expose these services to the internet or production networks.

## What This Is
Playbox is a collection of deliberately vulnerable mini-services grouped by domain. Each domain exposes OWASP Top 10 (2021) style endpoints plus extra classic issues (SQLi, XSS, CORS, etc.). The goal is to provide a safe local playground for security testing, training, and tooling demos.

## What You Get
Domains and their lab surfaces:
- Web app lab (Flask, HTML) with XSS, CSRF, path traversal, uploads, etc.
- API lab (Flask, JSON) with SQLi, IDOR, weak auth, CORS, SSRF, etc.
- AI lab (Flask) with LLM-style prompts and agent-style tool execution
- Network lab (Flask + TCP) with unsafe length framing and HTTP wrappers
- Cloud lab (Flask) with insecure policies, metadata SSRF, misconfig examples
- Gateway (nginx) that routes unified paths: `/labs/web/`, `/labs/api/`, `/labs/ai/`, `/labs/network/`, `/labs/cloud/`

## Quick Start (Docker)
```
docker compose up --build -d
```
Gateway URLs (path-based):
- http://localhost/labs/web/
- http://localhost/labs/api/
- http://localhost/labs/ai/
- http://localhost/labs/network/
- http://localhost/labs/cloud/

If you want `http://playbox/...`, add `127.0.0.1 playbox` to your hosts file.

## Local Run (No Docker)
Prereqs:
- Python 3
- pip packages: `flask`, `requests`

Install deps:
```
pip install -r requirements.txt
```

Start services:
```
./run_local.sh
```

Optional local gateway (path-based /labs/... on one port):
```
./run_gateway_local.py
```
Gateway runs at: http://localhost:8081

Notes:
- The local gateway is a minimal Python reverse proxy. For the full nginx gateway, use Docker.
- Each service still runs on its own port locally.

## Direct Ports (Local Access)
- Web: http://localhost:8000
- API: http://localhost:5000
- AI: http://localhost:8080
- Network HTTP: http://localhost:9101
- Network TCP: localhost:9001
- Cloud App: http://localhost:9100
- MinIO: http://localhost:9000

## OWASP Top 10 (2021) Endpoint Pattern
Every domain exposes endpoints for:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)

Examples:
- Web SQLi: http://localhost/labs/web/sqli
- Web CORS: http://localhost/labs/web/cors
- API SQLi: http://localhost/labs/api/sqli
- AI prompt injection: http://localhost/labs/ai/prompt-injection
- Network unsafe length: http://localhost/labs/network/unsafe-length
- Cloud metadata SSRF: http://localhost/labs/cloud/metadata

## Repo Layout
- gateway/ -> Nginx reverse proxy for unified lab URLs
- vuln_webapp/ -> Web app lab
- vuln_api/ -> API lab
- vuln_ai/ -> AI lab (LLM + agent behaviors)
- vuln_network/ -> TCP server + HTTP network lab endpoints
- vuln_cloud/ -> Cloud lab API + MinIO
- run_local.sh -> Local runner for all services
- run_gateway_local.py -> Local reverse proxy gateway
- requirements.txt -> Local Python dependencies

## Security Notice
This repository is intentionally vulnerable. Use only in isolated environments. Do not expose it to any public network or production system.
