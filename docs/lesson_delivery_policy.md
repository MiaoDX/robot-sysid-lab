# Lesson Delivery Policy

The learner-facing explanation should remain useful without running Python. Each
lesson therefore has a static core, an optional browser experiment, and a local
full experiment. The three surfaces share one experiment contract and one source
of numerical truth.

## Three surfaces

| Surface | Purpose | Required for every lesson | Execution boundary |
|---|---|---:|---|
| HTML and video | Explain the question, model boundary, experiment design, evidence, and limits | Yes | Static files on GitHub Pages |
| Marimo WASM | Give a small number of safe, immediate experiments | Optional | Python runs in the learner's browser |
| Local CPU/GPU experiment | Support long runs, large data, unsupported packages, and deeper exercises | Yes for computational labs | Learner's machine or a server |

The HTML and video carry the main narrative. A learner should be able to
understand the plant boundary, read the fit/validation evidence, and know what
to try next without opening Marimo. WASM adds a short feedback loop where it is
useful; it is not the canonical execution environment for the whole lab ladder.

## Task split for a new lesson

Every new lesson is split into these tasks, in this order:

### 1. Freeze the lesson contract

Write down the learning question, plant boundary, hidden Oracle effects,
observations, Student model, fit/validation split, learner controls, evidence,
and omitted effects. Add an execution budget before writing UI code.

The budget records:

- expected input and dataset size;
- package and backend requirements;
- default CPU runtime;
- worst-case learner-controlled runtime;
- peak memory estimate;
- whether the operation is replay, instant, interactive, or a job.

### 2. Build the local numerical path

Implement the importable CPU/GPU model, frozen configuration, dataset
generation, estimator, validation, report generation, and focused tests. The
local path is the reference implementation even when a browser version exists.

Long computation must be exposed as an explicit command or job-style workflow.
Presentation controls should read a completed run instead of silently fitting
again.

### 3. Produce the static lesson and video

Write the HTML lesson and render the teaching clips before adding optional
interaction. The static package must show:

- the physical or algorithmic setup;
- the model boundary and observations;
- what was fitted and what was held out;
- baseline versus identified behavior;
- the main residual or failure evidence;
- the limits of the result;
- the local command for the full experiment.

The generated report records one fixed run. It supports the lesson but does not
replace its explanation.

### 4. Classify the browser experiment

Add a Marimo WASM surface only when all of these are true:

- required packages have a Pyodide/WASM build;
- local modules and data can be bundled or fetched as public static assets;
- the control is useful as a short learner experiment;
- the default and worst-case run fit the browser execution budget;
- the experiment does not require GPU, native processes, shared memory, or
  hardware access;
- the result is still understandable if the browser run is unavailable.

The first WASM version should prefer replay, parameter previews, short
simulations, and small fits. It should not expose an unbounded optimizer or a
large dataset just because the local implementation supports it.

### 5. Add the local deep-dive path

Document the full experiment beside the lesson. This path may use a notebook,
the CPU/GPU command, a larger dataset, a native simulator, or a queued job. It
must state expected runtime, dependencies, output location, and how to reproduce
the report.

The local path is the extension point when a lesson grows beyond the browser
budget. It should reuse the same contract and configuration vocabulary as the
static and WASM surfaces.

### 6. Verify each surface independently

The release check has three parts:

1. Open the static HTML and confirm that the narrative, videos, links, and
   report evidence work without a Python process.
2. If a WASM surface exists, test a cold browser load, one learner control, one
   completed interaction, and console/network errors on supported browsers.
3. Run the local command in a clean environment and compare its result with the
   checked-in report and metrics.

## Execution gates

These are engineering guidelines, not hard platform limits:

| Result of the budget review | Delivery decision |
|---|---|
| Small pure-Python computation, short arrays, supported packages, interaction usually under a few seconds | Add WASM as a learner enhancement |
| Browser replay is useful but fitting is slow or data is sizeable | WASM shows precomputed results; local mode performs the fit |
| Native/GPU dependency, large memory use, long optimization, multiprocessing, or hardware access | Keep the full computation local/server-side; provide HTML/video and optionally a WASM replay |

Marimo documents a roughly 2 GB WASM memory ceiling and states that its browser
concurrency adapters do not provide true CPU parallelism. These make the second
and third delivery decisions important as the labs move from 1-DoF examples to
legs and whole robots. See the [Marimo WASM guide](https://docs.marimo.io/guides/wasm.html).

## Application to the lab ladder

The [unified design](lessons/course-design.md) owns lesson scope and
prerequisites. K lessons use static explanations, diagrams, and cited lab
results without an independent numerical implementation requirement. The table
describes delivery targets; H retains its earlier arrangements outside this
design round.

| Level | Static HTML/video | WASM role | Full experiment |
|---|---|---|---|
| L0 inertia and damping | Core lesson and fixed report | Small fit and safe controls | Local CPU runner and notebook |
| L1 delayed servo and pendulum | Core lesson, machine explanation, and report | Small fit, replay, and residual views after packaging dependencies | Local CPU runner and notebook |
| L0-E/L1-O; elective L1-S | Isolated excitation, observation, or saturation comparisons | Optional bounded interaction after budget checks | Local CPU |
| L2 fixed-base leg | Core lesson and videos explain coupling | Precomputed replay or tiny previews; no whole fit by default | Local simulator and fitting workflow |
| L3 contact | Core lesson and contact-failure videos | Static evidence or replay only unless a bounded toy contact case qualifies | Local simulator with contact experiments |
| L4 Microduck | Core lesson, videos, and report summaries | Summary/replay surface | Local or scheduled whole-robot fitting |
| L5 Microban | Core lesson, videos, and scaling evidence | Optional result explorer | Local/GPU workflow |
| L6 structural and cross-engine mismatch | Both single-engine structural mismatch and a genuine cross-engine case | Fixed results or replay | Local reproduction with both backends |
| H hardware track | Safety and experiment procedure in HTML/video | No hardware execution in WASM | Local machine and hardware services |

This keeps the course readable and deployable while allowing the computational
work to grow without forcing every learner to download or execute the largest
experiment in a browser tab.

## Definition of done

A lesson is ready to publish when:

- its static package answers the learning question by itself;
- its report and video use the same frozen configuration as the numerical path;
- its local experiment is reproducible and documents resource expectations;
- its WASM surface, when present, is explicitly marked as an optional bounded
  interaction;
- the lesson names the point at which learners should switch from WASM to local
  execution.
