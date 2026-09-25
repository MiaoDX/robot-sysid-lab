# Project status and next steps

This file tracks changing delivery status, immediate work, and completion evidence. The [README](README.md) stays focused on the project purpose, architecture, and reading entry points.

**Snapshot: 2026-09-25.** L0 and L1 have executable Marimo lessons, inspectable
notebooks, CPU runners, and generated reports. L1 engineering gates pass;
independent learner acceptance remains open. Formal K/L reading pages now cover
K0–K8 and L0–L6 (including L0-E, L1-O, and L1-S); numerical implementations
for the newly added experiment pages remain pending.

## Current checkpoint

| Area | State | Evidence / interpretation |
|---|---|---|
| Knowledge and synthetic-lab direction | K/L formal reading rollout delivered through L6; later numerical paths remain pending | [Course map](docs/course/index.html), [rollout plan](docs/plans/course-content-rollout.md), [roadmap](docs/03_synthetic_lab_roadmap.md) |
| Oracle, whole-robot, and RL protocols | Documented; not implemented | [Experiment design](docs/04_oracle_sim_experiment_design.md) |
| Visualization and learning experience | K/L/H course map and guided L0 Marimo course delivered; Jupyter remains an inspectable lab surface | [course map](docs/course/index.html), [L0 lessons](docs/lessons/l0/README.md), [reporting](docs/05_visualization_and_reporting.md), [learning experience](docs/06_learning_experience.md) |
| Reusable lesson workflow | Documented as a contract; code extraction waits for a second lesson | [Lesson / Experiment Pipeline](docs/lesson_pipeline.md) |
| Benchmark rules | Documented reference | [Benchmark contract](docs/07_benchmark_contract.md) |
| L0 happy-path scope | Implemented and locally verified; independent learner signoff remains open | [First-lab contract](docs/08_happy_path_and_identifiability.md#2-first-happy-path-benchmark-one-default-experiment) |
| Original 1-DoF prototype | Removed in the design PR | No replacement runnable lab is claimed here |
| Example results and reproduction command | Delivered | [Interactive course](apps/l0_inertia_damping.py), [generated report](reports/l0_inertia_damping/report.md), [notebook](notebooks/l0_inertia_damping.ipynb), and [reproduction instructions](synthetic/README.md) |
| Learner walkthrough | Maintainer browser walkthrough passed; independent reader pending | [Walkthrough script](reports/l0_inertia_damping/verification.md#learner-acceptance-walkthrough) |

## Delivery rule

**Finish one experiment that can be seen, run, and explained before expanding the matrix.**

For the first delivery, Sections 2 and 17 of the happy-path document define the required scope. Earlier documents retain the long-term design, but their exhaustive model, observation, and visualization catalogs are not a cumulative checklist for L0. This is staged delivery, not removal of the broader plan.

No additional architecture chapter is needed before implementation. Resolve sample values, numerical tolerances, and small API choices in the implementation PR and record the decision with the example.

## Current delivery: L0 inertia and damping

The deliverable is one CPU-only lesson around `J*qdd + b*qd = u`: known applied torque, ideal `t/u/q/qd` observations, only `J` and `b` unknown, one matched Student with incorrect Initial-model parameters, one fit chirp, one held-out multisine, and one bounded nonlinear least-squares estimator.

The required output is **True system / Initial model / Identified model curves + parameters + fit/validation metrics + a readable explanation**. The explanation now lives in the [L0 lesson set](docs/lessons/l0/README.md) and the generated report links back to it. Coulomb friction, delay, sensors, RL, contact, and extra backends are deliberately absent. The [first-lab specification](docs/08_happy_path_and_identifiability.md#2-first-happy-path-benchmark-one-default-experiment) is authoritative for the detailed assumptions.

### Work in this order

- [x] **1. Freeze one runnable example configuration.** Set physical units, truth/nominal values, public bounds, initial state, excitation, timing, objective scaling, and expected tolerances. Explain the input boundary; do not add an unknown torque scale.
- [x] **2. Implement and check the numerical baseline.** Build the small CPU forward model and compare with the constant-input analytical reference. Include finite-output, invalid-input, zero-input dissipation, and numerical repeatability checks.
- [x] **3. Generate separated fitting and validation data.** Give the estimator only fitting observations and public metadata. Keep Oracle parameters in the generator/evaluator path. Record provenance; no hidden acceleration or validation-based retuning.
- [x] **4. Fit and evaluate.** Use one estimator, report its convergence/failure, compare `J` and `b` after fitting, and score the untouched validation motion. Add one lightweight fitting-data sensitivity diagnostic.
- [x] **5. Generate the visual lesson from that run.** Make a guided Marimo course the primary learner entry point, retain the Jupyter notebook for inspection, and add a Markdown lesson set around them. Produce before/after position and velocity overlays, applied input, time residuals, parameter comparison, and separate fit/validation metrics. Keep plots and numbers tied to one configuration.
- [x] **6. Provide complementary entry points.** Use Marimo for guided interaction, Jupyter for cell-level inspection, and a headless CPU path for CI and reproducibility. All entry points must use the same implementation and configuration; do not add placeholder commands or invented results.
- [ ] **7. Ask an independent colleague to try it.** Check that they can spot the nominal mismatch, reproduce it, explain the held-out result, change one setting, and state the assumptions. Capture feedback and fix confusing material.
- [ ] **8. Close L0 with evidence.** Link the implementation commit, exact example configuration, generated report, check output, and learner feedback here. Only then start the next lesson.

### Verification evidence

- Implementation: `86db325` introduced the numerical lesson; subsequent L0
  course and interaction work is included through `24d3922`.
- Frozen input: [`synthetic/l0_config.json`](synthetic/l0_config.json).
- Generated evidence: [`report.md`](reports/l0_inertia_damping/report.md),
  [`report.png`](reports/l0_inertia_damping/report.png), and
  [`metrics.json`](reports/l0_inertia_damping/metrics.json).
- CPU checks on 2026-09-16: `python -m pytest -q` passed 18 tests; the documented
  headless command regenerated the report and recovered `J = 0.065` and
  `b = 0.055`; notebook JSON validation passed.
- Maintainer browser walkthrough on Marimo 0.24.2: desktop and 375 px mobile
  layouts rendered without application console errors; changing Initial-model
  inertia from `0.095` to `0.120` updated both preview metrics and marked the
  Identified result stale; **Run identification** restored a current result.
  This verifies the interaction mechanics but does not count as the required
  independent-reader feedback.

The checklist follows the [engineering and learning acceptance criteria](docs/08_happy_path_and_identifiability.md#17-deliver-the-first-lesson-end-to-end). Marimo is the guided L0 visual surface, while the notebook and static report remain useful inspection and evidence surfaces. Do not block L0 on the renderer, deployment framework, or every future diagnostic.

## Then, not in parallel by default

The knowledge and synthetic-lab tracks advance together: each lesson explains a concept and demonstrates it against declared Oracle/Student data. Hardware and robot-derived experiments converge with that track after the synthetic L0/L1 contracts are working; they are application stages, not prerequisites for the first lesson.

| Order | Next step | Trigger |
|---|---|---|
| 1 | Add one model-mismatch lesson, preferably delay | L0 is reproducible and understandable; define the new boundary and timing assumptions |
| 2 | Build L1 synthetic actuator | Reuse the proven data/fit/report loop; add actuator effects one at a time |
| 3 | Fixed-base leg, then controlled contact | The component results have passed their scoped validation |
| 4 | Microduck, then Microban | The subsystem workflow works; scale the same reasoning to whole robots |

For later options and study questions, use the [full lab roadmap](docs/03_synthetic_lab_roadmap.md). Microban remains the designated small humanoid.

## Explicitly deferred

Broad Oracle distributions, complete sensor/timing ablations, optimizer leaderboards, automatic model selection, active SysID, counterfactual interventions, SysID-informed domain randomization, cross-engine studies, and hardware validation remain research directions. They are not first-lesson dependencies.

The complete FRF/landscape suite, synchronized robot video, ghost overlays, interactive labs, and documentation portal also retain their place in the [visualization](docs/05_visualization_and_reporting.md) and [learning](docs/06_learning_experience.md) plans. Implement them when the relevant lesson can use them, not before any lesson exists.

Package layout, storage format, tracking service, and web framework should be chosen to support the first experiment. Do not build a general orchestration platform first.

## Evidence and maintenance

L0 and L1 implementations and generated lessons are delivered; notebooks, reports,
configurations, and check output are linked in their delivery sections. The reusable workflow
contract and course-facing L0 lesson set are documented. Independent learner
feedback is the only remaining release-acceptance item.

Keep task state and completion evidence here. Keep the reusable lesson assumptions and acceptance criteria in the happy-path document, and long-term options in the roadmap. Update the snapshot when work changes; leave the README free of dates, percentages, implementation checklists, and claims of capabilities that only exist in the plan.

## Current delivery: L1 servo-loaded pendulum

L1 engineering implementation is delivered; **independent learner acceptance is
still pending**. The [lesson](docs/lessons/l1/README.md), [Marimo app](apps/l1_servo_loaded_pendulum.py),
[notebook](notebooks/l1_servo_loaded_pendulum.ipynb), and [report](reports/l1_servo_loaded_pendulum/report.md)
share the [frozen v2 config](synthetic/l1_config.json) and one analytical CPU
module. The declared hidden effect is torque-command delay after the full PD
law. The public fitter cannot receive Oracle config or validation observations.

Verification on 2026-09-17: **30 tests passed**, fresh CPU report reproduction and
notebook execution passed; default delay recovered at **0.080 s**. Held-out q
RMSE improves from **0.03085465 rad** to floating-point residual, and qd RMSE
from **0.49007 rad/s** to floating-point residual (both exceed the 90% gate).
Real browser checks at 320/768/1440 px verified explicit fit, stale controls,
recorded playback, all signal views, and no application console errors. Default
run: **0.176 s**. Marimo asset-preload warnings are documented; the earlier
missing-Marimo/browser and pytest import-path blockers are resolved.

```bash
python -m pip install -r requirements-dev.txt -r requirements-interactive.txt
python -m pytest -q
python -m synthetic.l1_servo_loaded_pendulum --output-dir reports/l1_servo_loaded_pendulum
python -m marimo run apps/l1_servo_loaded_pendulum.py --port 2719
```

The [verification record](reports/l1_servo_loaded_pendulum/verification.md)
contains clean-environment versions, commands, screenshots, and the gate audit.
Next action: obtain an independent reader's actual answers and feedback using
the [walkthrough](reports/l1_servo_loaded_pendulum/verification.md#learner-acceptance-walkthrough). Gates
1–6 and 8 pass; learning gate 7 stays open. Hardware-transfer claims, friction,
saturation, multibody/contact and framework extraction remain deferred by the
[plan](docs/plans/l1-servo-loaded-pendulum.md).
