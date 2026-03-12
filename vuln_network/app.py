# vuln_network/app.py -- HTTP wrapper for network labs + starts TCP server
import os
import threading
import subprocess
import requests
from flask import Flask, request, jsonify, make_response
from tcp_server import start_tcp_server

APP_HOST = "0.0.0.0"
APP_PORT = 9101

app = Flask(__name__)


def list_links(base, items):
    return {"endpoints": [base + i for i in items]}


@app.route("/labs/network/")
def labs_network_index():
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
        "unsafe-length",
        "tcp-info",
        "cors",
    ]
    payload = list_links("/labs/network/", items)
    payload["disclaimer"] = "WARNING: This site is intentionally insecure. Training and educational use only."
    return jsonify(payload)


@app.route("/labs/network/tcp-info")
def tcp_info():
    return jsonify({"tcp_host": "0.0.0.0", "tcp_port": 9001, "note": "Use TCP client with 4-byte length header."})


@app.route("/labs/network/unsafe-length")
def unsafe_length():
    n = int(request.args.get("n", "1024"))
    # intentionally unsafe allocation
    data = bytearray(n)
    return jsonify({"allocated": n, "sample": len(data)})


@app.route("/labs/network/a01-broken-access-control")
def net_a01_broken_access_control():
    return jsonify({"admin_config": {"allow_any": True, "internal": "exposed"}})


@app.route("/labs/network/a02-cryptographic-failures")
def net_a02_crypto_failures():
    msg = request.args.get("msg", "hello")
    key = request.args.get("key", "k")
    # weak XOR
    enc = "".join([chr(ord(c) ^ ord(key[0])) for c in msg])
    return jsonify({"plaintext": msg, "xor": enc})


@app.route("/labs/network/a03-injection")
def net_a03_injection():
    cmd = request.args.get("cmd", "id")
    try:
        out = subprocess.check_output(cmd, shell=True, text=True, timeout=3)
        return jsonify({"cmd": cmd, "output": out[:2000]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/network/a04-insecure-design")
def net_a04_insecure_design():
    role = request.headers.get("X-Role", "user")
    return jsonify({"role": role, "authorized": True})


@app.route("/labs/network/a05-security-misconfiguration")
def net_a05_security_misconfig():
    resp = make_response(jsonify({"debug": True, "env": dict(os.environ)}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


@app.route("/labs/network/a06-vulnerable-and-outdated-components")
def net_a06_outdated():
    return jsonify({"openssl": "1.0.1", "note": "intentionally outdated"})


@app.route("/labs/network/a07-identification-and-authentication-failures")
def net_a07_auth_failures():
    token = request.headers.get("Authorization")
    if token:
        return jsonify({"ok": True, "note": "token not verified"})
    return jsonify({"ok": False}), 401


@app.route("/labs/network/a08-software-and-data-integrity-failures")
def net_a08_integrity_failures():
    url = request.args.get("url", "http://example.com")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"downloaded": True, "bytes": len(r.content), "verified": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/network/a09-security-logging-and-monitoring-failures", methods=["POST"])
def net_a09_logging_failures():
    return jsonify({"logged": False, "alerted": False})


@app.route("/labs/network/a10-ssrf")
def net_a10_ssrf():
    url = request.args.get("url", "http://example.com")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"url": url, "status": r.status_code, "len": len(r.text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/network/cors")
def net_cors():
    resp = make_response(jsonify({"secret": "network-cors-secret"}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


if __name__ == "__main__":
    t = threading.Thread(target=start_tcp_server, daemon=True)
    t.start()
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
