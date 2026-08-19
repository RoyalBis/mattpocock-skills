# Slidev authoring reference

Use this as a compact map, not a substitute for the installed version's help or the official documentation. Check version-sensitive commands and options against the project's `package.json`, local CLI help, and the linked primary sources.

## Project conventions

| Path | Purpose |
| --- | --- |
| `slides.md` | Default deck entry and headmatter |
| `public/` | Static assets served from `/` and copied into the build |
| `components/` | Auto-imported Vue components |
| `layouts/` | Local layouts that override theme and built-in layouts |
| `snippets/` | Source snippets imported into code blocks |
| `style.css` or `styles/index.*` | Global styles; scope slide rules under `.slidev-layout` |

A minimal deck uses YAML headmatter on the first slide, blank-line-padded `---` separators, optional per-slide frontmatter, and an HTML comment at the end of a slide for presenter notes:

````md
---
theme: default
title: A clear promise
aspectRatio: 16/9
---

# A clear promise

What the audience will leave with

<!--
Open with the audience's current pain. Pause before revealing the promise.
-->

---
layout: two-cols
---

# The old path hides the tradeoff

```ts {2|3-4}
const input = read()
const result = transform(input)
publish(result)
```

::right::

## The new path makes it visible

One explanation, diagram, or result.
````

The first frontmatter block is deck-wide headmatter. Later frontmatter blocks configure one slide. A slide's presenter note is the final HTML comment in that slide.

## Choose the smallest Slidev feature that carries the beat

| Need | Reach for | Verify |
| --- | --- | --- |
| Establish a new section or key claim | `cover`, `section`, `statement`, or `fact` layout | Hierarchy and breathing room |
| Compare two things | `two-cols`, `two-cols-header`, or a purpose-built local layout | Equal visual weight and aligned baselines |
| Explain code in stages | Shiki line highlighting or magic-move | Every click state and readable code size |
| Let the audience edit or run code | Monaco features | Browser support, reset behavior, and a static fallback |
| Reveal an argument in order | `v-click`, `v-clicks`, or click ranges | Forward and backward navigation |
| Show a system or sequence | Mermaid or PlantUML | Parser validity, label size, and rendered fit |
| Show math | KaTeX/LaTeX | Glyph rendering and export output |
| Reuse a repeated visual structure | A local Vue component or layout | Props, empty states, and theme consistency |
| Reuse or split deck sections | `src` imports from another Markdown file | Rendered numbering and frontmatter merging |

Use slide-scoped `<style>` for a one-slide exception. Use global styles or a local layout for a pattern that repeats. Prefer a small set of reusable layouts to many near-duplicate utility-class compositions.

## Assets and exports

Reference `public/diagram.png` as `/diagram.png`. Local assets make offline presenting and export more reliable than runtime remote fetches.

Slidev can export PDF, image-based PPTX, PNG, and Markdown. CLI visual exports require `playwright-chromium`. Use `--with-clicks` when click states must become separate exported pages. A hosted build preserves interactions that static exports cannot.

When Playwright is present but cannot start because the host lacks browser libraries, use an existing browser tool, Slidev's browser exporter, or an already-installed Chromium executable. If the environment offers none of those, report rendered QA as blocked and name the missing dependency rather than substituting a source-only review.

## Agent tooling

Current Slidev versions expose an MCP endpoint at `http://localhost:<port>/__mcp` while the dev server runs, and a standalone `slidev mcp [entry]` command. The tools can inspect, update, insert, remove, reorder, and navigate slides. Use them when already connected; direct Markdown and Vue edits remain the source of truth.

## Primary sources

- [Getting started and current commands](https://sli.dev/guide/)
- [Syntax, frontmatter, notes, code, and diagrams](https://sli.dev/guide/syntax.html)
- [Layouts](https://sli.dev/guide/layout)
- [Animations and click states](https://sli.dev/guide/animations)
- [Project directory structure](https://sli.dev/custom/directory-structure)
- [Exporting](https://sli.dev/guide/exporting.html)
- [MCP server](https://sli.dev/features/mcp)
- [Official Slidev agent skill](https://github.com/slidevjs/slidev/tree/main/skills/slidev)
