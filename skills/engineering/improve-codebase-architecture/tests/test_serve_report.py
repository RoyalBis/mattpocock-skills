#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SERVE_REPORT = SKILL_DIR / "scripts" / "serve-report.py"
SPEC = importlib.util.spec_from_file_location("serve_report", SERVE_REPORT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {SERVE_REPORT}")
serve_report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(serve_report)


class ServeReportTests(unittest.TestCase):
    def test_serves_only_the_tokenized_report_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "report.html"
            report.write_text("<h1>Architecture</h1>", encoding="utf-8")
            server = ThreadingHTTPServer(
                ("127.0.0.1", 0),
                serve_report.handler_for(report, "/private-token/"),
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_address[1]}"
            try:
                with urllib.request.urlopen(
                    f"{base_url}/private-token/", timeout=2
                ) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(
                        response.read(), b"<h1>Architecture</h1>"
                    )
                    self.assertEqual(response.headers["Cache-Control"], "no-store")

                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(f"{base_url}/", timeout=2)
                self.assertEqual(error.exception.code, 404)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
