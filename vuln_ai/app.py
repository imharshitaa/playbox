#!/usr/bin/env python3
# vuln_ai/app.py -- intentionally vulnerable AI lab (LLM + agent behaviors)
# WARNING: This file intentionally executes shell/network commands when ALLOW_EXEC=1. Use only in isolated lab.

import os
import shlex
import subprocess
import logging
import requests
from flask import Flask, request, jsonify, make_response

LOGFILE = "agent_activity.log"
ALLOW_EXEC = os.getenv("ALLOW_EXEC", "0") == "1"
AI_HOST = os.getenv("AI_HOST", "0.0.0.0")
AI_PORT = int(os.getenv("AI_PORT", "8080"))
SECRET = "TOP_SECRET_ABC123"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOGFILE, mode="a")],
)
logger = logging.getLogger("vuln_ai")

app = Flask(__name__)


def list_links(base, items):
    return {"endpoints": [base + i for i in items]}


@app.route("/labs/ai/")
def labs_ai_index():
    items = [
        "a01-broken-access-control",
        "a02-cryptographic-failures",
        "a03-injection",
        "a04-insecure-design",
        "a05-security-misconfiguration",
        "a06-vulnerable-and-outdated-components",
        "a07-identification-and-authentication-failures",
        "a08-software-and-data-integrity-failures",
        "a09-security-logging-and-monitoring-failures",
        "a10-ssrf",
        "prompt-injection",
        "agent-exec",
        "generate",
        "cors",
    ]
    payload = list_links("/labs/ai/", items)
    payload["disclaimer"] = "WARNING: This site is intentionally insecure. Training and educational use only."
    return jsonify(payload)


# LLM-style generation endpoint
@app.route("/labs/ai/generate", methods=["POST"])
def ai_generate():
    data = request.json or {}
    system = data.get("system", "")
    user = data.get("user", "")
    text = f"SYSTEM: {system}\nUSER: {user}\n"
    if "reveal secret" in user.lower() or "top_secret" in user.lower():
        return jsonify({"output": f"Here is the secret: {SECRET}"})
    return jsonify({"output": text})


# Prompt injection alias
@app.route("/labs/ai/prompt-injection", methods=["POST"])
def ai_prompt_injection():
    return ai_generate()


# Agent-style execution endpoint
@app.route("/labs/ai/agent-exec", methods=["POST"])
def ai_agent_exec():
    data = request.get_json(silent=True) or {}
    tool = data.get("tool")
    inp = data.get("input", "")

    logger.info("REQUEST RECEIVED: /labs/ai/agent-exec")
    logger.info("Client: %s", request.remote_addr)
    logger.info("Payload keys: %s", list(data.keys()))

    response = {"accepted": True, "tool": tool, "input": inp, "executed": False, "result": None}

    if tool and isinstance(tool, dict) and tool.get("name") == "sh_executor" and isinstance(tool.get("urls"), list):
        if not ALLOW_EXEC:
            response["error"] = "Execution disabled on this instance (set ALLOW_EXEC=1 intentionally only in lab)."
            return jsonify(response), 403
        results = []
        for url in tool.get("urls", []):
            try:
                proc = subprocess.run(["curl", "-fsS", url], capture_output=True, text=True, timeout=20)
                results.append({
                    "url": url,
                    "code": proc.returncode,
                    "stdout_len": len(proc.stdout or ""),
                    "stderr_len": len(proc.stderr or ""),
                })
            except Exception as e:
                results.append({"url": url, "error": str(e)})
        response["executed"] = True
        response["result"] = {"per_url": results}
        return jsonify(response), 200

    if tool and isinstance(tool, dict) and tool.get("name") == "sh_executor" and isinstance(tool.get("args"), list):
        if not ALLOW_EXEC:
            response["error"] = "Execution disabled on this instance (set ALLOW_EXEC=1 intentionally only in lab)."
            return jsonify(response), 403
        args = tool.get("args", [])
        try:
            proc = subprocess.run(args, capture_output=True, text=True, timeout=20)
            response["executed"] = True
            response["result"] = {"code": proc.returncode, "stdout": proc.stdout[:2000], "stderr": proc.stderr[:2000]}
        except Exception as e:
            response["error"] = str(e)
        return jsonify(response), 200

    return jsonify(response), 200


# OWASP Top 10 (2021) style AI labs

@app.route("/labs/ai/a01-broken-access-control")
def ai_a01_broken_access_control():
    convo_id = request.args.get("id", "1")
    return jsonify({"convo_id": convo_id, "messages": ["user secret", "assistant secret"]})


@app.route("/labs/ai/a02-cryptographic-failures")
def ai_a02_crypto_failures():
    key = request.args.get("key", "ai-api-key")
    return jsonify({"api_key_plaintext": key})


@app.route("/labs/ai/a03-injection", methods=["POST"])
def ai_a03_injection():
    return ai_generate()


@app.route("/labs/ai/a04-insecure-design", methods=["POST"])
def ai_a04_insecure_design():
    data = request.json or {}
    return jsonify({"allowed_tool_call": data.get("tool"), "verified": False})


@app.route("/labs/ai/a05-security-misconfiguration")
def ai_a05_security_misconfig():
    return jsonify({"debug": True, "env": dict(os.environ)})


@app.route("/labs/ai/a06-vulnerable-and-outdated-components")
def ai_a06_outdated():
    return jsonify({"model": "gpt-2", "tokenizer": "old-tokenizer", "note": "intentionally outdated"})


@app.route("/labs/ai/a07-identification-and-authentication-failures", methods=["POST"])
def ai_a07_auth_failures():
    data = request.json or {}
    if data.get("api_key"):
        return jsonify({"ok": True, "note": "no real verification"})
    return jsonify({"ok": False}), 401


@app.route("/labs/ai/a08-software-and-data-integrity-failures", methods=["POST"])
def ai_a08_integrity_failures():
    data = request.json or {}
    url = data.get("weights_url")
    if url:
        try:
            r = requests.get(url, timeout=3)
            return jsonify({"downloaded": True, "bytes": len(r.content)})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"downloaded": False, "note": "no verification"})


@app.route("/labs/ai/a09-security-logging-and-monitoring-failures", methods=["POST"])
def ai_a09_logging_failures():
    return jsonify({"logged": False, "alerted": False})


@app.route("/labs/ai/a10-ssrf")
def ai_a10_ssrf():
    url = request.args.get("url", "http://example.com")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"url": url, "status": r.status_code, "len": len(r.text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/ai/cors")
def ai_cors():
    resp = make_response(jsonify({"secret": "ai-cors-secret"}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


if __name__ == "__main__":
    logger.info("Starting vulnerable AI lab on %s:%s ALLOW_EXEC=%s", AI_HOST, AI_PORT, ALLOW_EXEC)
    app.run(host=AI_HOST, port=AI_PORT, debug=True)
