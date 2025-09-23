# apis/api.py -- intentionally insecure demo API
from flask import Flask, request, jsonify
import sqlite3, os

DB='users.db'
if not os.path.exists(DB):
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, secret TEXT)")
    c.execute("INSERT INTO users(username,password,secret) VALUES('alice','pass','ALICE_SECRET')")
    c.execute("INSERT INTO users(username,password,secret) VALUES('bob','word','BOB_SECRET')")
    conn.commit()
    conn.close()

app = Flask(__name__)

# weak login (no rate limit, simple check)
@app.route("/login", methods=["POST"])
def login():
    d=request.json or {}
    u=d.get("username","")
    p=d.get("password","")
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    # vulnerable to SQL injection (unsafe string concat)
    q = "SELECT id,username FROM users WHERE username='%s' AND password='%s'" % (u,p)
    try:
        c.execute(q)
        r=c.fetchone()
    except Exception as e:
        return {"error": str(e)},400
    if r:
        return {"token": f"token-for-{r[0]}"}
    return {"error":"invalid"},401

# IDOR: any user id accessible without auth checks
@app.route("/users/<uid>")
def user(uid):
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute("SELECT id,username,secret FROM users WHERE id=?", (uid,))
    r=c.fetchone()
    if r:
        return jsonify({"id":r[0],"username":r[1],"secret":r[2]})
    return {"error":"not found"},404

# search endpoint - vulnerable to naive SQLi
@app.route("/search")
def search():
    q = request.args.get("q","")
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    # vulnerable - concatenation
    sql = "SELECT id,username FROM users WHERE username LIKE '%%%s%%'" % (q)
    try:
        c.execute(sql)
        rows=c.fetchall()
    except Exception as e:
        return {"error":str(e)},400
    return jsonify([{"id":r[0],"username":r[1]} for r in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
