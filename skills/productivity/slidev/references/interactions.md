# Slidev animations and interactions

Use motion to stage an explanation or expose a change in state. Every interaction should have a named job in the talk; prefer a static slide when the audience gains nothing from the state change.

## Contents

- [Choose the interaction](#choose-the-interaction)
- [Stage content with clicks](#stage-content-with-clicks)
- [Animate transitions and motion](#animate-transitions-and-motion)
- [Animate and run code](#animate-and-run-code)
- [Build custom Vue interactions](#build-custom-vue-interactions)
- [Keep notes and exports coherent](#keep-notes-and-exports-coherent)
- [Verify every state](#verify-every-state)

## Choose the interaction

| The beat needs | Use | Avoid adding |
| --- | --- | --- |
| An ordered explanation | `v-click`, `v-after`, or `v-clicks` | A new slide for every bullet |
| A temporary or replacing state | Click ranges or `v-switch` | Elements stacked invisibly in the same space |
| Continuity between slides | A slide transition | Continuous ambient motion |
| A code change | Line highlighting or Shiki magic-move | Two dense code blocks competing side by side |
| Audience-editable code | Monaco editor or runner | A live editor with no reset or fallback |
| A real control, simulation, or demo | A local Vue component | Rebuilding a native HTML control from scratch |

## Stage content with clicks

Use `v-click` for one reveal and `v-after` when two elements should enter on the same click:

```md
<div v-click>Parse the input</div>
<div v-after>Validate the boundary</div>
<div v-click>Commit the result</div>
```

Use `v-clicks` to reveal direct child items one at a time:

```md
<v-clicks>

- Parse
- Validate
- Commit

</v-clicks>
```

Position a reveal only when independent sequences must synchronize:

```md
<div v-click="2">Visible at click 2</div>
<div v-click="'+2'">Visible two clicks after the previous relative step</div>
<div v-click="[2, 4]">Visible at clicks 2 and 3</div>
<div v-click.hide="3">Hidden from click 3 onward</div>
```

Numbers are absolute positions. Strings beginning with `+` or `-` are relative positions. Click ranges use an exclusive end. Prefer automatic click counting; set `clicks` in slide frontmatter only when the slide deliberately needs a fixed total.

Use a built-in animation preset when the reveal needs direction:

```md
<div v-click.fade>Fade in</div>
<div v-click.fade.right>Fade in while moving right</div>
<div v-click.none>Reveal without motion</div>
```

Keep the order meaningful when moving forward and backward. An element that replaces another should not leave an empty click or an unreadable overlap.

## Animate transitions and motion

Set a deck-wide transition in headmatter or override it on one slide:

```md
---
transition: slide-left
---
```

Built-in transitions include `fade`, `fade-out`, `slide-left`, `slide-right`, `slide-up`, `slide-down`, and `view-transition`. Treat `view-transition` as progressive enhancement because browser support varies.

Use `v-motion` when an element's position or emphasis communicates the change:

```md
<div
  v-click="[1, 3]"
  v-motion
  :initial="{ x: -40, opacity: 0 }"
  :enter="{ x: 0, opacity: 1 }"
  :leave="{ x: 40, opacity: 0 }"
>
  This state is visible at clicks 1 and 2.
</div>
```

For click-specific motion, add variants such as `:click-1="{ y: 20 }"` or `:click-2-4="{ x: 40 }"`. Keep `v-click` and `v-motion` on the same element so click visibility controls the motion reliably.

## Animate and run code

Use line highlighting for one stable snippet whose focus changes:

````md
```ts {1|2-3|all}
const input = read()
const result = validate(input)
publish(result)
```
````

Use Shiki magic-move when the code itself changes. The outer fence in the Slidev file uses four backticks:

`````md
````md magic-move
```ts
const result = parse(input)
```
```ts
const result = parse(input).map(validate)
```
````
`````

Use Monaco only when editing or execution is part of the beat:

````md
```ts {monaco}
const message = 'Edit me'
```

```ts {monaco-run} {autorun:false} {showOutputAt:'+1'}
console.log('Run me')
```
````

Use `<<< @/snippets/example.ts {monaco-write}` only when the user explicitly wants the presentation to edit that file. It writes changes back to disk, so keep the target under version control or backed up.

Test Monaco against the actual delivery environment. Confirm dependencies and type acquisition work without relying on the author's cache, and provide a static code state when the requested export cannot preserve the editor.

## Build custom Vue interactions

Put reusable interactions in `components/`. Slidev auto-imports them by filename:

```vue
<!-- components/CounterDemo.vue -->
<script setup lang="ts">
import { ref } from 'vue'
import { onSlideEnter } from '@slidev/client'

const count = ref(0)

onSlideEnter(() => {
  count.value = 0
})
</script>

<template>
  <button type="button" @click="count++">
    Count: {{ count }}
  </button>
</template>
```

Use it directly in the deck:

```md
<CounterDemo />
```

Slide component instances are preserved across navigation. Reset or resume state intentionally with `onSlideEnter`, `onSlideLeave`, or `useIsSlideActive`; do not rely on mount and unmount for slide lifecycle. Keep controls keyboard-operable, visibly focused, and large enough to use while presenting.

Pass the current click to a component when its visual state should follow the talk rather than audience input:

```md
<ArchitectureDiagram :step="$clicks" />
```

## Keep notes and exports coherent

Synchronize presenter notes with click steps using click markers:

```md
<!--
Introduce the complete problem.

[click] Explain the parser.

[click] Connect validation to publishing.

[click:4] Land on the final state.
-->
```

For a static fallback, render interactive and print states separately:

````md
<RenderWhen context="main">

```ts {monaco-run}
console.log('Interactive in the browser')
```

</RenderWhen>

<RenderWhen context="print">

```ts
console.log('Static export state')
```

</RenderWhen>
````

Use `slidev export --with-clicks` when each click state must appear as a separate exported page. When the deliverable is a hosted deck, preserve the interaction and still define what viewers see before interaction, after interaction, and when the interaction fails.

## Verify every state

For every animated or interactive slide, check:

1. the initial state before any clicks;
2. every forward click, including simultaneous and replacing elements;
3. every backward click;
4. direct navigation or reload into the slide;
5. leaving and re-entering the slide;
6. presenter notes and click-marker synchronization;
7. keyboard focus and control operation;
8. the requested export or print fallback;
9. clipping and overflow in every geometry-changing state.

The interaction is complete when every reachable state has been rendered and the audience can still receive the beat if the live behavior is unavailable.

## Primary sources

- [Animations, click positions, motion, and transitions](https://sli.dev/guide/animations)
- [Shiki magic-move](https://sli.dev/features/shiki-magic-move.html)
- [Monaco configuration](https://sli.dev/custom/config-monaco)
- [Monaco runner](https://sli.dev/features/monaco-run.html)
- [Writable Monaco](https://sli.dev/features/monaco-write.html)
- [Components in slides](https://sli.dev/guide/component)
- [Slide lifecycle hooks](https://sli.dev/features/slide-hook)
- [Built-in components and `RenderWhen`](https://sli.dev/builtin/components.html)
- [Presenter-note click markers](https://sli.dev/features/click-marker)
- [Exporting click states](https://sli.dev/guide/exporting.html)
