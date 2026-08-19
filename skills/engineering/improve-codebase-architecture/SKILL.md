---
name: improve-codebase-architecture
description: Scan a codebase for places where callers carry too much implementation complexity, present architectural candidates as a visual HTML report, then explore the candidate the user selects.
---

# Improve Codebase Architecture

Surface architectural friction and propose changes that place substantial behaviour behind a small interface. Use deep-module principles to evaluate the design; explain the result in direct engineering prose. The aim is testability and AI-navigability.

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- Call the Skill tool with "codebase-design" for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real"). Use the concepts accurately, but do not force every term into every suggestion. Prefer the project's domain language and concrete verbs when they make the point more clearly.
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
- **Target design** — enough shape to show the proposed module could actually take responsibility for the work: the module or type to introduce or change, its primary public operation, major inputs, return value, what it owns, and what remains with the caller. Use a small interface sketch when it makes the change clearer.
- **Implementation path** — for a non-trivial recommendation, identify the short sequence of code changes that gets from the current design to the target design, including caller and test migration and any public helpers that should be narrowed or removed.
- **Expected outcome** — state what callers no longer need to know and what code or tests can verify after the change.
- **Alternatives** — when meaningful choices exist, compare the strongest realistic alternatives and explain why the recommendation is preferable. Do not invent alternatives to fill a format.
- **Failure and retry decisions** — when an operation creates non-reproducible output, changes identity, calls external infrastructure, or leaves partial work, identify what must survive a retry and which failures the interface must define.
- **Testing payoff** — identify the test seam that improves and which current tests or test helpers would disappear or simplify.

Do not turn vocabulary matching into proof. Seeing "Sealer", "manifest", "adapter", or "interface" in code does not by itself prove a bad seam. If the evidence is plausible but incomplete, present it as a **Question to validate**, not as a **Problem**.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/architecture-review-<timestamp>.html` so each run gets a fresh file.

Before serving the report, call the Skill tool with "validate-mermaid" and validate the absolute report path with Mermaid 11.16.1. The compatibility command `python3 scripts/validate-report.py <absolute-report-path>` delegates to that skill's validator when a direct Skill tool call is unavailable. If `validate-mermaid` is not installed, stop and tell the user instead of skipping validation. Fix every reported diagram and rerun validation until it succeeds. Do not serve a report with unvalidated Mermaid syntax. Pin the report's Mermaid CDN import to the same exact `11.16.1` version; do not use a floating `@11` URL.

Make the report reachable from the user's browser. Run `python3 scripts/serve-report.py <absolute-report-path>` from this skill's directory as a long-running process. The script chooses a free port and prints a tokenized `REPORT_URL=http://localhost:<port>/<token>/`; give that URL to the user, followed by the absolute file path as a fallback. Keep the server running while the user reviews the report. If the harness cannot run the bundled script, use an equivalent single-file local server that does not expose the rest of the temp directory.

Opening the file directly is optional. Use `xdg-open`, `open`, or `start` only when a desktop session is available, and never treat a successful opener exit code as proof that the user can see the report. Do not finish with only a temp-file path.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals — use Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something more editorial (mass diagrams, cross-sections, collapse animations). Each candidate gets a **before/after visualisation**. Be visual.

Lead each substantial candidate with a concise statement of the proposed change. The reader should know what to add, move, replace, or consolidate before reading the supporting context. If the evidence is incomplete, lead with the concrete question or experiment needed to validate the idea instead of presenting an unearned recommendation.

Each candidate must cover the following material, but it does not need to expose these items as a fixed series of headings. Use sections when they help the reader scan the argument; combine them when a short narrative is clearer.

