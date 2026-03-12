# vuln_cloud/app.py -- intentionally vulnerable cloud lab API
import os
import requests
from flask import Flask, request, jsonify, make_response

APP_HOST = "0.0.0.0"
APP_PORT = 9100

app = Flask(__name__)


def list_links(base, items):
    return {"endpoints": [base + i for i in items]}


@app.route("/labs/cloud/")
def labs_cloud_index():
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
        "policy",
        "metadata",
        "cors",
    ]
    payload = list_links("/labs/cloud/", items)
    payload["disclaimer"] = "WARNING: This site is intentionally insecure. Training and educational use only."
    return jsonify(payload)


@app.route("/labs/cloud/a01-broken-access-control")
def cloud_a01_broken_access_control():
    return jsonify({"buckets": ["public-data", "prod-backups"], "note": "no auth required"})


@app.route("/labs/cloud/a02-cryptographic-failures")
def cloud_a02_crypto_failures():
    secret = request.args.get("secret", "cloud-secret")
    return jsonify({"plaintext_secret": secret})


@app.route("/labs/cloud/a03-injection")
def cloud_a03_injection():
    name = request.args.get("bucket", "logs")
    # naive string interpolation into a fake command string
    return jsonify({"cmd": f"mc ls {name}", "note": "no sanitization"})


@app.route("/labs/cloud/a04-insecure-design", methods=["POST"])
def cloud_a04_insecure_design():
    data = request.json or {}
    return jsonify({"bucket": data.get("bucket", "new-bucket"), "public": True})


@app.route("/labs/cloud/a05-security-misconfiguration")
def cloud_a05_security_misconfig():
    return jsonify({
        "minio_user": os.getenv("MINIO_ROOT_USER", "minioadmin"),
        "minio_password": os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
        "cors": "*",
    })


@app.route("/labs/cloud/a06-vulnerable-and-outdated-components")
def cloud_a06_outdated():
    return jsonify({"minio": "old", "note": "intentionally outdated"})


@app.route("/labs/cloud/a07-identification-and-authentication-failures")
def cloud_a07_auth_failures():
    key = request.headers.get("X-Access-Key")
    if key:
        return jsonify({"ok": True, "note": "key not verified"})
    return jsonify({"ok": False}), 401


@app.route("/labs/cloud/a08-software-and-data-integrity-failures", methods=["POST"])
def cloud_a08_integrity_failures():
    data = request.json or {}
    return jsonify({"policy": data.get("policy"), "verified": False})


@app.route("/labs/cloud/a09-security-logging-and-monitoring-failures", methods=["POST"])
def cloud_a09_logging_failures():
    return jsonify({"logged": False, "alerted": False})


@app.route("/labs/cloud/a10-ssrf")
def cloud_a10_ssrf():
    url = request.args.get("url", "http://169.254.169.254/latest/meta-data/")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"url": url, "status": r.status_code, "len": len(r.text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/cloud/policy", methods=["POST"])
def cloud_policy():
    data = request.json or {}
    return jsonify({"accepted": True, "policy": data, "validated": False})


@app.route("/labs/cloud/metadata")
def cloud_metadata():
    url = request.args.get("url", "http://169.254.169.254/latest/meta-data/")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"url": url, "status": r.status_code, "body": r.text[:2000]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/cloud/cors")
def cloud_cors():
    resp = make_response(jsonify({"secret": "cloud-cors-secret"}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
