# Vulnerable Lab Environment

⚠️ WARNING: This project is intentionally insecure. It is for learning, training, and testing only. Run inside an isolated VM or an offline Docker host. Do not expose these services to the internet or production networks.

About: 
"vuln-input" repo is a collection of simple, intentionally vulnerable applications and services.
They are grouped by domain (web, API, LLM, network, cloud) and packaged with Docker for easy setup.

Repo Contents ->
- web/ → Minimal Flask website (basic OWASP web issues).
- apis/ → Small REST API (SQLi, IDOR, weak auth).
- llm/ → Mock LLM service (prompt injection playground).
- network/ → Tiny TCP server (unsafe message framing).
- cloud/ → MinIO service with an insecure policy (study-only).
- payloads/ → Example payload files (just text/json snippets).
- docker-compose.yml → Starts the main services (web, api, llm, tcp).
- README.md → You are reading this.

Tech Used ->
1. Python 3.11 with: - Flask (web + API) - FastAPI + Uvicorn (LLM) - SQLite (API DB)
2. MinIO (S3-like object storage)
3. Docker & Docker Compose for setup
4. Netcat (nc) or Python (for TCP client testing)

| Service | Domain   | Port | URL / Address                                  |
| ------- | -------- | ---- | ---------------------------------------------- |
| `web`   | Website  | 8000 | [http://localhost:8000](http://localhost:8000) |
| `api`   | REST API | 5000 | [http://localhost:5000](http://localhost:5000) |
| `llm`   | Mock LLM | 8080 | [http://localhost:8080](http://localhost:8080) |
| `tcp`   | Network  | 9001 | tcp\://localhost:9001                          |
| `cloud` | MinIO    | 9000 | [http://localhost:9000](http://localhost:9000) |


SETUP
-

Quick start:

- build and start everything (web, api, llm, tcp)
`docker compose up --build -d`

- check running containers
`docker compose ps`

- stop all
`docker compose down`

## Domain based Setup:

1. WEB
```
cd web
docker build -t vuln-web .
docker run -d --rm -p 8000:8000 --name vuln-web vuln-web
docker stop vuln-web
```
2. API
```
cd apis
docker build -t vuln-api .
docker run -d --rm -p 5000:5000 --name vuln-api vuln-api
docker stop vuln-api
```
3. LLM
```
cd llm
docker build -t vuln-llm .
docker run -d --rm -p 8080:8080 --name vuln-llm vuln-llm
docker stop vuln-llm
```
4. CLOUD
```
cd cloud
docker compose up -d
docker compose down
```
- Web console: http://localhost:9000
- Default user: minioadmin
- Default password: minioadmin

5. NETWORK
```
cd network
docker build -t vuln-tcp .
docker run -d --rm -p 9001:9001 --name vuln-tcp vuln-tcp
docker stop vuln-tcp
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
(18000:8000)































