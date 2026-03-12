# Note: these apps are intentionally insecure — run inside an isolated VM or an offline Docker host only.
from flask import Flask, request, render_template_string, send_from_directory, redirect, jsonify, make_response
import os
import sqlite3
import hashlib
import base64
import requests

app = Flask(__name__)
UPLOAD_DIR = "/tmp/vuln_uploads"
WEB_DB = "/tmp/web_lab.db"
COMMENTS_FILE = "/tmp/comments.txt"
CSRF_STATE_FILE = "/tmp/csrf_state.txt"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- helpers ---------------------------------------------------------------

def init_db():
    if os.path.exists(WEB_DB):
        return
    conn = sqlite3.connect(WEB_DB)
    c = conn.cursor()
    c.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, secret TEXT)")
    c.execute("INSERT INTO users(username,password,secret) VALUES('alice','pass','ALICE_WEB_SECRET')")
    c.execute("INSERT INTO users(username,password,secret) VALUES('bob','word','BOB_WEB_SECRET')")
    conn.commit()
    conn.close()


def unsafe_query(sql):
    init_db()
    conn = sqlite3.connect(WEB_DB)
    c = conn.cursor()
    c.execute(sql)
    rows = c.fetchall()
    conn.close()
    return rows


def list_links(base, items):
    links = "".join([f"<li><a href='{base}{i}'>{i}</a></li>" for i in items])
    return f"<ul>{links}</ul>"


# --- legacy routes ---------------------------------------------------------

# index + reflected XSS example
@app.route("/")
def index():
    name = request.args.get("name", "")
    # reflected XSS: user content inserted unsafely
    return render_template_string("<h1>Welcome</h1><p>Hello, %s</p><form><input name='name'><button>Go</button></form>" % name)


# stored XSS (very simple; stored in file)
@app.route("/comment", methods=["GET", "POST"])
def comment():
    if request.method == "POST":
        c = request.form.get("comment", "")
        with open(COMMENTS_FILE, "a") as f:
            f.write(c + "\n")
        return redirect("/comment")
    comments = ""
    if os.path.exists(COMMENTS_FILE):
        comments = open(COMMENTS_FILE).read()
    return render_template_string(
        """
    <h2>Leave comment</h2>
    <form method=post><textarea name=comment></textarea><button>Post</button></form>
    <h3>All comments</h3><pre>%s</pre>""" % comments
    )


# insecure file download - path traversal vulnerable
@app.route("/download")
def download():
    fname = request.args.get("file", "example.txt")
    # intentionally insecure: no sanitization
    return send_from_directory("/", fname, as_attachment=True)


# insecure upload (no checks)
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            path = os.path.join(UPLOAD_DIR, f.filename)
            f.save(path)
            return "saved: " + path
    return """
    <form method='post' enctype='multipart/form-data'>
      <input type='file' name='file'>
      <button>Upload</button>
    </form>
    """


# --- OWASP Top 10 (2021) lab routes ---------------------------------------

@app.route("/labs/web/")
def labs_web_index():
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
        "xss",
        "csrf",
        "cors",
        "idor",
        "path-traversal",
        "file-upload",
        "open-redirect",
    ]
    return "<h1>Web Labs</h1>" + list_links("/labs/web/", items)


@app.route("/labs/web/a01-broken-access-control")
def a01_broken_access_control():
    uid = request.args.get("id", "1")
    rows = unsafe_query("SELECT id, username, secret FROM users WHERE id=%s" % uid)
    if rows:
        r = rows[0]
        return jsonify({"id": r[0], "username": r[1], "secret": r[2]})
    return jsonify({"error": "not found"}), 404


@app.route("/labs/web/a02-cryptographic-failures")
def a02_crypto_failures():
    pwd = request.args.get("password", "password123")
    weak = hashlib.md5(pwd.encode()).hexdigest()
    encoded = base64.b64encode(pwd.encode()).decode()
    return jsonify({"plaintext": pwd, "md5": weak, "base64": encoded})


