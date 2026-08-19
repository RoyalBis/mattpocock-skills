## What it does

`validate-mermaid` finds Mermaid diagrams in Markdown, MDX, HTML, and standalone Mermaid files, then checks each one with Mermaid's own parser. It can scan one file, one directory level, or an entire directory tree.

It validates syntax against a specific Mermaid version. That matters because a diagram accepted by one release can fail under another; HTML documents with an exact Mermaid import are detected automatically, while other renderers can be supplied explicitly.

## When to reach for it

Type `/validate-mermaid`, or the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) reaches for it automatically after creating or changing Mermaid diagrams.

Reach for it before publishing generated documentation, when a browser shows `Syntax error in text`, or when you want to check every diagram below a directory. For visual design or browser layout problems, use the application's normal browser-testing workflow instead; this skill checks Mermaid grammar rather than rendered appearance.

## Prerequisites

Node.js and npm must be available. The skill installs its pinned parser dependencies into `~/.cache/validate-mermaid` on first use, leaving the repository's dependencies unchanged.

## What it scans

| Input | Mermaid source it validates |
| --- | --- |
| `.md`, `.markdown`, `.mdx` | Fenced code blocks marked `mermaid` |
| `.html`, `.htm` | Elements whose class list includes `mermaid` |
| `.mmd`, `.mermaid` | The complete file |
| Directory | Supported files directly inside it |
| Recursive directory | Supported files at every level, excluding dependency and version-control directories |

Each result includes the file and starting line, so a failed recursive scan points back to the source that needs attention rather than only returning Mermaid's parser message.

## Common questions

**A generated report says `Syntax error in text`. Should this catch it?**

Yes, provided the report is validated with the same Mermaid version it loads. This is why `improve-codebase-architecture` pins Mermaid 11.16.1 and calls this skill before serving its report.

**Does a passing result prove the diagram will look correct?**

No. It proves that Mermaid accepts the source. CDN failures, clipped labels, unreadable sizing, theme differences, and layout problems only appear when the document is rendered in a browser.

**Will a recursive scan walk through `node_modules`?**

No. It skips `node_modules`, virtual environments, and version-control metadata. It still checks generated output directories because those can contain the document that will actually be published.

**Why does it install Mermaid instead of using whichever version is already in the repository?**

Validation must be reproducible and must not mutate the repository. The cache lets multiple projects reuse an exact parser version without adding or changing project packages.

## It's working if

- Every discovered diagram reports a file and starting line.
- Invalid Mermaid returns a non-zero exit and the parser's reason.
- Recursive runs report how many diagrams and files they checked.
- The reported parser version matches the renderer or an explicit version supplied by the caller.
- A passing syntax check is not presented as proof of browser layout.

## Where it fits

`validate-mermaid` is a **reach-for-it-anytime standalone** and a reusable final check for any skill that creates Mermaid. [improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) calls it before serving visual reports; other document-producing skills can use the same check without copying the parser setup. [ask-matt](https://aihero.dev/skills-ask-matt) is the router over the complete skill set.
