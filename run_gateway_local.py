#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.error
import os

PORT = int(os.getenv("PORT", "8081"))

ROUTES = {
    "/labs/web/": "http://localhost:8000/",
    "/labs/api/": "http://localhost:5000/",
    "/labs/ai/": "http://localhost:8080/",
    "/labs/network/": "http://localhost:9101/",
    "/labs/cloud/": "http://localhost:9100/",
}


class Proxy(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def _proxy(self):
        target = None
        for prefix, base in ROUTES.items():
            if self.path.startswith(prefix):
                target = base + self.path[len(prefix):]
                break

        if self.path == "/labs/" or self.path == "/labs":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Playbox Vulnerable Labs\nWARNING: This site is intentionally insecure. Training and educational use only.\nUse /labs/web/, /labs/api/, /labs/ai/, /labs/network/, /labs/cloud/\n")
            return

        if not target:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Playbox Vulnerable Labs\nWARNING: This site is intentionally insecure. Training and educational use only.\nUse /labs/web/, /labs/api/, /labs/ai/, /labs/network/, /labs/cloud/\n")
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else None
        req = urllib.request.Request(target, data=body, method=self.command)

        for k, v in self.headers.items():
            if k.lower() == "host":
                continue
            req.add_header(k, v)

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(e.read() or str(e).encode())
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(str(e).encode())


if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), Proxy) as httpd:
        print(f"Playbox local gateway running on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
