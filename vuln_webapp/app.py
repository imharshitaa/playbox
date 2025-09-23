# Note: these apps are intentionally insecure — run inside an isolated VM or an offline Docker host only.
from flask import Flask, request, render_template_string, send_from_directory, redirect
import os

app = Flask(__name__)
UPLOAD_DIR = "/tmp/vuln_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# index + reflected XSS example
@app.route("/")
def index():
    name = request.args.get("name", "")
    # reflected XSS: user content inserted unsafely
    return render_template_string("<h1>Welcome</h1><p>Hello, %s</p><form><input name='name'><button>Go</button></form>" % name)

# stored XSS (very simple; stored in file)
@app.route("/comment", methods=["GET","POST"])
def comment():
    file = "/tmp/comments.txt"
    if request.method == "POST":
        c = request.form.get("comment","")
        with open(file, "a") as f:
            f.write(c + "\n")
        return redirect("/comment")
    comments = ""
    if os.path.exists(file):
        comments = open(file).read()
    return render_template_string("""
    <h2>Leave comment</h2>
    <form method=post><textarea name=comment></textarea><button>Post</button></form>
    <h3>All comments</h3><pre>%s</pre>""" % comments)

# insecure file download - path traversal vulnerable
@app.route("/download")
def download():
    fname = request.args.get("file","example.txt")
    # intentionally insecure: no sanitization
    return send_from_directory("/", fname, as_attachment=True)

# insecure upload (no checks)
@app.route("/upload", methods=["GET","POST"])
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