- State the proposed change in the title, summary, or first recommendation callout.
- Explain the current architectural problem at the highest useful level, then use implementation details and file/line citations as evidence.
- Show a concrete target design. Name the module or type, its primary public operation, major inputs, return value, responsibilities it owns, and responsibilities that deliberately remain with the caller. Include a small API sketch when it materially improves clarity.
- For non-trivial work, give a short implementation path: introduce or change the module, move responsibilities, migrate callers and tests, then narrow obsolete public helpers where evidence allows it.
- State the expected outcome as an observable property of callers, code, or tests.
- Include realistic alternatives when there is a meaningful design choice, then say why the recommended option wins.
- Identify unresolved design decisions separately from the recommended work. Cover failure and retry semantics when regenerated output, external calls, or partial persistence can change protocol identity or observable behaviour.
- Explain whether specs, ADRs, comments, or decision logs make the current shape intentional, and how that intent constrains the proposal.
- Explain what becomes simpler for callers and tests, and what implementation knowledge moves into one place.
- Include a side-by-side **Before / After diagram** that illustrates the current friction and the proposed change.
- Show recommendation strength (`Strong`, `Worth exploring`, or `Speculative`) and confidence (`High`, `Medium`, or `Low`).
- Include the deletion-test reasoning somewhere in the argument, without treating it as ceremonial proof.
- Name the files and modules involved.

Write for a reader who has not been living in the code:

- Let the architectural argument determine the structure. Lead with the proposed change, explain the current problem and why the change solves it, then use implementation details and repository references as evidence.
- Candidate summaries must name the domain process or object, not only the architectural move. Prefer "Assemble signed evidence bundles through one interface" over "Make finalization a deeper interface".
- Prefer an active recommendation such as "Add a `CompletionFinalizer` that owns Evidence Bundle assembly behind `Finalize(...)`" over "This responsibility should move into exosign."
- Do not use rhetorical concession patterns like "the seam is real, but..." or "the abstraction exists, but...". State the claim first, then give evidence.
- Connect intent sources to the recommendation, but do not let citations drive the grammar. Avoid a run of sentences that begin "Because X says...". State the design constraint naturally, then cite the source that establishes it.
- Put the high-level criticism before implementation detail. For example, explain that callers orchestrate an entire protocol before listing the steps that demonstrate it.
- Preserve hierarchy. Group related operations instead of flattening everything into one comma list.
- Prefer verbs and concrete actions over compressed noun phrases. Say "callers hash the stored bytes" rather than "stored-byte hashing" when the action matters.
- Avoid shorthand such as "deepen the module", "one narrower entry point", or "leverage: one caller interface" when a direct explanation would be clearer.
- Explain benefits in complete thoughts. Describe what callers no longer need to coordinate, where the implementation knowledge now lives, and how tests exercise the behaviour.
- Make outcomes testable. State what the caller should provide, what it should receive, and which implementation facts it should no longer need to understand.
- Separate recommended changes, optional improvements, alternatives, and unresolved decisions. Do not let an open retry or persistence question blur the parts of the design that are already supported by evidence.
- Treat failure semantics as architecture when retries can regenerate bytes, repeat external effects, or leave partially persisted output. Ask what data survives, what can safely be repeated, and what remains outside the operation.
- Keep sentences concise, but do not reduce reasoning to labels or fragments. A few connected sentences are better than a dense inventory of specialist nouns.
- Expand local jargon the first time it appears in a report card. If a term like "finalization" names a domain stage, say what stage it is in the candidate title or summary.

End the report with a **Top recommendation** section that states the implementation decision, why it should come first, the expected result, and any open decision that must be resolved before coding.

**Use CONTEXT.md vocabulary for the domain, and use the `/codebase-design` vocabulary when it adds architectural precision.** If `CONTEXT.md` defines "Order," talk about "the Order intake module" rather than inventing a generic name. Do not stack glossary terms where plain language communicates the same reasoning more naturally.

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007 — but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

**Intentional interfaces are not automatic problems.** Protocol libraries, low-level codecs, migration steps, and provider adapters often intentionally expose ordering or byte-level primitives. If a spec says the caller owns orchestration, the report must either respect that decision or explicitly frame the candidate as "reopen this decision because..." with evidence that the decision is now hurting callers.

See [HTML-REPORT.md](HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling guidance.

Do not make the interface sketch implementation-ready or settle low-level types prematurely. Make it concrete enough to evaluate ownership, caller experience, migration work, and failure semantics. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, call the Skill tool with "grilling" to work through the unresolved choices with them: constraints, dependencies, the shape of the proposed module, what it owns, and which tests survive.

Side effects happen inline as decisions crystallize — call the Skill tool with "domain-modeling" to keep the domain model current as you go:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing — skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Want to explore alternative interfaces for the deepened module?** Call the Skill tool with "codebase-design" and use its design-it-twice parallel sub-agent pattern.
