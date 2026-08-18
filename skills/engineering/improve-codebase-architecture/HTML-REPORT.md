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

The diagrams make relationships easy to see; the prose carries the architectural argument. Write in plain engineering language and use glossary terms from the `/codebase-design` skill only when they improve precision.

Each candidate is one `<article>`. The card can use short named sections, a compact narrative, or a mix of the two. Do not render every analytical checkpoint as a heading merely because the review process collected it separately.

Open the card with the proposed change. A highlighted recommendation sentence works well, but it is not required when the title already states the change precisely.

The reader must still be able to find:

- A short title and opening recommendation that name the domain process or object and state what should change.
- Recommendation strength (`Strong` = emerald, `Worth exploring` = amber, `Speculative` = slate) and confidence (`High`, `Medium`, or `Low`). Include a dependency category only when it materially affects the recommendation, and label it plainly.
- A monospaced file list with line numbers where possible.
- A side-by-side **Before / After diagram**. See the patterns below.
- Concrete caller or test evidence with exact file/line citations and counts when useful.
- The current architectural problem, stated before the implementation details that prove it.
- Any intent from specs, ADRs, comments, or decision logs that constrains the proposal. If none was found, say where you looked.
- A concrete target design: module or type, primary public operation, major inputs, return value, ownership inside the abstraction, and responsibilities left with the caller. Use a compact API sketch when useful.
- A short implementation path for non-trivial changes.
- An expected outcome expressed as a property that callers or tests can demonstrate.
- Meaningful alternatives and the reason for preferring the recommendation, when a real design choice exists.
- Open decisions, especially failure and retry semantics that affect generated output, external effects, or persistence.
- A plain explanation of what becomes simpler for callers and tests.
- The deletion-test result as supporting reasoning.
- An amber ADR callout when the proposal would reopen an existing decision.

Use short paragraphs when the reasoning needs continuity and bullets when the information is genuinely a list. The diagram should clarify the structure, but the prose must remain understandable on its own.

## Reader clarity gates

Each card must make sense to a reader who knows the project but has not just read the files you read.

- The summary under the card title names the domain object or process and the user-visible work. Do not write only the architecture move. Prefer "Assemble signed evidence bundles through one interface" over "Make finalization a deeper interface".
- Start a proven candidate with the proposed change: "Add a `CompletionFinalizer` that owns Evidence Bundle assembly behind `Finalize(...)`." Do not delay the recommendation until after several context paragraphs.
- If a local term names a stage, define it in the first sentence. Example: "Finalization is the post-signature stage that creates the evidence bundle."
- State the architectural problem at the right level. Follow it with the evidence as a short explanation, an ordered sequence, or a few focused bullets.
- Connect intent sources to their implication without making citations control the sentence. Avoid consecutive "Because X says..." constructions.
- Establish the higher-level point before naming implementation work. Explain that callers coordinate the whole process, then use rendering, hashing, manifest construction, or signing steps as evidence.
- Give long operation lists hierarchy. Group related work or move supporting detail into evidence bullets.
- Prefer verbs over compressed implementation nouns: "render the artifacts and hash their bytes" is easier to read than "artifact rendering and stored-byte hashing".
- Make ownership explicit. Say what the proposed abstraction does and which responsibilities remain with its caller.
- Make the target design concrete. Name the type or module, show its main operation, and state its important inputs and output. A small code sketch is preferable to an abstract ownership claim when the caller experience is otherwise ambiguous.
- Give substantial recommendations an implementation path. Keep it short and ordered; include caller and test migration and the fate of old public helpers.
- State what becomes true after the change. Prefer properties that a test can assert over broad claims such as "cleaner architecture."
- Compare alternatives only when they are plausible choices. Explain the tradeoff and select one.
- Call out retry and failure decisions when the operation creates generate-once output, invokes external systems, or leaves work that must be retained between attempts.
- Explain benefits as cause and effect rather than labels such as "locality" or "leverage" followed by fragments.
- Avoid rhetorical concession patterns: "the seam is real, but...", "the interface exists, but...", "this is already good, but...".
- Avoid vague movement verbs: "absorb", "swallow", "hide everything". Use concrete verbs: "move behind the interface", "own", "keep outside", "call", "return", "persist".

Bad:

> The finalization seam is real in the implementation, but the exported interface still requires bundle-producing callers to learn PDF assembly, stored-byte hashing, manifest construction, canonical bytes, digesting, sealing order, and Bundle field wiring.

Good:

> Add a `CompletionFinalizer` that owns Evidence Bundle assembly behind one `Finalize(...)` operation.
>
> Callers currently orchestrate the entire completion protocol. They render the documents and hash the stored bytes, then build the manifest, seal its digest, and construct the final `Bundle`.

A useful target sketch makes the ownership concrete without pretending the interface is finished:

```go
type CompletionFinalizer struct {
    // resolved limits and internal collaborators
}

func (f *CompletionFinalizer) Finalize(
    ctx context.Context,
    bundleID BundleID,
    frozen FrozenEvidence,
    original Document,
    sealer Sealer,
) (Bundle, error)
```

Follow the sketch with the ownership decision:

