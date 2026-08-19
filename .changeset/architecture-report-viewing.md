---
"mattpocock-skills": patch
---

Add a reusable `validate-mermaid` skill for recursive syntax checks across Markdown, MDX, HTML, and standalone Mermaid files. `improve-codebase-architecture` now delegates its report preflight to this validator and serves validated reports at a temporary localhost URL instead of relying on desktop file openers.
