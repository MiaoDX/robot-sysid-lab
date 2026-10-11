# Robot SysID Lab Design System

## Direction

The course uses one visual system and one interface accent across lessons. Lesson numbers, headings, and content structure identify each chapter.

The exploratory styles in `docs/course/lesson-visual-styles.html` are not the production palette.

## Stable Foundations

- **Canvas:** `#f7f8f6` paper, white content surfaces, `#f1f1f1` soft fields.
- **Ink:** `#1f2937`; muted copy `#65717d`; rules `#d6ddd8`.
- **Typography:** system sans for body and display, CJK-safe fallbacks, monospace only for codes, lesson IDs, and technical values.
- **Geometry:** 8px maximum radius, 1px rules, restrained 0-3px shadows, no decorative card stacks.
- **Layout:** reading pages use a stable content column and a compact sticky contents rail; diagrams, tables, and callouts use the same spacing and border language.
- **Interaction:** links and controls use one shared blue accent; focus rings remain high contrast; no motion is required to understand content.

## Shared Accent

All course navigation, links, section markers, tables, and callouts use the shared ink black `#1f2937` with neutral `#f1f1f1` soft fields. Chapters and delivery states must be identified in text, not by a hue change.

Plots and video may retain distinct colors when those colors encode data roles such as observations and competing models. They do not set the page chrome color.

## Content Components

- Use a short eyebrow for lesson code and role.
- Use one clear page title, followed by a concise claim or question.
- Use tables for explicit comparisons, bordered flows for declared experiment boundaries, and callouts for exercises or limits.
- Keep diagrams and code blocks on the same paper/ink system. Do not draw fake browser or editor chrome.
- Keep generated Markdown as the content source of truth. CSS and the build script own presentation and page metadata.

## Reading Adaptation

The L0 reading page carries the visual language studied in
`ai-coding-resources/demos/visual-system/` into the existing document flow.

- Keep the paper canvas, restrained geometry, compact contents rail, and
  continuous reading layout.
- Use a short eyebrow, assertion-led section headings, one experiment-contract
  flow, evidence media frames, and bounded callouts to create visual rhythm.
- Keep model, initial model, and identified model colors consistent with the
  existing experiment media. Blue is the identified model, amber the initial
  model, and dark ink the observed system on light diagrams.
- Reserve any hand-drawn treatment for conceptual emphasis. Equations, tables,
  plots, and code stay precise.
- The optional bilingual L0 presentation prototype remains available for
  recording experiments, but it is not part of the primary lesson path.
- Markdown remains the source of the complete lesson; CSS owns the shared visual
  treatment and responsive behavior.

## Verification

After changing shared presentation, run `python tools/build_course.py --check`, render the course index and representative K/L pages at desktop and 390px widths, then run `git diff --check`.