> The finalizer renders the completion documents, hashes the stored bytes, builds the canonical manifest, computes its digest, invokes the supplied sealer, and returns a populated bundle. The caller still mints the bundle ID and owns key infrastructure, durable storage, and verification trust anchors.

For a non-trivial recommendation, include a short implementation path:

1. Introduce `CompletionFinalizer`.
2. Move document production and stored-byte hashing behind it.
3. Move manifest construction, canonicalization, digest calculation, and the sealer call behind `Finalize(...)`.
4. Return the complete `Bundle`.
5. Migrate bundle-building callers and tests, then narrow lower-level helpers that no longer need to be public.

State the result in caller-visible terms:

> After this change, a bundle-producing caller provides the frozen evidence, original document, bundle ID, and sealer. It receives a complete bundle and does not need to know the manifest format, artifact ordering, digest construction, or bundle field layout.

When failure can affect identity, separate the open decision:

> Open decision: define what survives a sealing or persistence failure. If document bytes are generate-once, the design must say whether `Finalize(...)` can be repeated, whether generated bytes are returned on failure, and which data the caller must retain before retrying.

When the design has a real choice, compare only the plausible options:

- **Option A: `CompletionFinalizer.Finalize(...)`** — owns the complete sequence behind one operation.
- **Option B: keep a lower-level manifest builder** — removes some duplication but leaves callers responsible for ordering and sealing.
- **Option C: keep the current primitives** — preserves maximum flexibility while every bundle-producing caller continues to coordinate the protocol.

Then choose: *Recommend Option A because the domain assigns bundle assembly to the module and callers do not need the lower-level sequencing to vary.*

Intent Check bad:

> PROTOCOL.md requires seal verification over stored bytes and additive-field tolerance. It does not permit skipping required known fields.

Intent Check good:

> The protocol verifies the seal against the stored manifest bytes, so the manifest module must preserve those bytes rather than parse and serialize them again. Its tolerance for unknown fields does not prevent it from rejecting required v1 signer fields when they are missing.

Benefit bad:

> locality: one finalization module
> leverage: one caller interface
> artifact order hidden

Benefit good:

> Callers use one operation instead of coordinating the sequence themselves. The rules for producing and sealing the bundle live in one implementation, and tests exercise that sequence through the same interface as production callers.

## Evidence gates

Every candidate must establish the following during analysis. The report must communicate the results, but these labels do not all need to appear in the rendered card:

- **Caller evidence** — real call sites or tests that must learn implementation ordering, invariants, collaborators, or data shape.
- **Intent source** — specs, ADRs, decision logs, comments, or "none found after checking X/Y/Z".
- **Deletion-test result** — what complexity concentrates behind the deeper interface instead of moving elsewhere.
- **Target design** — the module or type, primary public operation, major inputs, return value, responsibilities moved inside, and responsibilities left outside.
- **Implementation path** — the ordered code, caller, and test changes needed to reach the target design.
- **Expected outcome** — caller-visible and testable properties of the resulting architecture.
- **Alternatives** — plausible options and a reasoned selection when the design has a meaningful choice.
- **Failure semantics** — retry, partial-output, identity, and persistence decisions when they affect the interface.
- **Testing payoff** — the seam tests would use and any old test surface that can shrink.

Do not let architecture vocabulary stand in for evidence. A claim that callers coordinate the whole bundle process is only proven when the card cites real callers that perform the sequence and checks whether a spec intentionally assigned that work to them. Mention the individual operations as supporting evidence rather than making the inventory carry the argument. Without that proof, present the idea as a question to validate.

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

Use one larger card with the implementation decision, why it should come first, the expected result, any blocking open decision, and an anchor link to its card.

## Tone

Write like an experienced engineer explaining a proposal to another engineer. Be concise, but give the reasoning enough syntax to breathe.

Use **module**, **interface**, **implementation**, **depth**, **deep**, **shallow**, **seam**, **adapter**, **leverage**, and **locality** accurately when those distinctions matter. Do not recite the vocabulary or stack several of its nouns into one sentence. Domain terms from `CONTEXT.md` usually make better subjects than abstract architecture terms.

Do not casually replace a precise glossary concept with "component", "service", "API", or "boundary". When the glossary concept is not the point, use ordinary engineering language rather than searching for a glossary word to insert.

Evidence bullets should name observable facts: *"`finalizer.go:42-61` repeats the manifest sequence"*, *"`bundle_test.go:18-39` constructs the same result"*, *"`ADR-0007` assigns storage to the caller"*. In the surrounding prose, translate abstractions into actions: callers construct, pass, order, verify, or persist.

Explain benefits rather than naming them. For example: *"Callers use one operation instead of reproducing the sequence. Changes to that sequence stay in one module, and tests cover it through the caller-facing interface."* This expresses leverage, locality, and the testing payoff without turning them into labels.

Use the deletion test in the same way. Write *"If this module disappeared, the ordering rules would move back into all four callers"* rather than *"Deletion test: passes."*

Cut hedging and throat-clearing, but do not cut the connective reasoning that makes the proposal readable. Prefer complete thoughts over note-like fragments, and choose paragraphs or bullets according to the material rather than a fixed template.
