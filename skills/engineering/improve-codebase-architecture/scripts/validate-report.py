#!/usr/bin/env python3
"""Compatibility wrapper for the shared validate-mermaid skill."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


MERMAID_VERSION = "11.16.1"
PINNED_MERMAID_IMPORT = re.compile(
    r"(?:mermaid@|/mermaid/)([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?)"
)


def find_validator() -> Path:
    override = os.environ.get("VALIDATE_MERMAID_SCRIPT")
    candidates = [
        Path(override).expanduser() if override else None,
        Path(__file__).resolve().parents[2]
        / "validate-mermaid"
        / "scripts"
        / "validate.py",
        Path.home() / ".agents" / "skills" / "validate-mermaid" / "scripts" / "validate.py",
        Path.home() / ".claude" / "skills" / "validate-mermaid" / "scripts" / "validate.py",
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise SystemExit(
        "validate-mermaid is required; install that skill or set VALIDATE_MERMAID_SCRIPT"
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate-report.py <report.html>")
    report = Path(sys.argv[1]).expanduser().resolve(strict=True)
    if not report.is_file() or report.suffix.lower() != ".html":
        raise SystemExit(f"report must be an HTML file: {report}")
    versions = set(
        PINNED_MERMAID_IMPORT.findall(report.read_text(encoding="utf-8"))
    )
    if versions != {MERMAID_VERSION}:
        rendered = ", ".join(sorted(versions)) if versions else "no exact version"
        raise SystemExit(
            f"report must import Mermaid {MERMAID_VERSION}; found {rendered}"
        )

    result = subprocess.run(
        [
            sys.executable,
            str(find_validator()),
            "--mermaid-version",
            MERMAID_VERSION,
            str(report),
        ],
        check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
