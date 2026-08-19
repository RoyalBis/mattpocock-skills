#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "scripts" / "validate.py"


class ValidateMermaidTests(unittest.TestCase):
    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(VALIDATOR), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_recursively_validates_supported_document_formats(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs").mkdir()
            (root / "site").mkdir()
            (root / "diagrams").mkdir()
            (root / "docs" / "flow.md").write_text(
                textwrap.dedent(
                    """\
                    # Flow

                    ```mermaid
                    flowchart TD
                      A[Start] --> B[Done]
                    ```
                    """
                ),
                encoding="utf-8",
            )
            (root / "site" / "report.html").write_text(
                textwrap.dedent(
                    """\
                    <!doctype html>
                    <script type="module">
                      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.16.1/dist/mermaid.esm.min.mjs";
                    </script>
                    <pre class="mermaid">sequenceDiagram
                      Alice->>Bob: Hello</pre>
                    """
                ),
                encoding="utf-8",
            )
            (root / "diagrams" / "states.mmd").write_text(
                "stateDiagram-v2\n  [*] --> Ready\n",
                encoding="utf-8",
            )
            (root / "ignored.txt").write_text(
                "```mermaid\nflowchart TD\n  X --> Y\n```\n",
                encoding="utf-8",
            )

            result = self.run_validator("--recursive", str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("docs/flow.md:4", result.stdout)
            self.assertIn("site/report.html:5", result.stdout)
            self.assertIn("diagrams/states.mmd:1", result.stdout)
            self.assertIn(
                "validated 3 Mermaid diagram(s) in 3 file(s)", result.stdout
            )
            self.assertNotIn("ignored.txt", result.stdout)

    def test_reports_the_file_and_line_for_invalid_mermaid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            document = root / "broken.md"
            document.write_text(
                textwrap.dedent(
                    """\
                    # Broken

                    ```mermaid
                    flowchart TD
                      A[Finalizer] -->|PutEvents: []Event| B[Storage]
                    ```
                    """
                ),
                encoding="utf-8",
            )

            result = self.run_validator(str(document))

            self.assertEqual(result.returncode, 1)
            self.assertIn(f"invalid {document}:5", result.stderr)
            self.assertIn("Parse error", result.stderr)
            self.assertNotIn("validated 1 Mermaid diagram", result.stdout)

    def test_html_validation_uses_the_source_mermaid_will_render(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "report.html"
            report.write_text(
                textwrap.dedent(
                    """\
                    <pre class="mermaid">flowchart TD
                      A --> B
                      <!-- invalid Mermaid source -->
                    </pre>
                    """
                ),
                encoding="utf-8",
            )

            result = self.run_validator(str(report))

            self.assertEqual(result.returncode, 1)
            self.assertIn(f"invalid {report}:3", result.stderr)

    def test_markdown_parser_ignores_example_fences_and_reads_blockquotes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Path(temp_dir) / "examples.md"
            document.write_text(
                textwrap.dedent(
                    """\
                    ````markdown
                    ```mermaid
                    this is shown as an example, not rendered
                    ```
                    ````

                    > ```mermaid
                    > flowchart LR
                    >   A --> B
                    > ```
                    """
                ),
                encoding="utf-8",
            )

            result = self.run_validator(str(document))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"ok {document}:8", result.stdout)
            self.assertIn("validated 1 Mermaid diagram(s)", result.stdout)

    def test_directory_scan_is_not_recursive_without_the_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            nested = root / "nested"
            nested.mkdir()
            (root / "top.mermaid").write_text(
                "flowchart LR\n  A --> B\n", encoding="utf-8"
            )
            (nested / "broken.mermaid").write_text(
                "flowchart LR\n  A -->|[]Event| B\n", encoding="utf-8"
            )

            result = self.run_validator(str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("top.mermaid:1", result.stdout)
            self.assertNotIn("broken.mermaid", result.stdout + result.stderr)
            self.assertIn(
                "validated 1 Mermaid diagram(s) in 1 file(s)", result.stdout
            )

    def test_fails_when_supported_documents_contain_no_mermaid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            document = Path(temp_dir) / "notes.md"
            document.write_text("# Notes\n\nNo diagrams here.\n", encoding="utf-8")

            result = self.run_validator(str(document))

            self.assertEqual(result.returncode, 1)
            self.assertIn("no Mermaid diagrams found", result.stderr)

    def test_missing_path_has_a_concise_error(self) -> None:
        result = self.run_validator("/path/that/does/not/exist.mmd")

        self.assertEqual(result.returncode, 1)
        self.assertIn("path does not exist", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
