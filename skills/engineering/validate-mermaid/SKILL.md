---
name: validate-mermaid
description: Validate Mermaid diagrams in Markdown, MDX, HTML, and standalone Mermaid files using Mermaid's own parser. Use when an agent creates or edits Mermaid diagrams, when a browser reports "Syntax error in text", or before publishing generated docs and reports.
---

# Validate Mermaid

Run Mermaid's parser over diagrams before treating their source as complete. This catches grammar errors with the same parser family used by the browser instead of relying on visual inspection or a Markdown parser that does not understand Mermaid.

## Validate

From this skill's directory, run:

```bash
python3 scripts/validate.py <file-or-directory>
```

Add `--recursive` when a directory tree should be scanned:

```bash
python3 scripts/validate.py --recursive <directory>
```

The command reads Mermaid fences in `.md`, `.markdown`, and `.mdx`; elements with the `mermaid` class in `.html` and `.htm`; and complete diagrams in `.mmd` and `.mermaid` files. Recursive scans skip `.git`, other version-control metadata, virtual environments, and `node_modules`.

Use the Mermaid version that will render the document. Exact versions in HTML imports are detected automatically. For another renderer, pass its exact version explicitly:

```bash
python3 scripts/validate.py --mermaid-version 11.16.1 <path>
```

Files without a detectable renderer version use Mermaid 11.16.1. The first run for a version installs Mermaid and JSDOM into `~/.cache/validate-mermaid`; it does not add packages to the user's repository.

## Handle results

The validator prints each diagram's file and starting line. It exits non-zero when a diagram is invalid, a requested path cannot be read, no supported documents are found, or the scanned documents contain no Mermaid diagrams.

When diagram changes are part of the current task, fix every reported syntax error and rerun the same command until it succeeds. When the user asked only for validation, report the errors without changing their files.

Report the command, Mermaid version, number of diagrams, and whether validation passed. Do not claim that syntax validation proves browser rendering: CDN loading, fonts, sizing, theme behaviour, and layout still require a browser check.
