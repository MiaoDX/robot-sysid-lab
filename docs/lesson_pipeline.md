# Lesson / Experiment Pipeline

Each lesson is a small, repeatable unit that teaches one system-identification
question and leaves behind enough evidence for another engineer to reproduce
it. The pipeline is deliberately a contract first. Shared Python abstractions
should be extracted only after a second lesson proves that a boundary is truly
repeated.

## The lesson contract

Every lesson declares these items before implementation:

| Contract item | Required question |
|---|---|
| Learning question | What should a beginner be able to explain after the lesson? |
| Plant boundary | What system is being identified, and what is outside it? |
| Oracle | Which hidden truth generates the data? |
| Observations | Which signals does the estimator receive? |
| Student model | Which structure and parameters may be fitted? |
| Experiment split | What is used for fitting, and what is held out? |
| Execution policy | Is this an instant calculation, interactive wait, or background job? |
| Learner control | Which one or two safe settings can be changed? |
| Evidence | Which curves, metrics, and diagnostics answer the question? |
| Limits | Which real effects are intentionally absent? |

The contract prevents a lesson from silently changing its model, data boundary,
or validation meaning while its narrative remains the same.

## The shared flow

```text
frame question
  -> freeze versioned configuration
  -> generate Oracle fit and validation observations
  -> fit the declared Student using fit observations only
  -> evaluate baseline and identified models on fit and held-out data
  -> inspect diagnostics and failure conditions
  -> explain the evidence in a lesson
  -> package a notebook, headless command, report, and checks
```

The computation has one source of truth: an importable Python module. The
lesson text explains the reasoning, the notebook or a future Marimo app is a
learner-facing adapter, and the static report records one reproducible run.
None of those presentation surfaces should reimplement simulation or fitting.

## Execution policy

Lessons keep calculation separate from result exploration. A completed
`ExperimentRun` is the boundary between them: fitting produces the run, while
plots, metric selection, joint selection, timelines, and camera controls read
it without silently fitting again.

Choose one execution policy for every learner control that changes the
experiment:

| Policy | Expected wait | Interaction |
|---|---:|---|
| Instant | under about 200 ms | recompute reactively after a control changes |
| Interactive | about 0.2-5 s | show running, success, and failure state in the page |
| Job | longer or remotely scheduled | submit work, return a job ID, show progress and cancellation, then load the completed run |

Controls that only change presentation never submit computation. Changing from
fit to validation, selecting a joint, scrubbing time, or switching a residual
view should reuse the same run. A complex Oracle dataset should normally be
prepared and cached once; fitting jobs consume its reference rather than
regenerating the Oracle on every page interaction.

For a machine leg or whole robot, the eventual flow is:

```text
prepare_experiment(spec) -> immutable dataset reference
submit_fit(dataset reference, Student, estimator) -> job ID
observe job -> progress / failure / completed ExperimentRun
select views from ExperimentRun -> plots, rollouts, metrics, report
```

This is a behavioral contract, not yet a shared queue API. Implement the job
boundary when a concrete actuator or leg lesson first exceeds the interactive
budget, so its retry, cancellation, cache, and worker requirements come from a
real workload.

## Artifact contract

A completed lesson produces:

```text
docs/lessons/<track>/<lesson>.md       narrative and exercises
synthetic/<lesson>.py                  shared numerical implementation
synthetic/<lesson>_config.json         frozen example configuration
notebooks/<lesson>.ipynb               visual learner entry point
reports/<lesson>/report.md             explained run result
reports/<lesson>/report.png            static visual evidence
reports/<lesson>/metrics.json          machine-readable metrics and provenance
tests/test_<lesson>.py                 focused numerical and contract checks
```

The report is not a replacement for the lesson. It answers “what happened in
this run”; the lesson answers “why did we run it, how should I read it, and
what should I try next?”.

## Acceptance gates

An experiment can move to the next lesson only when it has:

1. **Numerical evidence:** the declared estimator runs, the fit/validation
   split is preserved, and the result meets the lesson's recovery or behavior
   criteria.
2. **Reproduction evidence:** a clean CPU command regenerates the report, and
   the visual entry point uses the same implementation and configuration.
3. **Learning evidence:** a reader can identify the baseline mismatch, explain
   the held-out result, change one exposed setting, and name the main limits.
4. **Scope evidence:** the report states what is absent, so later model
   complexity is introduced because a failure requires it.

## Presentation surfaces

Jupyter remains an inspectable L0 surface. The current Marimo preview demonstrates
reactive controls while calling the same numerical implementation: changing a
nominal parameter performs an instant fit, while switching fit/validation only
selects another view from the completed run. Quarto or MkDocs can host the lesson
prose when the lesson set grows, while generated reports remain useful as
immutable run artifacts.

## L0 mapping

The L0 set uses the contract as follows:

| Lesson | Question | Evidence |
|---|---|---|
| Orientation | What are plant, input, output, and parameter? | model boundary and units |
| Physics to data | How do `J` and `b` shape motion? | Oracle versus nominal curves |
| Fit to validation | Did fitting recover useful behavior? | parameter recovery and held-out metrics |
| Assumptions | Where does this result stop applying? | omitted effects and next-step delay lesson |

The next model-mismatch lesson should use the same headings and artifact layout.
Only after that comparison should repeated data structures be promoted into a
shared `ExperimentRun` or `run_experiment(...)` API.
