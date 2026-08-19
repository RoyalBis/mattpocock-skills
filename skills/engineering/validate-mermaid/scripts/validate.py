#!/usr/bin/env python3
"""Discover and validate Mermaid diagrams with Mermaid's own parser."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


DEFAULT_MERMAID_VERSION = "11.16.1"
JSDOM_VERSION = "26.1.0"
MDAST_VERSION = "2.0.3"
SUPPORTED_SUFFIXES = {".htm", ".html", ".markdown", ".md", ".mdx", ".mermaid", ".mmd"}
SKIPPED_DIRECTORIES = {".git", ".hg", ".svn", ".venv", "node_modules", "venv"}
EXACT_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
HTML_MERMAID_VERSION = re.compile(
    r"(?:mermaid@|/mermaid/)([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Mermaid diagrams in documents and standalone diagram files."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Supported file or directory to scan",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Descend into subdirectories when a path is a directory",
    )
    parser.add_argument(
        "--mermaid-version",
        metavar="VERSION",
        help=(
            "Exact Mermaid version to use for every diagram. By default, pinned HTML "
            f"imports are detected and other files use {DEFAULT_MERMAID_VERSION}."
        ),
    )
    args = parser.parse_args()
    if args.mermaid_version and not EXACT_VERSION.fullmatch(args.mermaid_version):
        parser.error("--mermaid-version must be an exact semantic version such as 11.16.1")
    return args


def iter_directory(directory: Path, recursive: bool):
    if not recursive:
        yield from sorted(directory.iterdir())
        return

    for root, directory_names, file_names in os.walk(directory):
        directory_names[:] = sorted(
            name for name in directory_names if name not in SKIPPED_DIRECTORIES
        )
        root_path = Path(root)
        for file_name in sorted(file_names):
            yield root_path / file_name


def discover(paths: list[str], recursive: bool) -> list[dict[str, str]]:
    discovered: dict[Path, str] = {}
    for raw_path in paths:
        requested = Path(raw_path).expanduser()
        try:
            path = requested.resolve(strict=True)
        except FileNotFoundError as error:
            raise SystemExit(f"path does not exist: {requested}") from error
        if path.is_file():
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                raise SystemExit(f"unsupported Mermaid document type: {path}")
            discovered.setdefault(path, str(path))
            continue
        if not path.is_dir():
            raise SystemExit(f"path must be a file or directory: {path}")

        for candidate in iter_directory(path, recursive):
            if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            resolved = candidate.resolve()
            discovered.setdefault(resolved, str(resolved.relative_to(path)))

    if not discovered:
        raise SystemExit("no supported Mermaid documents found")
    return [
        {"path": str(path), "display": discovered[path]}
        for path in sorted(discovered, key=lambda item: str(item))
    ]


def detect_html_version(path: Path) -> str | None:
    if path.suffix.lower() not in {".htm", ".html"}:
        return None
    try:
        html = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise SystemExit(f"cannot read UTF-8 document {path}: {error}") from error
    versions = set(HTML_MERMAID_VERSION.findall(html))
    if len(versions) > 1:
        rendered = ", ".join(sorted(versions))
        raise SystemExit(f"multiple pinned Mermaid versions in {path}: {rendered}")
    return next(iter(versions), None)


def installed_version(modules: Path, package: str) -> str | None:
    package_json = modules / package / "package.json"
    try:
        return json.loads(package_json.read_text(encoding="utf-8"))["version"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None


def ensure_modules(cache: Path, mermaid_version: str) -> Path:
    modules = cache / "node_modules"
    if (
        installed_version(modules, "mermaid") == mermaid_version
        and installed_version(modules, "jsdom") == JSDOM_VERSION
        and installed_version(modules, "mdast-util-from-markdown") == MDAST_VERSION
    ):
        return modules
    if shutil.which("npm") is None:
        raise SystemExit("npm is required to install the Mermaid validator")

    cache.mkdir(parents=True, exist_ok=True)
    print(
        f"installing Mermaid {mermaid_version} validator in {cache}",
        flush=True,
    )
    try:
        subprocess.run(
            [
                "npm",
                "install",
                "--prefix",
                str(cache),
                "--no-package-lock",
                "--no-save",
                "--no-audit",
                "--no-fund",
                f"mermaid@{mermaid_version}",
                f"jsdom@{JSDOM_VERSION}",
                f"mdast-util-from-markdown@{MDAST_VERSION}",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as error:
        raise SystemExit(
            f"failed to install Mermaid {mermaid_version} validator"
        ) from error
    return modules


def validate_group(
    files: list[dict[str, str]],
    mermaid_version: str,
    cache_root: Path,
) -> tuple[int, int, int]:
    modules = ensure_modules(cache_root / f"mermaid-{mermaid_version}", mermaid_version)
    validator = Path(__file__).with_name("validate.mjs")

    with tempfile.TemporaryDirectory(prefix="validate-mermaid-") as temp_dir:
        temp = Path(temp_dir)
        manifest = temp / "manifest.json"
        result_path = temp / "result.json"
        manifest.write_text(json.dumps(files), encoding="utf-8")
        result = subprocess.run(
            [
                "node",
                str(validator),
                str(manifest),
                str(modules),
                str(result_path),
            ],
            check=False,
        )
        if not result_path.exists():
            raise SystemExit(result.returncode or 1)
        summary = json.loads(result_path.read_text(encoding="utf-8"))
        return summary["diagrams"], summary["files"], summary["failures"]


def main() -> None:
    args = parse_args()
    if shutil.which("node") is None:
        raise SystemExit("node is required to run the Mermaid validator")

    files = discover(args.paths, args.recursive)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for file in files:
        version = (
            args.mermaid_version
            or detect_html_version(Path(file["path"]))
            or DEFAULT_MERMAID_VERSION
        )
        grouped[version].append(file)

    cache_root = Path(
        os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
    ) / "validate-mermaid"
    total_diagrams = 0
    files_with_diagrams = 0
    failures = 0
    for version in sorted(grouped):
        diagrams, diagram_files, group_failures = validate_group(
            grouped[version], version, cache_root
        )
        total_diagrams += diagrams
        files_with_diagrams += diagram_files
        failures += group_failures

    if failures:
        raise SystemExit(1)
    if total_diagrams == 0:
        raise SystemExit(f"no Mermaid diagrams found in {len(files)} scanned file(s)")

    versions = ", ".join(sorted(grouped))
    print(
        f"validated {total_diagrams} Mermaid diagram(s) in "
        f"{files_with_diagrams} file(s) with Mermaid {versions}"
    )


if __name__ == "__main__":
    main()
