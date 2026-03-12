# Playbox Technical Documentation

## Purpose
Playbox is a deliberately vulnerable lab environment for cybersecurity testing and training. It provides multiple domains (web, API, AI, network, cloud) with OWASP Top 10 (2021) style endpoints. Each endpoint is intentionally unsafe and should only be used in isolated, local environments.

## High-Level Architecture
- A set of small Flask services implement each lab domain.
- A TCP server is bundled for network-level testing.
- Optional gateway routes all labs under a single path prefix.
- Docker Compose can orchestrate everything, or you can run services locally without Docker.

## Services and Responsibilities

Web Lab (`vuln_webapp`)
Framework: Flask. Focus: classic web issues (XSS, CSRF, traversal, uploads) and OWASP Top 10 routes. Storage: SQLite database in `/tmp/web_lab.db`.

API Lab (`vuln_api`)
Framework: Flask. Focus: API-style issues (SQLi, IDOR, CORS, weak auth, SSRF) and OWASP Top 10 routes. Storage: SQLite database in `/tmp/api_lab.db`.

AI Lab (`vuln_ai`)
Framework: Flask. Focus: LLM-style prompt injection and agent tool execution. Special: when `ALLOW_EXEC=1`, it can execute commands or fetch URLs.

Network Lab (`vuln_network`)
Framework: Flask + Python TCP server. Focus: unsafe length framing and network misconfig examples. TCP listens on port 9001 with a 4-byte length prefix parser.

Cloud Lab (`vuln_cloud`)
Framework: Flask. Focus: insecure policy handling, metadata SSRF, misconfig examples. MinIO is included via Docker Compose for S3-like storage.

Gateway (`gateway`)
Nginx reverse proxy that exposes unified routes: `/labs/web/`, `/labs/api/`, `/labs/ai/`, `/labs/network/`, `/labs/cloud/`

## OWASP Top 10 (2021) Mapping
Each domain exposes endpoints for A01 Broken Access Control, A02 Cryptographic Failures, A03 Injection, A04 Insecure Design, A05 Security Misconfiguration, A06 Vulnerable and Outdated Components, A07 Identification and Authentication Failures, A08 Software and Data Integrity Failures, A09 Security Logging and Monitoring Failures, and A10 Server-Side Request Forgery (SSRF).

Additional classic routes exist per domain, such as `sqli`, `cors`, `prompt-injection`, and `unsafe-length`.

## Local Run Flow (No Docker)
1. Install dependencies: `pip install -r requirements.txt`
2. Start all services: `./run_local.sh`
3. Optional: start the local gateway: `./run_gateway_local.py`

## Docker Run Flow
1. Build and start everything: `docker compose up --build -d`
2. Access unified paths at `http://localhost/labs/web/`, `http://localhost/labs/api/`, `http://localhost/labs/ai/`, `http://localhost/labs/network/`, `http://localhost/labs/cloud/`

## Data Storage
- Web lab SQLite DB: `/tmp/web_lab.db`
- API lab SQLite DB: `/tmp/api_lab.db`
- Comments and temporary files stored under `/tmp`

## Security Model (Intentionally Weak)
No auth enforcement for many endpoints. Unsafe string concatenation for SQL queries. Wildcard CORS configuration in several labs. SSRF-like endpoints that fetch remote URLs. Optional command execution in AI lab when enabled.

## Extending the Labs
Add endpoints in each domain under `/labs/<domain>/...`. Keep behavior intentionally unsafe but isolated. Update `README.md` if you add new major routes. If you add new dependencies, update `requirements.txt`.

## Disclaimer
This project is intentionally insecure. Do not deploy to any public or production network. Always use isolated environments for testing.
