"""Dependency-free HTTP adapter for local demonstration."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .gateway import MeasurementGateway
from .models import EventValidationError


class GatewayHandler(BaseHTTPRequestHandler):
    gateway = MeasurementGateway()

    def _respond(self, code: int, body: dict[str, Any]) -> None:
        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/health":
            self._respond(200, {"status": "ok", "service": "measurement-gateway"})
        else:
            self._respond(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path != "/events":
            self._respond(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            decision = self.gateway.ingest(payload)
        except (ValueError, json.JSONDecodeError, EventValidationError) as exc:
            self._respond(400, {"error": str(exc)})
            return
        status_code = {"accepted": 200, "duplicate": 409, "blocked": 202}[decision.status]
        self._respond(status_code, decision.to_dict())

    def log_message(self, _format: str, *_args: Any) -> None:
        # Avoid printing request bodies or identifiers in the demo server log.
        return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), GatewayHandler)
    print(f"Measurement gateway listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
