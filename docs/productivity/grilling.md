## What it does

`grilling` is the conversation loop that stress-tests a plan, decision, or idea before anyone acts on it. It identifies which choices depend on others, starts with the uncertainty that matters most, and keeps questioning the proposal until the important assumptions are explicit.

It works in focused rounds. Each round contains the material questions that can be answered without first resolving another question in that round. Every question has a stable `Q1`, `Q2`, `Q3` label, so you can answer the round by number. The agent gives its recommendation and reasoning for each question, waits for your answers, then decides what still needs discussion.

## When to reach for it

Type `/grilling`, or the [agent](https://www.aihero.dev/ai-coding-dictionary/agent) reaches for it on its own when a task fits. It is the only [skill](https://www.aihero.dev/ai-coding-dictionary/skill) in the grilling family that is model-invoked, which is why you rarely type it: usually a skill you *did* type is running it for you.

Typing `/grilling` directly gets you the plain interview and nothing else. Where you want something more than that:

| What you have | Reach for |
| --- | --- |
| You aren't working in a working directory | [grill-me](https://aihero.dev/skills-grill-me) — the same [session](https://www.aihero.dev/ai-coding-dictionary/session), under a name the agent will never fire by itself |
| You are in a working directory | [grill-with-docs](https://aihero.dev/skills-grill-with-docs) — the same session, and it writes `CONTEXT.md` and ADRs as it goes |
| An effort too big to hold in one session | [wayfinder](https://aihero.dev/skills-wayfinder) — it charts a map and runs grilling inside the decision tickets |
| A question that talking cannot settle — how something should look or feel | [prototype](https://aihero.dev/skills-prototype) — build the throwaway version, then come back |
| A skill of your own that needs an interview | Invoke `/grilling` from it, rather than writing another interview |

## Focused rounds and who decides

Three ideas carry the skill.

First, question order follows dependency order. The agent keeps that map private and asks all material questions that can be decided now. If one answer will reshape the rest of the discussion, it may ask only that question; otherwise it should not hold back independent decisions merely to create a one-question rhythm. Later rounds are rebuilt from what you actually said rather than copied from a questionnaire prepared at the start.

Second, each question should sound like part of an engineering discussion while remaining easy to answer. Every question gets a visible `Q1`, `Q2`, `Q3` label, even when a round contains only one, and numbering continues across the session. The recommendation follows in natural prose. There are no mandatory emoji, decorative titles, or `Recommended answer` blocks.

Third, facts and decisions have different owners. Facts are the skill's job: it reads the [environment](https://www.aihero.dev/ai-coding-dictionary/environment), uses tools, or dispatches a [sub-agent](https://www.aihero.dev/ai-coding-dictionary/subagent) instead of asking you to investigate. Decisions are yours. The agent can recommend an answer and challenge your reasoning, but it must wait for you to decide. It does not act until it summarizes the shared understanding and you confirm it.

The honest limit is that question order remains the agent's judgement. It can still group two questions and later discover that one answer should have changed the other. When that happens, reopen the affected decision instead of preserving a stale answer for the sake of the format.

## What lives here and what lives in the wrappers

This page covers the mechanism. The things people most often want are documented one level up.

| Question | Where it is answered |
| --- | --- |
| Focused rounds, question order, recommendations, facts vs decisions | Here |
| How long a session should run, what to do with a question you can't answer by talking, how to avoid nodding along | [grill-me](https://aihero.dev/skills-grill-me) |
| What gets written to `CONTEXT.md`, what becomes an ADR | [grill-with-docs](https://aihero.dev/skills-grill-with-docs) |

## Common questions

**Can I go back to one question at a time?**
Yes, and a large part of the audience does. Add this to your global `CLAUDE.md`:

```
When grilling, ask one question at a time.
```

The round-based default is genuinely contested. Practitioners who read slowly, who work in a second language, or who use the sequential format as focus scaffolding all report the one-at-a-time rhythm is better for them, and the opt-out is supported rather than tolerated.

**Where did `/batch-grill-me` go?**
Into this skill. Round-based questioning shipped briefly as a separate skill, then moved into `grilling` itself, so everything built on the primitive — `grill-me`, `grill-with-docs`, `triage`, `wayfinder` — got it at once. There is no `batch-grill-me` to install. The current default asks the independently answerable questions together, and the `CLAUDE.md` line above changes that cadence to one at a time without removing the `Q1`, `Q2`, `Q3` sequence.

**Why not ask every available question in one round?**
Large question batches are difficult to answer and encourage the agent to preserve questions that your first answer has made irrelevant. Focused rounds keep the discussion efficient without forcing one-question-at-a-time interaction. Questions in one round should be independent; the next round is recomputed from your answers.

**It ran out of questions and started building.**
A confirmation gate exists precisely for this: the skill is not finished when it runs out of material questions, it is finished when it summarizes the decision and you say the understanding is shared. Weaker and faster [models](https://www.aihero.dev/ai-coding-dictionary/model) still break it by turning a couple of answers directly into a plan. If yours does it, the reliable fix is a line in your own `AGENTS.md` or `CLAUDE.md` telling the agent not to implement without permission.

**It answered its own questions instead of asking me.**
That is a bug in the run, not the intended behaviour, and it was the reason facts and decisions were separated in the skill's text. It shows up most when another skill runs `grilling` inside a resolve-this-ticket frame, where the surrounding task reads as licence to keep moving. The same constraint is why there is no async mode: people have asked for a variant that reads a GitHub issue and posts one consolidated decision memo, and that is a different skill, because a grilling session that nobody answers has produced the agent's opinion rather than yours.

**Can I cap the number of questions?**
There is no fixed cap, because the useful stopping point depends on the decision. Every question must still earn its place by being capable of changing the direction, risk, ownership, rollout, or implementation. Tell the agent to wrap up when the remaining uncertainty is acceptable. If a session is running very long, the scope is usually too large; split the work and stress-test the pieces separately.

**I installed `grill-me` on its own and nothing happens.**
`grill-me` is a one-line skill whose whole body is "run a `/grilling` session", so it needs this skill installed too. The same is true of `grill-with-docs`, which additionally needs [domain-modeling](https://aihero.dev/skills-domain-modeling). Installing the whole set avoids the problem; installing selectively means installing the primitives as well.

**`grill-with-docs` ran, but it never loaded `grilling`.**
A real and unfixed rough edge, reported across [harnesses](https://www.aihero.dev/ai-coding-dictionary/harness) and models: a skill that names another skill does not reliably cause that skill to load, and `grill-with-docs` names two. The tell is a session that asks everything at once with no recommendations attached — that is the model improvising an interview rather than running this one. Asking the agent directly whether it loaded `grilling` and `domain-modeling` usually recovers it.

## It's working if

- A round opens with the decision or uncertainty that matters now.
- It asks the material questions that can be answered now, and nothing in a round needs another question in that round answered first.
- Every question has a visible `Q1`, `Q2`, `Q3` label, with numbering continuing across rounds.
- Each recommendation explains why it is preferred instead of naming a bare option.
- Questions read like a conversation, without mandatory emoji or decorative template labels.
- Later rounds ask things the first round could not have asked.
- It goes and looks facts up — reading files, dispatching a sub-agent — rather than asking you something it could have found out.
- Research running in the background does not stall the round; only the questions that depend on it wait.
- It stops at the end and asks you to confirm the understanding is shared, instead of starting work.

## Where it fits

`grilling` is a **primitive**, not a step you schedule: the single source of truth for the questioning technique, kept in one place so every skill that needs it does not invent another interview format. [grill-me](https://aihero.dev/skills-grill-me) and [grill-with-docs](https://aihero.dev/skills-grill-with-docs) are its two user-invoked front doors, and `grill-with-docs` is where the main build chain begins, ahead of [to-spec](https://aihero.dev/skills-to-spec). [wayfinder](https://aihero.dev/skills-wayfinder) uses it to resolve decision tickets, [triage](https://aihero.dev/skills-triage) to turn a vague report into a workable one, and [improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) after you pick a candidate. When you are unsure which entry point fits, [ask-matt](https://aihero.dev/skills-ask-matt) routes you.
