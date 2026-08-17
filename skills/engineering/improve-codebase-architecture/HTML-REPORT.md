# HTML Report Format

The architectural review is rendered as a single self-contained HTML file in the OS temp directory. Tailwind and Mermaid both come from CDNs. Mermaid handles graph-shaped diagrams reliably; hand-built divs and inline SVG handle the more editorial visuals (mass diagrams, cross-sections). Mix the two — don't lean on Mermaid for everything, it'll start to look generic.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review — {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer for things Tailwind doesn't cover cleanly:
         dashed seam lines, hand-drawn-feeling arrow heads, etc. */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Repo name, date, and a compact legend: solid box = module, dashed line = seam, red arrow = leakage, thick dark box = deep module. No introduction paragraph — straight into the candidates.

## Candidate card

The diagrams carry the weight. Prose is sparse, plain, and uses the glossary terms (from the `/codebase-design` skill) without ceremony.

Each candidate is one `<article>`:

- **Title** — short, names the deepening (e.g. "Collapse the Order intake pipeline").
- **Badge row** — recommendation strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate), plus a tag for the dependency category (`in-process`, `local-substitutable`, `ports & adapters`, `mock`).
- **Files** — monospaced list, `font-mono text-sm`, with line numbers where possible.
- **Before / After diagram** — the centrepiece. Two columns, side by side. See patterns below.
- **Evidence** — 2-4 bullets naming the concrete caller/test evidence and exact file/line citations. Include counts when available.
- **Intent check** — a short source-to-implication note saying whether specs, ADRs, comments, or decision logs make the current shape intentional, and how that affects the candidate. If none were found, say "No intent source found" and cite where you looked.
- **Problem** or **Question to validate** — **Problem** only when evidence proves real friction. **Question to validate** when the observation is plausible but still missing caller evidence, intent clarity, or deletion-test certainty.
- **Solution** — one sentence. What changes, including the rough interface shape (name plus 1-3 entry points).
- **Wins** — bullets, ≤6 words each. e.g. "Tests hit one interface", "Pricing logic stops leaking", "Delete 4 shallow wrappers".
- **Confidence** — `High`, `Medium`, or `Low`, plus one short reason. `Strong` candidates should almost always be `High`; `Speculative` candidates should almost always be `Low`.
- **ADR callout** (if applicable) — one line in an amber-tinted box.

No paragraphs of explanation. If the diagram needs a paragraph to be understood, redraw the diagram. If the evidence needs more room, the candidate is not ready for this report; narrow it until the proof is crisp.

## Reader clarity gates

Each card must make sense to a reader who knows the project but has not just read the files you read.

- The summary under the card title names the domain object or process and the user-visible work. Do not write only the architecture move. Prefer "Assemble signed evidence bundles through one interface" over "Make finalization a deeper interface".
- If a local term names a stage, define it in the first sentence. Example: "Finalization is the post-signature stage that creates the evidence bundle."
- The **Problem** starts with the claim. The next sentence gives the evidence as ordered operations or short bullets.
- The **Intent check** connects facts. Do not write two adjacent source facts and make the reader infer the relationship. Use: "Because the spec requires X, this candidate must preserve Y; it can still change Z."
- Long operation lists need hierarchy. Group by work type: document artifacts, manifest bytes, seal, returned bundle.
- Avoid rhetorical concession patterns: "the seam is real, but...", "the interface exists, but...", "this is already good, but...".
- Avoid vague movement verbs: "absorb", "swallow", "hide everything". Use concrete verbs: "move behind the interface", "own", "keep outside", "call", "return", "persist".

Bad:

> The finalization seam is real in the implementation, but the exported interface still requires bundle-producing callers to learn PDF assembly, stored-byte hashing, manifest construction, canonical bytes, digesting, sealing order, and Bundle field wiring.

Good:

> The exported interface still exposes too much of the bundle-finalization process. Callers have to assemble the PDF, hash the stored bytes, construct and canonicalize the manifest, compute its digest, seal the digest in the correct order, and populate the Bundle fields themselves.

Intent Check bad:

> PROTOCOL.md requires seal verification over stored bytes and additive-field tolerance. It does not permit skipping required known fields.

Intent Check good:

> Because PROTOCOL.md requires seal verification over stored bytes, the manifest module must keep the original bytes for the seal check and avoid parse-reserializing them. Additive-field tolerance only applies to unknown fields; the same parser can still reject known v1 signer fields when they are missing.

## Evidence gates

