#!/usr/bin/env python3
"""Serve one generated architecture report without exposing its directory."""

from __future__ import annotations

import argparse
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="HTML report to serve")
    parser.add_argument("--bind", default="0.0.0.0", help="address to bind")
    parser.add_argument("--port", type=int, default=0, help="port, or 0 for any free port")
    return parser.parse_args()


def handler_for(report: Path, route: str) -> type[BaseHTTPRequestHandler]:
    content = report.read_bytes()

    class ReportHandler(BaseHTTPRequestHandler):
        def do_HEAD(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler hook
            self._respond(include_body=False)

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler hook
            self._respond(include_body=True)

        def _respond(self, *, include_body: bool) -> None:
            path = urlsplit(self.path).path
            if path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return
            if path not in (route, f"{route}index.html"):
                self.send_error(404)
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if include_body:
                self.wfile.write(content)

        def log_message(self, format: str, *args: object) -> None:
            return

    return ReportHandler


def main() -> None:
    args = parse_args()
    report = args.report.expanduser().resolve(strict=True)
    if not report.is_file() or report.suffix.lower() != ".html":
        raise SystemExit(f"report must be an HTML file: {report}")

    route = f"/{secrets.token_urlsafe(18)}/"
    server = ThreadingHTTPServer((args.bind, args.port), handler_for(report, route))
    port = server.server_address[1]
    print(f"REPORT_URL=http://localhost:{port}{route}", flush=True)
    print(f"REPORT_PATH={report}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
