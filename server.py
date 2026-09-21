#!/usr/bin/env python3
"""Stdlib-only HTTP server for Seraphim Organizer — port 8777."""
from __future__ import annotations

import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from organize import organize_bytes, organize_payload  # noqa: E402

HOST = "127.0.0.1"
PORT = 8777


def _parse_multipart(body: bytes, content_type: str):
    """Minimal multipart/form-data parser (stdlib only)."""
    if "boundary=" not in content_type:
        raise ValueError("multipart missing boundary")
    boundary = content_type.split("boundary=", 1)[1].strip()
    if boundary.startswith('"') and boundary.endswith('"'):
        boundary = boundary[1:-1]
    sep = b"--" + boundary.encode("ascii", errors="ignore")
    parts = body.split(sep)
    files = {}
    fields = {}
    for part in parts:
        if not part or part in (b"--\r\n", b"--", b"--\r\n--"):
            continue
        if part.startswith(b"--"):
            continue
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if part == b"--" or part.endswith(b"--"):
            # closing
            if part.rstrip(b"-").strip() == b"":
                continue
            part = part.rstrip(b"-").rstrip(b"\r\n")
        header_blob, _, content = part.partition(b"\r\n\r\n")
        if not _:
            continue
        headers = {}
        for line in header_blob.decode("utf-8", errors="replace").split("\r\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()
        disp = headers.get("content-disposition", "")
        name = None
        filename = None
        for bit in disp.split(";"):
            bit = bit.strip()
            if bit.startswith("name="):
                name = bit[5:].strip().strip('"')
            elif bit.startswith("filename="):
                filename = bit[9:].strip().strip('"')
        # strip trailing CRLF that precedes next boundary
        if content.endswith(b"\r\n"):
            content = content[:-2]
        if name is None:
            continue
        if filename is not None:
            files[name] = {
                "filename": filename,
                "content": content,
                "content_type": headers.get("content-type", "application/octet-stream"),
            }
        else:
            fields[name] = content.decode("utf-8", errors="replace")
    return fields, files


class Handler(BaseHTTPRequestHandler):
    server_version = "SeraphimOrganizer/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = unquote(self.path.split("?", 1)[0])
        if path in ("/", "/index.html"):
            return self._file(ROOT / "index.html", "text/html; charset=utf-8")
        if path.startswith("/"):
            rel = path.lstrip("/")
            # prevent traversal
            if ".." in rel or rel.startswith("/"):
                return self._json(404, {"error": "not found"})
            target = (ROOT / rel).resolve()
            if not str(target).startswith(str(ROOT.resolve())):
                return self._json(403, {"error": "forbidden"})
            if target.is_file():
                ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
                if target.suffix in (".html", ".css", ".js", ".json", ".md", ".txt", ".csv"):
                    ctype = {
                        ".html": "text/html; charset=utf-8",
                        ".css": "text/css; charset=utf-8",
                        ".js": "application/javascript; charset=utf-8",
                        ".json": "application/json; charset=utf-8",
                        ".md": "text/markdown; charset=utf-8",
                        ".txt": "text/plain; charset=utf-8",
                        ".csv": "text/csv; charset=utf-8",
                    }.get(target.suffix, ctype)
                return self._file(target, ctype)
        return self._json(404, {"error": "not found"})

    def do_POST(self):
        path = unquote(self.path.split("?", 1)[0])
        if path != "/api/organize":
            return self._json(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        ctype = self.headers.get("Content-Type") or ""
        try:
            if "multipart/form-data" in ctype:
                fields, files = _parse_multipart(body, ctype)
                if "file" in files:
                    f = files["file"]
                    result = organize_bytes(
                        f["content"],
                        filename=f.get("filename") or "",
                        content_type=f.get("content_type") or "",
                    )
                elif "text" in fields:
                    result = organize_payload({"text": fields["text"]})
                elif "json" in fields:
                    result = organize_payload(json.loads(fields["json"]))
                else:
                    return self._json(400, {"error": "multipart needs file|text|json field"})
            elif "application/json" in ctype or body[:1] in (b"{", b"["):
                payload = json.loads(body.decode("utf-8"))
                if isinstance(payload, list):
                    payload = {"rows": payload}
                result = organize_payload(payload)
            else:
                # treat raw body as text dump
                result = organize_bytes(body, filename="paste.txt", content_type="text/plain")
            return self._json(200, result)
        except Exception as e:
            return self._json(400, {"error": str(e)})

    def _file(self, path: Path, ctype: str):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code: int, obj):
        data = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)


def main():
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Seraphim Organizer → http://{HOST}:{PORT}/", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye", flush=True)
        httpd.server_close()


if __name__ == "__main__":
    main()
