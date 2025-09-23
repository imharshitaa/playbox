# vuln-lab (simple junior-friendly vulnerable apps)

Note: these apps are intentionally insecure — run inside an isolated VM or an offline Docker host only.

## Quick start (isolated environment recommended)
# Build & run all
docker compose up --build -d

# Services after startup:
# Web (OWASP playground):  http://localhost:8000
# API (SQLi, IDOR):         http://localhost:5000
# Mock LLM:                 http://localhost:8080
# TCP service:              tcp://localhost:9001
# MinIO (cloud):            http://localhost:9000  (if you started cloud/minio)

## Quick test examples
# Web reflected XSS:
open "http://localhost:8000/?name=<script>alert(1)</script>"

# API SQLi test
curl "http://localhost:5000/search?q=%27%20OR%20%271%27%3D%271"

# LLM injection test
curl -s -X POST http://localhost:8080/generate -H "Content-Type: application/json" -d @payloads/llm_injection.json

# TCP malformed frame test
printf '\x00\x00\xff\xff' | nc localhost 9001

## Safety
- Run in an isolated VM or Docker host.
- Do not expose these services to the public internet.