Every card must show:

- **Caller evidence** — real call sites or tests that must learn implementation ordering, invariants, collaborators, or data shape.
- **Intent source** — specs, ADRs, decision logs, comments, or "none found after checking X/Y/Z".
- **Deletion-test result** — what complexity concentrates behind the deeper interface instead of moving elsewhere.
- **Interface sketch** — the proposed module name and 1-3 entry points.
- **Testing payoff** — the seam tests would use and any old test surface that can shrink.

Do not let architecture vocabulary stand in for evidence. A sentence like "callers still assemble the PDF, hash the stored bytes, canonicalize the manifest, digest it, seal it, and populate the Bundle" is only acceptable if the card cites real callers that repeat that sequence and checks whether a spec intentionally assigned that orchestration to them. Without that proof, write it as a **Question to validate**.

## Diagram patterns

Pick the pattern that fits the candidate. Mix them. Don't make every diagram look the same — variety is part of the point.

### Mermaid graph (the workhorse for dependencies / call flow)

Use a Mermaid `flowchart` or `graph` when the point is "X calls Y calls Z, and look at the mess." Wrap it in a Tailwind-styled card so it doesn't feel parachuted in. Style with classDef to colour leakage edges red and the deep module dark. Sequence diagrams work well for "before: 6 round-trips; after: 1."

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### Hand-built boxes-and-arrows (when Mermaid's layout fights you)

Modules as `<div>`s with borders and labels. Arrows as inline SVG `<line>` or `<path>` elements positioned absolutely over a relative container. Reach for this when you want the "after" diagram to feel like one thick-bordered deep module with greyed-out internals — Mermaid won't render that with the right weight.

### Cross-section (good for layered shallowness)

Stack horizontal bands (`h-12 border-l-4`) to show layers a call passes through. Before: 6 thin layers each doing nothing. After: 1 thick band labelled with the consolidated responsibility.

### Mass diagram (good for "interface as wide as implementation")

Two rectangles per module — one for interface surface area, one for implementation. Before: interface rectangle is nearly as tall as the implementation rectangle (shallow). After: interface rectangle is short, implementation rectangle is tall (deep).

### Call-graph collapse

Before: a tree of function calls rendered as nested boxes. After: the same tree collapsed into one box, with the now-internal calls shown faded inside it.

## Style guidance

- Lean editorial, not corporate-dashboard. Generous whitespace. Serif optional for headings (`font-serif` works well with stone/slate).
- Colour sparingly: one accent (emerald or indigo) plus red for leakage and amber for warnings.
- Keep diagrams ~320px tall so before/after sits comfortably side by side without scrolling.
- Use `text-xs uppercase tracking-wider` for module labels inside diagrams — they should read as schematic, not as UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static — no app code, no interactivity beyond Mermaid's own rendering.

## Top recommendation section

One larger card. Candidate name, one sentence on why, anchor link to its card. That's it.

## Tone

Plain English, concise — but the architectural nouns and verbs come straight from the `/codebase-design` skill. Concision is not an excuse to drift.

**Use exactly:** module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality.

**Never substitute:** component, service, unit (for module) · API, signature (for interface) · boundary (for seam) · layer, wrapper (for module, when you mean module).

**Phrasings that fit the style:**

- "Order intake module is shallow — interface nearly matches the implementation."
- "Pricing leaks across the seam."
- "Deepen: one interface, one place to test."
- "Two adapters justify the seam: HTTP in prod, in-memory in tests."

**Evidence bullets** name facts, not interpretations: *"`finalizer.go:42-61` repeats the 5-step manifest sequence"*, *"`bundle_test.go:18-39` hand-assembles the same order"*, *"`ADR-0007` explicitly assigns storage outside the seam"*. Don't write *"callers learn everything"* unless you can point to the callers. Even then, translate "learn" into observable work: "callers construct", "callers pass", "callers order", "callers persist".

**Wins bullets** name the gain in glossary terms: *"locality: bugs concentrate in one module"*, *"leverage: one interface, N call sites"*, *"interface shrinks; wrappers move inside"*. Don't write *"easier to maintain"* or *"cleaner code"* — those terms aren't in the glossary and don't earn their place.

No hedging, no throat-clearing, no "it's worth noting that…". No "X is real, but..." setup clauses. If a sentence could be a bullet, make it a bullet. If a bullet could be cut, cut it. If a term isn't in the `/codebase-design` glossary, reach for one that is before inventing a new one.
