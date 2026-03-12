# Vulnerable Lab Environment

⚠️ WARNING: This project is intentionally insecure. It is for learning, training, and testing only. Run inside an isolated VM or an offline Docker host. Do not expose these services to the internet or production networks.

About:
"playbox" repo is a collection of simple, intentionally vulnerable applications and services.
They are grouped by domain (web, API, AI, network, cloud) and packaged with Docker for easy setup.

Repo Contents ->
- gateway/ → Nginx reverse proxy for unified lab URLs
- vuln_webapp/ → Minimal Flask website (basic OWASP web issues)
- vuln_api/ → Small REST API (SQLi, IDOR, weak auth)
- vuln_ai/ → AI lab (LLM + agent behaviors)
- vuln_network/ → TCP server + HTTP network lab endpoints
- vuln_cloud/ → Cloud lab API + MinIO (insecure policy examples)
- payloads → Placeholder payload file
- docker-compose.yml → Starts all services
- README.md → You are reading this

Tech Used ->
1. Python 3.11 with: - Flask (web + API + AI + network + cloud) - SQLite (web + API DB)
2. MinIO (S3-like object storage)
3. Docker & Docker Compose for setup
4. Netcat (nc) or Python (for TCP client testing)

Unified Gateway URLs (path-based on localhost):
- http://localhost/labs/web/
- http://localhost/labs/api/
- http://localhost/labs/ai/
- http://localhost/labs/network/
- http://localhost/labs/cloud/

Tip: to use `http://playbox/...` locally, add `127.0.0.1 playbox` to your hosts file.

Service Ports (direct access):
- web: 8000
- api: 5000
- ai: 8080
- network tcp: 9001
- network http: 9101
- cloud app: 9100
- minio: 9000

SETUP
-

Quick start:

- build and start everything
`docker compose up --build -d`

- check running containers
`docker compose ps`

- stop all
`docker compose down`

OWASP Top 10 (2021) Lab Endpoints
-
Each lab has endpoints for the OWASP Top 10 (2021) categories plus a few extras.
Examples:
- Web SQLi: http://localhost/labs/web/sqli
- Web CORS: http://localhost/labs/web/cors
- API SQLi: http://localhost/labs/api/sqli
- AI prompt injection: http://localhost/labs/ai/prompt-injection
- Network unsafe length: http://localhost/labs/network/unsafe-length
- Cloud metadata SSRF: http://localhost/labs/cloud/metadata

Domain-based Setup (optional):

1. WEB
```
cd vuln_webapp
docker build -t vuln-web .
docker run -d --rm -p 8000:8000 --name vuln-web vuln-web
docker stop vuln-web
```

2. API
```
cd vuln_api
docker build -t vuln-api .
docker run -d --rm -p 5000:5000 --name vuln-api vuln-api
docker stop vuln-api
```

3. AI
```
cd vuln_ai
docker build -t vuln-ai .
docker run -d --rm -p 8080:8080 --name vuln-ai vuln-ai
docker stop vuln-ai
```

4. CLOUD
```
cd vuln_cloud
docker build -t vuln-cloud .
docker run -d --rm -p 9100:9100 --name vuln-cloud vuln-cloud
# MinIO separately via docker compose
cd ..
docker compose up -d minio
```

5. NETWORK
```
cd vuln_network
docker build -t vuln-network .
docker run -d --rm -p 9001:9001 -p 9101:9101 --name vuln-network vuln-network
docker stop vuln-network
```

TIPS:

- run from repo root to start all at once
`docker compose up --build -d`

- use to see running containers
`docker ps`

- use to view logs
`docker logs <container-name>`

- stop everything
`docker compose down`

- port conflicts: change left side of mapping in docker-compose file
(18080:8080)
