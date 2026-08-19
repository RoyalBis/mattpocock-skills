## What it does

`slidev` turns a brief, source material, or an existing deck into a working Slidev presentation with a coherent story, speaker notes, and a verified browser or export artifact.

It treats the deck as something performed, not a document broken into pages. Every slide carries **one beat**, and the skill does not call the deck finished until the rendered slides have been inspected at presentation size.

## When to reach for it

You invoke this by typing `/slidev` — the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) won't reach for it on its own.

Reach for it when you want to create or revise:

- a conference or meetup talk;
- a technical walkthrough with code;
- a workshop or teaching deck;
- a live, hosted, PDF, or PPTX presentation built with Slidev;
- the story, visuals, animations, notes, or export behavior of an existing Slidev deck.

For a cited research artifact without a presentation, use [research](https://aihero.dev/skills-research). For a multi-session course that teaches the user rather than an audience, use [teach](https://aihero.dev/skills-teach).

## Prerequisites

Run it in an existing Slidev project. When you explicitly ask for a new presentation or project, you can instead run it in the directory where that project should be created. Invocation alone does not authorize scaffolding: without an existing deck or an explicit creation request, the skill stops and asks you to identify the deck.

It needs a compatible Node.js environment and may write project files such as `slides.md`, `styles/`, `components/`, `layouts/`, and `public/`, plus any requested exports.

## One beat per slide

A beat is one thing the audience has to absorb before the speaker moves on: a claim, question, example, comparison, or transition. Topic headings such as "Architecture" or "Results" do not say what the audience should notice. A claim heading does.

The skill outlines those beats before it polishes Markdown. Detail that helps the speaker but would crowd the audience's view goes into presenter notes. A slide that needs tiny text, multiple focal points, or "and" in its title is usually two beats.

Animation is staging for a beat, not decoration. The skill carries concrete patterns for click reveals, slide transitions, motion, code highlighting and morphing, Monaco editors, and custom Vue interactions. It also makes the agent define what happens when the presenter moves backward, re-enters the slide, or delivers a static export.

## Tracer slides before the whole deck

The skill first builds a cover, a representative content slide, and the hardest code, data, or diagram slide. These **tracer slides** prove the type, spacing, color, layout, and code treatment before that visual system is repeated twenty times.

Once they render cleanly, the remaining slides reuse the same language. This is the presentation equivalent of proving the risky path before filling in the routine work.

## The rendered-slide loop

Slide Markdown can compile while the actual presentation is unusable. The skill therefore checks every slide full-size, including meaningful click states, for clipping, tiny type, weak contrast, broken media, awkward whitespace, and narrative jumps. Shared style changes send affected slides back through the loop.

A production build is required, but it is not visual proof. The final gate is a rendered deck or export that has been looked at slide by slide.

## Common questions

**Slidev already publishes an agent skill. Why use this one?**

The [official Slidev skill](https://github.com/slidevjs/slidev/tree/main/skills/slidev) is a broad syntax and feature reference. This skill points to that primary material while adding an opinionated end-to-end workflow for narrative structure, tracer slides, speaker notes, and rendered QA. Both use the name `slidev`, so install one implementation rather than leaving duplicate skills for the same trigger.

**Do I need an existing Slidev project?**

No, but you must explicitly ask it to create a new presentation or project and name or approve the destination. If you invoke it from an unrelated repository without that request, it asks you to identify an existing deck and creates nothing.

**Can it build interactive slides, or only static decks?**

It can build staged reveals, transitions, code animations, editable or runnable Monaco examples, and custom Vue controls. The interaction must carry part of the explanation, and the skill tests forward navigation, backward navigation, re-entry, keyboard operation, and the requested export state rather than treating a successful build as proof.

**Can it produce PDF or PowerPoint?**

Yes. Slidev exports PDF, PNG, and image-based PPTX files. Static formats cannot preserve every browser interaction, so the skill checks whether click states need separate pages or a static fallback. CLI visual export requires `playwright-chromium`; the [official export guide](https://sli.dev/guide/exporting.html) carries the current options.

## It's working if

- You can describe the talk's promise in one sentence before the deck is fully authored.
- Every slide title tells the audience what to notice, rather than merely naming a topic.
- The cover, normal content, and hardest technical slide establish one reusable visual system.
- Presenter notes add timing, transitions, provenance, and recovery detail instead of repeating the slide.
- Animations advance the explanation, and interactive slides still make sense after backward navigation, re-entry, or static export.
- Every slide remains readable at presentation size and every meaningful click state has been checked.
- The production build passes and the requested export has been opened and inspected.

## Where it fits

`slidev` is a **reach-for-it-anytime standalone** for producing a presentation. [Research](https://aihero.dev/skills-research) can supply grounded source material before the deck is written, while [teach](https://aihero.dev/skills-teach) is the nearby alternative when the output should be a course for the user rather than a talk for an audience. When you are unsure which skill or flow fits, [ask-matt](https://aihero.dev/skills-ask-matt) routes across the whole set.