@app.route("/labs/web/a03-injection")
def a03_injection():
    q = request.args.get("q", "")
    sql = "SELECT id, username FROM users WHERE username LIKE '%%%s%%'" % q
    rows = unsafe_query(sql)
    return jsonify([{"id": r[0], "username": r[1]} for r in rows])


@app.route("/labs/web/a04-insecure-design", methods=["POST"])
def a04_insecure_design():
    user = request.form.get("user", "alice")
    # insecure design: no verification step for reset
    return jsonify({"reset": "ok", "user": user, "note": "no verification performed"})


@app.route("/labs/web/a05-security-misconfiguration")
def a05_security_misconfig():
    # exposes internal config and debug data
    return jsonify({
        "debug": True,
        "env": dict(os.environ),
        "allowed_hosts": "*",
    })


@app.route("/labs/web/a06-vulnerable-and-outdated-components")
def a06_outdated():
    return jsonify({
        "server": "Werkzeug/0.16",
        "library": "jquery 1.12.4",
        "note": "intentionally outdated demo info",
    })


@app.route("/labs/web/a07-identification-and-authentication-failures", methods=["POST"])
def a07_auth_failures():
    u = request.form.get("username", "")
    p = request.form.get("password", "")
    # weak auth: accepts any password length >= 1
    if u and p:
        return jsonify({"login": "ok", "user": u})
    return jsonify({"error": "invalid"}), 401


@app.route("/labs/web/a08-software-and-data-integrity-failures", methods=["POST"])
def a08_integrity_failures():
    data = request.form.get("data", "")
    sig = request.form.get("sig", "")
    # intentionally ignore signature
    return jsonify({"accepted": True, "data": data, "sig": sig, "verified": False})


@app.route("/labs/web/a09-security-logging-and-monitoring-failures", methods=["POST"])
def a09_logging_failures():
    # does not log or alert failed auth
    return jsonify({"status": "failed", "logged": False})


@app.route("/labs/web/a10-ssrf")
def a10_ssrf():
    url = request.args.get("url", "http://example.com")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"url": url, "status": r.status_code, "len": len(r.text)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/labs/web/sqli")
def web_sqli():
    user = request.args.get("user", "")
    sql = "SELECT id, username FROM users WHERE username='%s'" % user
    rows = unsafe_query(sql)
    return jsonify([{"id": r[0], "username": r[1]} for r in rows])


@app.route("/labs/web/xss")
def web_xss():
    payload = request.args.get("q", "")
    return render_template_string("<h2>Echo</h2><p>%s</p>" % payload)


@app.route("/labs/web/csrf")
def web_csrf():
    action = request.args.get("action", "transfer")
    with open(CSRF_STATE_FILE, "a") as f:
        f.write(action + "\n")
    return jsonify({"status": "ok", "action": action, "csrf": False})


@app.route("/labs/web/cors")
def web_cors():
    resp = make_response(jsonify({"secret": "web-cors-secret"}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


@app.route("/labs/web/idor")
def web_idor():
    uid = request.args.get("id", "1")
    rows = unsafe_query("SELECT id, username, secret FROM users WHERE id=%s" % uid)
    if rows:
        r = rows[0]
        return jsonify({"id": r[0], "username": r[1], "secret": r[2]})
    return jsonify({"error": "not found"}), 404


@app.route("/labs/web/path-traversal")
def web_path_traversal():
    fname = request.args.get("file", "etc/passwd")
    return send_from_directory("/", fname, as_attachment=False)


@app.route("/labs/web/file-upload", methods=["GET", "POST"])
def web_file_upload():
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            path = os.path.join(UPLOAD_DIR, f.filename)
            f.save(path)
            return "saved: " + path
    return """
    <form method='post' enctype='multipart/form-data'>
      <input type='file' name='file'>
      <button>Upload</button>
    </form>
    """


@app.route("/labs/web/open-redirect")
def web_open_redirect():
    target = request.args.get("next", "https://example.com")
    return redirect(target)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
