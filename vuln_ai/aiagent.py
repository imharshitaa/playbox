#!/usr/bin/env python3
# vulnagent.py  (LAB ONLY) - intentionally vulnerable agent endpoint with multi-URL support + logging
# WARNING: This file intentionally executes shell/network commands when ALLOW_EXEC=1. Use only in isolated lab.

import os
import shlex
import subprocess
import re
import logging
from flask import Flask, request, jsonify

# --- configuration ---------------------------------------------------------
LOGFILE = "agent_activity.log"
ALLOW_EXEC = os.getenv("ALLOW_EXEC", "0") == "1"
AGENT_HOST = os.getenv("AGENT_HOST", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "9000"))
# -------------------------------------------------------------------------

# logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGFILE, mode="a"),
    ],
)
logger = logging.getLogger("vulnagent")

app = Flask(__name__)

def safe_join_preview(s: str, n=200):
    if not s:
        return ""
    return (s[:n] + "...") if len(s) > n else s

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True) or {}
    tool = data.get("tool")
    inp = data.get("input", "")

    # header logs (4-6 lines per request)
    logger.info("REQUEST RECEIVED: /execute")
    logger.info("Client: %s", request.remote_addr)
    logger.info("Payload keys: %s", list(data.keys()))
    logger.info("Parsed input preview: %s", safe_join_preview(inp))

    response = {"accepted": True, "tool": tool, "input": inp, "executed": False, "result": None}

    # New: support {"tool": {"name":"sh_executor", "urls": ["http://...", ...]}}
    if tool and isinstance(tool, dict) and tool.get("name") == "sh_executor" and isinstance(tool.get("urls"), list):
        logger.info("BRANCH: tool execution with multiple URLs")
        if not ALLOW_EXEC:
            logger.warning("Execution disabled (ALLOW_EXEC=0). Rejecting execution.")
            response["error"] = "Execution disabled on this instance (set ALLOW_EXEC=1 intentionally only in lab)."
            return jsonify(response), 403

        results = []
        for url in tool.get("urls", []):
            logger.info("Invoking CURL for URL: %s", url)
            try:
                proc = subprocess.run(["curl", "-fsS", url], capture_output=True, text=True, timeout=20)
                results.append({
                    "url": url,
                    "code": proc.returncode,
                    "stdout_len": len(proc.stdout or ""),
                    "stderr_len": len(proc.stderr or "")
                })
                logger.info("CURL result: url=%s code=%s stdout_len=%s", url, proc.returncode, len(proc.stdout or ""))
            except Exception as e:
                results.append({"url": url, "error": str(e)})
                logger.exception("CURL invocation failed for %s", url)

        response["executed"] = True
        response["result"] = {"per_url": results}
        logger.info("---- end request ----")
        return jsonify(response), 200

    # Legacy: existing sh_executor via args (unchanged)
    if tool and isinstance(tool, dict) and tool.get("name") == "sh_executor" and isinstance(tool.get("args"), list):
        logger.info("BRANCH: tool execution via args")
        if not ALLOW_EXEC:
            logger.warning("Execution disabled (ALLOW_EXEC=0). Rejecting execution.")
            response["error"] = "Execution disabled on this instance (set ALLOW_EXEC=1 intentionally only in lab)."
            return jsonify(response), 403
        args = tool.get("args", [])
        logger.info("Executing command: %s", " ".join(shlex.quote(a) for a in args))
        try:
            proc = subprocess.run(args, capture_output=True, text=True, timeout=20)
            response["executed"] = True
            response["result"] = {"code": proc.returncode, "stdout": proc.stdout[:2000], "stderr": proc.stderr[:2000]}
            logger.info("Execution finished: returncode=%s stdout_len=%d", proc.returncode, len(proc.stdout or ""))
            logger.info("---- end request ----")
        except Exception as e:
            response["error"] = str(e)
            logger.exception("Execution failed")
        return jsonify(response), 200

    # If input contains "Fetch http://..." pattern, simulate a tool invocation by running curl (if ALLOW_EXEC)
    m = re.search(r"(https?://[^\s]+)", inp)
    if m:
        url = m.group(1)
        logger.info("BRANCH: input contains URL -> %s", url)
        if not ALLOW_EXEC:
            logger.warning("Execution disabled (ALLOW_EXEC=0). Rejecting execution.")
            response["error"] = "Execution disabled on this instance (set ALLOW_EXEC=1 intentionally only in lab)."
            return jsonify(response), 403
        logger.info("Invoking curl to fetch URL: %s", url)
        try:
            proc = subprocess.run(["curl", "-fsS", url], capture_output=True, text=True, timeout=20)
            response["executed"] = True
            response["result"] = {"code": proc.returncode, "stdout_len": len(proc.stdout or "")}
            logger.info("Curl finished: returncode=%s stdout_len=%d", proc.returncode, len(proc.stdout or ""))
            logger.info("---- end request ----")
        except Exception as e:
            response["error"] = str(e)
            logger.exception("Curl invocation failed")
        return jsonify(response), 200

    # Otherwise just echo / store
    logger.info("BRANCH: echo/default (no tool/url found).")
    logger.info("---- end request ----")
    return jsonify(response), 200

if __name__ == "__main__":
    logger.info("Starting vulnerable agent (lab only) on %s:%s ALLOW_EXEC=%s", AGENT_HOST, AGENT_PORT, ALLOW_EXEC)
    app.run(host=AGENT_HOST, port=AGENT_PORT)
