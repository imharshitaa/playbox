# apis/api.py -- intentionally insecure demo API
from flask import Flask, request, jsonify, make_response
import sqlite3
import os
import requests
import base64
import hashlib

DB = '/tmp/api_lab.db'


def init_db():
    if os.path.exists(DB):
        return
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, secret TEXT)")
    c.execute("INSERT INTO users(username,password,secret) VALUES('alice','pass','ALICE_SECRET')")
    c.execute("INSERT INTO users(username,password,secret) VALUES('bob','word','BOB_SECRET')")
    conn.commit()
    conn.close()


def unsafe_query(sql):
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(sql)
    rows = c.fetchall()
    conn.close()
    return rows


app = Flask(__name__)

# weak login (no rate limit, simple check)
@app.route("/login", methods=["POST"])
def login():
    d = request.json or {}
    u = d.get("username", "")
    p = d.get("password", "")
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # vulnerable to SQL injection (unsafe string concat)
    q = "SELECT id,username FROM users WHERE username='%s' AND password='%s'" % (u, p)
    try:
        c.execute(q)
        r = c.fetchone()
    except Exception as e:
        return {"error": str(e)}, 400
    if r:
        return {"token": f"token-for-{r[0]}"}
    return {"error": "invalid"}, 401


# IDOR: any user id accessible without auth checks
@app.route("/users/<uid>")
def user(uid):
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id,username,secret FROM users WHERE id=?", (uid,))
    r = c.fetchone()
    if r:
        return jsonify({"id": r[0], "username": r[1], "secret": r[2]})
    return {"error": "not found"}, 404


# search endpoint - vulnerable to naive SQLi
@app.route("/search")
def search():
    q = request.args.get("q", "")
    init_db()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # vulnerable - concatenation
    sql = "SELECT id,username FROM users WHERE username LIKE '%%%s%%'" % (q)
    try:
        c.execute(sql)
        rows = c.fetchall()
    except Exception as e:
        return {"error": str(e)}, 400
    return jsonify([{"id": r[0], "username": r[1]} for r in rows])


# --- OWASP Top 10 (2021) lab routes ---------------------------------------

@app.route("/labs/api/")
def labs_api_index():
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
        "sqli",
        "cors",
        "idor",
    ]
    return jsonify({"disclaimer": "WARNING: This site is intentionally insecure. Training and educational use only.", "endpoints": ["/labs/api/" + i for i in items]})


@app.route("/labs/api/a01-broken-access-control")
def api_a01_broken_access_control():
    uid = request.args.get("id", "1")
    rows = unsafe_query("SELECT id, username, secret FROM users WHERE id=%s" % uid)
    if rows:
        r = rows[0]
        return jsonify({"id": r[0], "username": r[1], "secret": r[2]})
    return jsonify({"error": "not found"}), 404


@app.route("/labs/api/a02-cryptographic-failures")
def api_a02_crypto_failures():
    pwd = request.args.get("password", "password123")
    weak = hashlib.md5(pwd.encode()).hexdigest()
    encoded = base64.b64encode(pwd.encode()).decode()
    return jsonify({"plaintext": pwd, "md5": weak, "base64": encoded})


@app.route("/labs/api/a03-injection")
def api_a03_injection():
    q = request.args.get("q", "")
    sql = "SELECT id, username FROM users WHERE username LIKE '%%%s%%'" % q
    rows = unsafe_query(sql)
    return jsonify([{"id": r[0], "username": r[1]} for r in rows])


@app.route("/labs/api/a04-insecure-design", methods=["POST"])
def api_a04_insecure_design():
    user = (request.json or {}).get("user", "alice")
    return jsonify({"reset": "ok", "user": user, "note": "no verification performed"})


@app.route("/labs/api/a05-security-misconfiguration")
def api_a05_security_misconfig():
    return jsonify({
        "debug": True,
        "env": dict(os.environ),
        "allowed_hosts": "*",
    })


@app.route("/labs/api/a06-vulnerable-and-outdated-components")
def api_a06_outdated():
    return jsonify({
        "server": "Werkzeug/0.16",
        "library": "flask 1.0",
        "note": "intentionally outdated demo info",
    })


@app.route("/labs/api/a07-identification-and-authentication-failures", methods=["POST"])
def api_a07_auth_failures():
    d = request.json or {}
    u = d.get("username", "")
    p = d.get("password", "")
    if u and p:
        return jsonify({"login": "ok", "user": u})
    return jsonify({"error": "invalid"}), 401


@app.route("/labs/api/a08-software-and-data-integrity-failures", methods=["POST"])
def api_a08_integrity_failures():
    d = request.json or {}
    return jsonify({"accepted": True, "data": d.get("data"), "sig": d.get("sig"), "verified": False})


@app.route("/labs/api/a09-security-logging-and-monitoring-failures", methods=["POST"])
def api_a09_logging_failures():
    return jsonify({"status": "failed", "logged": False})


@app.route("/labs/api/a10-ssrf")
def api_a10_ssrf():
    url = request.args.get("url", "http://example.com")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"url": url, "status": r.status_code, "len": len(r.text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/api/sqli")
def api_sqli():
    user = request.args.get("user", "")
    sql = "SELECT id, username FROM users WHERE username='%s'" % user
    rows = unsafe_query(sql)
    return jsonify([{"id": r[0], "username": r[1]} for r in rows])


@app.route("/labs/api/cors")
def api_cors():
    resp = make_response(jsonify({"secret": "api-cors-secret"}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


@app.route("/labs/api/idor")
def api_idor():
    uid = request.args.get("id", "1")
    rows = unsafe_query("SELECT id, username, secret FROM users WHERE id=%s" % uid)
    if rows:
        r = rows[0]
        return jsonify({"id": r[0], "username": r[1], "secret": r[2]})
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
