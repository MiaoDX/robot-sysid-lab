# Robot SysID Lab Design System

## Direction

The course uses one visual mother system with restrained chapter variants. Content stays continuous across lessons; variation signals the job of a chapter rather than changing the product identity.

The visual reference is the coherent combination prototype in `docs/course/lesson-visual-styles.html?mix=1`.

## Stable Foundations

- **Canvas:** `#f7f8f6` paper, white content surfaces, `#eef3f5` soft fields.
- **Ink:** `#1f2937`; muted copy `#65717d`; rules `#d6ddd8`.
- **Typography:** system sans for body and display, CJK-safe fallbacks, monospace only for codes, lesson IDs, and technical values.
- **Geometry:** 8px maximum radius, 1px rules, restrained 0-3px shadows, no decorative card stacks.
- **Layout:** reading pages use a stable content column and a compact sticky contents rail; diagrams, tables, and callouts use the same spacing and border language.
- **Interaction:** links and controls use a single visible accent per chapter; focus rings remain high contrast; no motion is required to understand content.

## Chapter Variants

Each lesson inherits the stable foundation and may change only `--page-accent` and `--page-soft`:

| Chapter role | Accent | Typical lessons |
| --- | --- | --- |
| Orientation and boundaries | `#285f86` blue | K0, K1, K3 |
| Dynamics and prediction | `#1f7f83` teal | K2, K6, L2, L3 |
| Parameter meaning and comparison | `#6b6597` violet | K5, K7, L4, L6 |
| Experiment design and records | `#ad7435` amber | K4, L0, L0-E |
| Failure modes and diagnostics | `#c45c4d` coral | L1, L1-O, L1-S |
| Control, transfer, and review | `#27866d` green | K8, L5 |

Variants are accents, not new fonts, shadows, border radii, or page structures. The same rule applies to future hardware lessons.

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
