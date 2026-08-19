---
name: slidev
description: Build, revise, and verify Slidev presentations as working web projects.
---

# Build Slidev Presentations

Treat the deck as a staged argument, not a document. Each slide carries **one beat**: one claim, question, example, comparison, or transition the audience can absorb before the speaker moves on.

## 1. Inspect the workspace and frame the talk

Classify the request before changing files:

- **Existing deck:** locate it, then read its `package.json`, entry Markdown, theme, styles, components, layouts, assets, and source material.
- **New deck:** enter this mode only when the user explicitly asks to create a new Slidev presentation or project. Invocation of this skill by itself is not permission to scaffold.

When the workspace contains no existing deck and the request does not explicitly ask for a new one, stop and ask the user to identify the deck. Do not scaffold a project, install Slidev, or create presentation files.

For an existing deck, preserve its visual system and package manager unless the user asked for a redesign or migration.

Establish these constraints from the request and available files:

- audience and what they already know;
- outcome: what the audience should understand, believe, or do;
- duration and whether demos or audience interaction consume time;
- delivery target: live browser, hosted SPA, PDF, PPTX, or a combination;
- tone, brand assets, accessibility needs, and required calls to action.

Infer constraints that the sources make clear. Ask only when a missing answer would materially change the deck. For an explicitly requested new deck, resolve its destination before scaffolding.

For claims not supplied by the user, verify them against primary sources and retain their URLs for a source line, speaker notes, or a references slide.

This step is complete when you can state the talk's promise in one sentence and name the delivery target.

## 2. Outline beats before slides

Write a slide inventory before polishing Markdown. Give each slide a claim, question, or purposeful transition rather than a topic label. Shape the sequence around the talk's needs; a useful default is:

1. create tension with the audience's problem;
2. make the central idea concrete;
3. prove it with examples, evidence, code, or a demo;
4. show the consequence or decision;
5. leave one memorable takeaway or action.

Use duration and interaction to size the deck; do not apply a universal slides-per-minute formula. Split a beat when its title needs "and", its visual has multiple focal points, or its content needs shrinking to fit.

Put nuance, transitions, citations, demo instructions, and fallback explanations in presenter notes. Slides carry the audience-facing beat; notes carry the speaker's route through it.

This step is complete when every required point has one place in the sequence and every slide has a reason to exist.

## 3. Establish the visual system with tracer slides

For an explicitly requested new deck, scaffold with Slidev's current official command and the chosen package manager. For syntax, project structure, feature choices, and current source links, read [references/authoring.md](references/authoring.md). Read it again when changing layouts, diagrams, export behavior, or MCP usage.

When a slide uses staged reveals, transitions, motion, code animation, Monaco, or a custom interactive Vue component, read [references/interactions.md](references/interactions.md) completely before implementing it. Use the smallest interaction that carries the beat, and apply that reference's state and export checks.

Build three **tracer slides** before the full deck:

- the cover, to prove identity and hierarchy;
- a representative content slide, to prove the normal rhythm;
- the most demanding code, data, or diagram slide, to prove the system under pressure.

Define a small visual language across those slides: a type scale, spacing rhythm, palette, code treatment, image treatment, and a handful of recurring layouts. Reuse the project's theme before inventing local abstractions. Scope global CSS under `.slidev-layout` so it does not leak into presenter UI.

Prefer one strong visual focal point. Turn lists into sequences, comparisons, diagrams, or separate beats. Use animation to control explanation order or compare states, and keep static content static. Keep code examples to the lines the audience must understand; import real snippets when drift from executable source would matter.

Run the dev server and inspect the tracer slides at presentation size. The visual system is ready only when all three are readable without clipping, emergency scaling, or layout exceptions that the remaining deck would repeat.

## 4. Author the full deck

Build the remaining slides from the approved visual language and beat inventory.

- Use local assets from `public/` when the deck must work offline or export reliably.
- Crop images intentionally and preserve their aspect ratios.
- Give code, diagrams, and data enough canvas to be the slide, not decorations beside prose.
- Use click reveals only when the speaker must control order. Check every meaningful click state.
- Keep citations legible on the slide when they support a visible claim; use notes or a references slide for longer provenance.
- Write presenter notes for transitions, timing, demos, pronunciations, and recovery paths.

If the Slidev MCP server is already connected, use its structured slide operations and live navigation where helpful. Direct file edits remain valid; do not pause the deck to configure MCP unless the user asked for that setup.

## 5. Run the rendered-slide loop

Keep the dev server running and inspect every slide full-size in sequence. Use live browser navigation, Slidev's MCP navigation when connected, or exported PNGs. Inspect every click state that changes meaning or geometry.

Check for:

- clipping, overflow, unintended scroll, and unsafe edge placement;
- type that becomes unreadable at presentation or export size;
- weak contrast, inconsistent alignment, accidental whitespace, and repetitive composition;
- broken code highlighting, diagrams, media, links, and remote assets;
- a sequence that stalls, repeats itself, or jumps without a spoken bridge;
- notes that merely repeat the slide instead of helping the speaker deliver it.

Fix issues and repeat the loop. After changing shared styles or layouts, revisit every affected slide. A source review or successful build does not replace this rendered review.

If the available browser or Playwright cannot launch, try an already-installed Chromium executable, Slidev's browser exporter, or another browser tool available in the harness. When none is available, report visual QA as blocked with the exact missing dependency. A successful build is still not evidence that the slides fit.

## 6. Validate and deliver

Use the project's scripts and package manager. At minimum:

1. run Slidev formatting when the project supports it;
2. run the production build;
3. if the deck contains Mermaid, call the Skill tool with `validate-mermaid` and fix every syntax error;
4. export the requested format and inspect that artifact;
5. rehearse the click order, notes, links, demos, and timing for a live deck.

CLI PDF, PPTX, and PNG export requires `playwright-chromium`. Install it in the deck project when export is part of the requested deliverable and the dependency is absent. Interactive features do not survive every export format, so provide static states or export click steps when the artifact depends on them.

Finish by reporting the deck entry, the command to present it, validation commands, exported artifact paths, and any assumptions or live-demo dependencies. Do not call the work complete until the production build passes and every delivered slide has been visually inspected after its last relevant change.
