"""A stand-in Ollama: `/api/version` and `/api/tags` on a free local port."""

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

PULLED = ["gpt-oss:20b"]


class _Ollama(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        bodies = {
            "/api/version": {"version": "0.0.0-test"},
            "/api/tags": {"models": [{"name": name} for name in PULLED]},
        }
        body = bodies.get(self.path)
        self.send_response(200 if body else 404)
        self.end_headers()
        if body:
            self.wfile.write(json.dumps(body).encode())

    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture
def ollama_url() -> Iterator[str]:
    server = HTTPServer(("127.0.0.1", 0), _Ollama)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
