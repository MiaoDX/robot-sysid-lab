# Formal Lesson Content Rollout Plan

[中文版](course-content-rollout.zh-CN.md) · [Unified curriculum design](../lessons/course-design.md)

**Status: Phase 2 in progress, 2026-09-25.** This plan turns the agreed K/L curriculum design into learner-facing lesson pages. It does not authorize invented numerical results: an experiment lesson may describe a contract and exercise before its runner/report exists, but it may claim a result only after the local path produces checked evidence.

## Scope

The hardware H track is outside this rollout. Existing K0, K1, L0, and L1 remain the reference style and delivered evidence. The remaining content is delivered in five reviewable batches:

| Batch | Content | Completion boundary |
|---|---|---|
| 0 · contract | bilingual template, terminology, navigation, evidence wording | every new page follows the shared structure and distinguishes planned evidence from measured evidence |
| 1 · method bridge | K4, K5, K6, L0-E | knowledge pages are complete; L0-E has a frozen narrative contract before numerical implementation |
| 2 · actuator and observation | K2, K3, L1-O, elective L1-S | command/dynamics/measurement boundaries are explained and isolated experiments are scoped |
| 3 · structure | K7, L2, L3 | parameter semantics, coupled-leg evidence, and normal-contact limits are explained |
| 4 · whole robot | K8, L4 | route comparison and the bounded same-Oracle controller comparison are documented |
| 5 · scale and mismatch | L5, L6 | sharing choices and both structural-mismatch and cross-engine cases are documented |

## Shared authoring contract

Every learner-facing page contains these sections in this order:

1. failure and prediction;
2. system boundary, signal visibility, and necessary equation;
3. controlled comparison;
4. evidence reading guide;
5. exercise and answer guide;
6. limits and next lesson.

Knowledge pages cite existing lab evidence or label conceptual figures as examples. Computational pages add the Oracle/Student contract, fit/development/final-evaluation split, local command, and resource budget after the experiment is implemented. English and Chinese keep the same headings, equations, units, data boundaries, and claims.

## Execution loop

For each batch:

1. read the card in the unified design and identify any unresolved contract decision;
2. write the English and Chinese Markdown pages together;
3. render paired HTML and update the course map/status links;
4. run heading, bilingual, link, and terminology checks;
5. review the rendered pages using the batch's lesson IDs;
6. freeze the content contract and only then implement numerical experiments or optional interaction.

## Current slice

Phase 0 is complete and Phase 1 knowledge pages K4–K6 are delivered. Phase 2 has delivered K2, K3, L1-O, and elective L1-S as formal reading/contract pages; their numerical paths remain future work. L0-E remains the next companion experiment page and must not contain fabricated plots or measurements.

## Review gates

A batch is ready for the next one when:

- each page answers one question without relying on an unwritten chapter;
- the signal boundary and data split are explicit;
- every claim is either supported by an existing report or marked as planned;
- an exercise can be answered from the page's evidence;
- English and Chinese render with matching heading anchors;
- the relevant local link and site checks pass.

Per-lesson numerical tolerances, asset versions, simulator choices, and runtime budgets remain decisions for the corresponding individual review.
