# Formal Lesson Content Rollout Plan

[中文版](course-content-rollout.zh-CN.md) · [Editorial principles](../lessons/course-editorial-principles.md) · [Unified curriculum design](../lessons/course-design.md)

**Status: Reading notes and experiment-design drafts published through Phase 5; approved media/evidence slice complete, 2026-09-26.** This plan turns the agreed K/L curriculum design into learner-facing lesson pages. It does not authorize invented numerical results: an experiment lesson may describe a contract and exercise before its runner/report exists, but it may claim a result only after the local path produces checked evidence.

## Approved media and evidence completion

Status: DONE, 2026-09-26. Owner: course-media-alignment (main session). The user approved the course/video review and its recommendations for execution with intuitive-flow. This section owns this task; the broader curriculum remains future work.

Goal: make course availability and media promises accurate, and complete the concrete teaching gaps identified in review.

Accepted scope and acceptance:

- [x] Distinguish reading notes, conceptual figures, teaching clips, reproducible experiments/reports, and independent learner acceptance in the bilingual course map/status. Record missing media explicitly for all 19 lesson pages.
- [x] Align delivery policy, editorial principles, curriculum, rollout and learner entry points. Static explanation and usable evidence are required; clips support named questions and must be marked available, planned, or not required with a reason. Page publication does not certify a complete experiment or video lecture.
- [x] Deliver and embed a data-backed L0 held-out clip and L1 friction clip with bilingual timed subtitles and written explanations. Reuse L0 iteration evidence in K5 and L1 delay/friction evidence in K3.
- [x] Deliver a frozen L0-E excitation comparison using L0 simulation/fitting code, a reproducible CPU command, coverage/sensitivity/loss/multistart/held-out evidence, bilingual report, and a teaching clip. K4 and L0-E must teach from these actual figures without claiming noise-free weak sensitivity guarantees parameter failure.
- [x] Give K2 a labelled conceptual single-joint diagram, torque decomposition/residual example, and units/derivation sufficient for its reading exercise.
- [x] Align existing L1 boundary subtitles to scene transitions; inspect other clips for the same timing issue and correct demonstrated mismatches.
- [x] Verify numerical invariants and leakage boundaries, regenerate bilingual HTML, run focused course/media tests, inspect actual new video frames and subtitle timing, and exercise the rendered site in a browser.

Route: execute the approved review directly, using three workers for numerical evidence, teaching media, and delivery documentation; the main session owns integration, site tests, canonical task state, verification and commits. Workers have disjoint file ownership. No GSD handoff is needed.

Non-goals: implementing L1-O/L1-S/L2-L6 or hardware experiments, full narrated lectures for every course, WASM deployment, independent human learner acceptance, or changing existing L0/L1 benchmark results. These remain explicitly recorded, not silently counted as complete.

Verification: reproducible L0-E runner and meaningful tests, existing numerical tests for reused contracts, `python tools/build_course.py --check`, course/media tests, ffprobe/frame inspection and browser checks. Stop when every accepted item has direct evidence and coherent owned changes are committed; external learner records cannot be fabricated.


Verification outcome (2026-09-26):

- `python -m pytest -q`: 65 passed. The inventory test checks all 19 lesson IDs against actual video embeds; bilingual tracks, local links, numerical recovery and estimator leakage boundaries pass.
- An independent full L0-E run reproduced the complete checked-in metrics JSON exactly in 8.89 seconds / 148.82 MiB peak RSS. The [report](../../reports/l0_excitation/report.md) and [runtime record](../../reports/l0_excitation/runtime.json) retain the frozen experiment and measured budget. Publication rejects custom contracts or results that cannot support the lesson's conclusions.
- `python tools/build_course.py --check`: 90 generated bilingual pages current. Browser checks covered the course map, matrix, K2–K7, L0, L0-E and L1 in both languages at 1280 px and 375 px; images/formulas loaded and page bodies had no horizontal overflow. Course navigation, language switching and K2's answer disclosure worked.
- All 10 unique clips are H.264, 1280×720, 30 fps, without audio; 20 subtitle files have matching bilingual timing within video/frame precision. Actual frames were reviewed. The three new clips and corrected L1 boundary clip played and sought correctly in both languages, with the selected subtitle below the video. Console errors/warnings were cleared and the affected pages rechecked after fixing one math punctuation warning.

Documentation alignment updated README, STATUS, the synthetic runner guide, delivery policy, curriculum and media matrix. Scope changes: none. Independent learner acceptance, advanced experiments, narrated lectures and WASM remain deferred under the non-goals above. Local browser/frame evidence is in ignored `artifacts/course-media-review/`; stable teaching artifacts are tracked with the lessons and reports.

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

1. review the learning question, prerequisite, boundary and intended evidence;
2. freeze the numerical contract, then implement and verify the local run for an experiment;
3. generate fixed figures and metrics, or explicitly labelled conceptual evidence for a knowledge lesson;
4. write both language pages, clips and exercises against that evidence;
5. inspect actual frames, subtitle timing, figures and exercise answers, then build and check the pages;
6. mark each delivery surface separately in the course status matrix. Optional browser interaction and independent learner acceptance remain separate.

Design drafts may be published before a run, but their promised evidence stays marked pending.

## Current slice

The published pages span the planned curriculum, but this does not complete the experiment ladder. The completed media/evidence slice added L0 held-out and L1 friction clips, a reproducible L0-E comparison and clip, K2 conceptual figures, and contextual reuse in K3–K7. L1-O, L1-S, and L2–L6 remain experiment-design drafts with their numerical evidence and clips pending. The [course matrix](../course/status.md) records each surface separately.

## Review gates

A batch is ready for the next one when:

- each page answers one question without relying on an unwritten chapter;
- the signal boundary and data split are explicit;
- every claim is either supported by an existing report or marked as planned;
- an exercise can be answered from the page's evidence;
- English and Chinese render with matching heading anchors;
- the relevant local link and site checks pass.

Per-lesson numerical tolerances, asset versions, simulator choices, and runtime budgets remain decisions for the corresponding individual review.
