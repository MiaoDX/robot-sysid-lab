# Lesson Delivery Policy

This policy separates a published reading page from a delivered experiment.
Every lesson must give the reader a static explanation and usable evidence for
the question it asks. A page existing in the repository is not, by itself, a
claim that the lesson has a runnable experiment or a teaching video.

## Delivery classes

| Class | Static explanation | Usable evidence | Local execution | Video rule |
|---|---|---|---|---|
| Knowledge / concept (K) | Required: question, boundary, derivation, exercise and limits | Required: a labelled conceptual figure or a cited/replayed lab result that lets the exercise be answered | Not required | Available when a clip answers a named question; otherwise mark planned or not needed with the reason |
| Runnable experiment (L) | Required: same contract plus fit/development/final split and local command | Required: checked report, metrics or plots from the declared run | Required for computational labs | Mark each named question available, planned, or not needed; a clip cannot replace the report |
| Experiment-design draft | Required: frozen question, boundary, observations, controls and acceptance criteria | Pending until a local run or accepted conceptual evidence exists | Planned | Planned only when a future clip has a named teaching question |
| Hardware proposal | Required: procedure, safety boundary and evidence plan | Pending until the hardware run is reviewed | Hardware service/local machine | Planned or not needed; do not imply hardware evidence |

The course map uses these classes as **Reading**, **Concept**, **Runnable**,
**Design draft**, and **Planned**. Each badge describes the available learning
surface; it does not mean that every delivery surface is complete.

## Shared evidence contract

The static page must stand on its own. It names the learning question, plant
boundary, signals visible to the fitter, the controlled comparison, the evidence
status, an exercise with an answer guide, and the limit or next experiment.
Each figure or number is labelled **recorded (simulated or hardware, explicitly stated)**, **replayed**, **conceptual**,
**planned**, or **diagnostic**. A conceptual figure can support a reading
exercise, but it cannot be described as a simulator result.

Computational labs additionally declare the Oracle/Student boundary, fit and
final held-out split, configuration, resource budget, reproducible command, and
the output path of the checked report. Evaluation-only and Oracle diagnostic
signals cannot enter fitting or model selection. A browser replay or video is a
view of evidence; it never silently reruns fitting and never replaces the
report.

## Video status

Video is an explanation surface, not a universal completion checkbox. For each
lesson, record every proposed clip beside the question it answers and choose
one status:

- **Available:** the checked MP4, subtitle tracks, and written explanation are
  present and the clip agrees with the report or clearly labelled concept.
- **Planned:** a clip is useful for a named question, but its source run or
  render is not complete. The page must remain understandable without it.
- **Not needed:** a clip would duplicate a static derivation or a compact
  figure; state that reason explicitly.

The map and [course status](course/status.md) keep this status for all 19 K/L
lesson IDs. Existing footage may be reused by another lesson only when the
reused clip's question and boundary are stated on that lesson page.

## Production order

1. Freeze the lesson contract: question, boundary, observations, Student,
   split, controls, evidence, omitted effects, and resource budget.
2. Build and verify the local numerical path for a runnable experiment. Keep
   the generated report and machine-readable metrics under `reports/<lesson>`.
3. Write the static page and its answerable exercise. Add a conceptual figure
   for a K lesson when no run is needed; label it clearly.
4. Decide whether a bounded browser surface is useful. WASM is optional and
   may only replay a completed result or run a bounded operation within the
   declared package, memory, and time budget.
5. Produce or reuse clips for named questions, then check both subtitle tracks,
   poster frames, links, and timing against the source scene.
6. Build paired English/Chinese HTML and run the static link, asset, and
   numerical checks. Human learner acceptance remains a separate gate.

## Browser and local boundaries

The static page and clips carry the explanation. A local CPU/GPU experiment is
the reference path for long fitting, native simulators, large data, and
hardware. A browser surface is an optional bounded adapter: controls that only
change a view read a completed run, while a fitting control must show its
runtime and completion state. Never promise a browser experiment merely because
Marimo or a WASM export is available.

## Execution gates

These are engineering guidelines, not hard platform limits:

| Result of the budget review | Delivery decision |
|---|---|
| Small pure-Python computation, short arrays, supported packages, interaction usually under a few seconds | Add WASM as a learner enhancement |
| Browser replay is useful but fitting is slow or data is sizeable | WASM shows precomputed results; local mode performs the fit |
| Native/GPU dependency, large memory use, long optimization, multiprocessing, or hardware access | Keep the full computation local/server-side; provide static explanation and available clips and optionally a WASM replay |

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

| Level | Static static explanation and available clips | WASM role | Full experiment |
|---|---|---|---|
| L0 inertia and damping | Core lesson and fixed report | Small fit and safe controls | Local CPU runner and notebook |
| L1 delayed servo and pendulum | Core lesson, machine explanation, and report | Small fit, replay, and residual views after packaging dependencies | Local CPU runner and notebook |
| L0-E/L1-O; elective L1-S | Isolated excitation, observation, or saturation comparisons | Optional bounded interaction after budget checks | Local CPU |
| L2 fixed-base leg | Core explanation; coupling clips planned after the run | Precomputed replay or tiny previews; no whole fit by default | Local simulator and fitting workflow |
| L3 contact | Core explanation; contact-failure clips planned after the run | Static evidence or replay only unless a bounded toy contact case qualifies | Local simulator with contact experiments |
| L4 Microduck | Core explanation, report summaries and clips where useful | Summary/replay surface | Local or scheduled whole-robot fitting |
| L5 Microban | Core explanation and scaling evidence | Optional result explorer | Local/GPU workflow |
| L6 structural and cross-engine mismatch | Both single-engine structural mismatch and a genuine cross-engine case | Fixed results or replay | Local reproduction with both backends |
| H hardware track | Safety and experiment procedure | No hardware execution in WASM | Local machine and hardware services |

This keeps the course readable and deployable while allowing the computational
work to grow without forcing every learner to download or execute the largest
experiment in a browser tab.

## Browser eligibility and surface verification

Add Marimo WASM only when all of these hold:

- required packages have Pyodide/WASM builds;
- local modules and public data can be bundled or fetched as static assets;
- a control answers a short learning question;
- measured default and worst-case runtime and memory fit the browser budget;
- the operation needs no GPU, native processes, shared memory or hardware;
- the explanation and result remain understandable if browser execution fails.

Prefer replay, parameter previews, short simulations and small fits. Declare
input/data size, backend packages, default and maximum runtime, peak memory, and
whether an operation is replay, instant, interactive or a job. Document the
local fallback command, dependencies, expected resources and report output.

Verify each delivered surface independently: open the static page with only an
HTTP server and check its evidence and clip links; for WASM, test a cold load,
one learner control, a completed interaction and console/network errors; for a
computational lab, reproduce the local report in the declared environment and
compare metrics. These engineering checks do not supply independent learner
acceptance.

## Definition of done

A lesson may be called **Runnable** only when its static package answers the
question, its declared evidence is usable and reproducible, and its limits are
visible. A clip may be **Available**, **Planned**, or **Not needed** independently
of that status. Independent learner acceptance, hardware validation, and future
WASM packaging remain explicit separate gates.
