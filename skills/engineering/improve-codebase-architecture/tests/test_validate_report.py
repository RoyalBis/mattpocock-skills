#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "scripts" / "validate-report.py"


class ValidateReportTests(unittest.TestCase):
    def run_validator(
        self, report: Path, validator_script: Path
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["VALIDATE_MERMAID_SCRIPT"] = str(validator_script)
        return subprocess.run(
            ["python3", str(VALIDATOR), str(report)],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_accepts_the_exact_renderer_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            validator = root / "validator.py"
            validator.write_text("raise SystemExit(0)\n", encoding="utf-8")
            report = root / "report.html"
            report.write_text(
                '<script src="https://cdn.jsdelivr.net/npm/mermaid@11.16.1/dist/mermaid.esm.min.mjs"></script>',
                encoding="utf-8",
            )

            result = self.run_validator(report, validator)

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_a_different_renderer_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            validator = root / "validator.py"
            validator.write_text("raise SystemExit(0)\n", encoding="utf-8")
            report = root / "report.html"
            report.write_text(
                '<script src="https://cdn.jsdelivr.net/npm/mermaid@11.15.0/dist/mermaid.esm.min.mjs"></script>',
                encoding="utf-8",
            )

            result = self.run_validator(report, validator)

            self.assertEqual(result.returncode, 1)
            self.assertIn("must import Mermaid 11.16.1", result.stderr)
            self.assertIn("found 11.15.0", result.stderr)

    def test_rejects_a_floating_renderer_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            validator = root / "validator.py"
            validator.write_text("raise SystemExit(0)\n", encoding="utf-8")
            report = root / "report.html"
            report.write_text(
                '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"></script>',
                encoding="utf-8",
            )

            result = self.run_validator(report, validator)

            self.assertEqual(result.returncode, 1)
            self.assertIn("found no exact version", result.stderr)


if __name__ == "__main__":
    unittest.main()
