---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- Call the Skill tool with "codebase-design" for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real"). Use these terms exactly in every suggestion — don't drift into "component," "service," "API," or "boundary."
- The domain language in `CONTEXT.md` gives names to good seams; ADRs in `docs/adr/` record decisions this command should not re-litigate.

## Process

### 1. Explore

**Scope before you scan — YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction — a module, a subsystem, a pain point — take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots — the files and areas that keep coming up — and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Read the project's domain glossary (`CONTEXT.md`) and any ADRs in the area you're touching first.

Then spawn a sub-agent to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

Before a finding can become a candidate, prove it. For each possible candidate collect:

- **Caller evidence** — at least one real caller or test that has to know the ordering, invariants, collaborators, or data shape you want to hide. Prefer counts: "4 callers repeat this sequence" beats "callers learn this".
- **File/line citations** — cite the exact lines for the public interface, the leaked implementation knowledge, and the caller/test evidence. A flat file list is not evidence.
- **Spec/ADR intent check** — read nearby specs, ADRs, decision logs, or comments that may make the current shape intentional. If the current interface was deliberately specified, say so and downgrade unless you can show new friction that justifies reopening the decision.
- **Deletion-test result** — state what complexity would move where if the module disappeared. If the answer is "unknown", the candidate is not proven.
- **Interface sketch** — enough shape to show the proposed deep module could actually hide the complexity: name, 1-3 entry points, key inputs/outputs, and what remains outside the seam.
- **Testing payoff** — identify the test seam that improves and which current tests or test helpers would disappear or simplify.

Do not turn vocabulary matching into proof. Seeing "Sealer", "manifest", "adapter", or "interface" in code does not by itself prove a bad seam. If the evidence is plausible but incomplete, present it as a **Question to validate**, not as a **Problem**.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file. Open it for the user — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — and tell them the absolute path.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals — use Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something more editorial (mass diagrams, cross-sections, collapse animations). Each candidate gets a **before/after visualisation**. Be visual.

For each candidate, render a card with:

- **Files** — which files/modules are involved
- **Evidence** — the strongest caller/test evidence, with file/line citations
- **Intent check** — whether specs, ADRs, comments, or decision logs indicate the current shape is intentional, and how that source supports or constrains the candidate
- **Problem** or **Question to validate** — use **Problem** only when the evidence proves current friction; use **Question to validate** when the finding is plausible but not proven
- **Solution** — plain English description of what would change, including the rough interface shape
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram** — side-by-side, custom-drawn, illustrating the shallowness and the deepening
- **Recommendation strength** — one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge
- **Confidence** — `High`, `Medium`, or `Low`, based on the evidence gates above

Write for a reader who has not been living in the code:

- Candidate summaries must name the domain process or object, not only the architectural move. Prefer "Assemble signed evidence bundles through one interface" over "Make finalization a deeper interface".
- Do not use rhetorical concession patterns like "the seam is real, but..." or "the abstraction exists, but...". State the claim first, then give evidence.
- Intent checks must connect the source to the recommendation. Do not place two spec facts side by side and leave the reader to infer the relationship. Use the shape: "Because the spec requires X, this candidate must preserve Y; it can still change Z."
- Split dense claims. Put the main criticism in one sentence, then list or sequence the operations the caller currently performs.
- Preserve hierarchy. Group related operations instead of flattening everything into one comma list.
- Avoid vague verbs such as "absorb" when the sentence means "own", "keep outside", "move behind the interface", "return", or "persist".
- Expand local jargon the first time it appears in a report card. If a term like "finalization" names a domain stage, say what stage it is in the candidate title or summary.

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use CONTEXT.md vocabulary for the domain, and the `/codebase-design` vocabulary for the architecture.** If `CONTEXT.md` defines "Order," talk about "the Order intake module" — not "the FooBarHandler," and not "the Order service."

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007 — but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

**Intentional interfaces are not automatic problems.** Protocol libraries, low-level codecs, migration steps, and provider adapters often intentionally expose ordering or byte-level primitives. If a spec says the caller owns orchestration, the report must either respect that decision or explicitly frame the candidate as "reopen this decision because..." with evidence that the decision is now hurting callers.

See [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling guidance.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, call the Skill tool with "grilling" to walk the decision tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize — call the Skill tool with "domain-modeling" to keep the domain model current as you go:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing — skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Want to explore alternative interfaces for the deepened module?** Call the Skill tool with "codebase-design" and use its design-it-twice parallel sub-agent pattern.
