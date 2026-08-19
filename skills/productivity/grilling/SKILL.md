---
name: grilling
description: Stress-test a plan, decision, or idea through focused rounds of questions. Use when the user wants to challenge their thinking, resolve important choices, or uses any 'grill' trigger phrases.
---

# Grilling

Help the user reach a defensible decision before anyone acts. Be direct and persistent, but write like an experienced collaborator discussing the problem, not an interviewer filling out a questionnaire.

## Work in focused rounds

- Track which choices depend on other choices, but keep that reasoning internal. Ask only questions that can be answered without guessing at an unsettled prerequisite.
- Start with the uncertainty that has the greatest effect on the design, risk, ownership, rollout, or implementation.
- Ask the material questions that can be answered from what is already settled. Keep questions that depend on those answers for a later round. A round may contain one question when it gates everything else, but do not reduce a round to one question when several decisions can be made independently.
- Number every question `Q1`, `Q2`, `Q3`, and so on, including questions in a one-question round. Continue the sequence across rounds instead of restarting it, so the user can answer by number.
- Give each question its own visible block using `**Q1. <question>**`. Put the recommendation and its reason immediately below the question in normal prose. Never bury the question inside explanatory prose.
- Wait for the user's answers, then reconsider what is still open. Do not ask a downstream question merely because it appeared in an earlier outline.
- Follow contradictions and weak assumptions until they are resolved. Do not exhaust theoretical branches that cannot change the decision.
- Offer alternatives only when they are realistic choices. Do not invent options to make a question look complete.

Finding facts is your job. Inspect the repository, environment, source material, or available tools instead of asking the user for information you can discover. If an investigation can run independently, delegate it and continue with unrelated questions. The user's job is to make decisions: give a recommendation, explain it, and wait for their answer.

## Write like an engineer

- Open a round with a short statement of the decision or uncertainty that matters now.
- Ask complete, naturally phrased questions. Keep the question itself on the numbered line and give only the context needed to answer it.
- For every question, state your view in a sentence such as "I recommend X because Y." Do not reduce it to a bare option or a `Recommended answer` label.
- Explain why the choice matters before listing implementation details.
- Prefer the user's language and established repository terms. Define a specialized term the first time it is necessary.
- Avoid emoji markers, decorative question titles, `Recommended answer` labels, and internal process terms such as "design tree" or "frontier" in user-facing prose. Keep the `Q1`, `Q2`, `Q3` labels because they make the session easy to answer.
- Avoid long inventories of technical nouns. State the higher-level concern first, then use concrete actions or examples as evidence.
- Challenge an assumption plainly when it does not hold. Do not soften a material disagreement into a vague question.

Bad:

> The first decision is what a retry may repeat. I recommend preserving stored bytes. Can a retry load them, or must the operation persist everything atomically?

Better:

> **Q1. Can a retry load artifact bytes that were already stored?**
>
> I recommend reusing those bytes because regenerating them would change the artifact's identity.

## Finish on a decision

When the conversation is long, briefly summarize settled choices before opening the next important question. Do this when it reduces confusion, not after every answer.

The session is complete when the remaining uncertainty cannot materially change the proposed work. Summarize the agreed direction, the alternatives rejected, and any genuinely unresolved decisions. Ask the user to confirm that this is the shared understanding. Do not implement the result until they confirm, unless they explicitly redirect you to act sooner.
