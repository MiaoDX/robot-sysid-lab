# Course Delivery Task Split

This is the implementation backlog for the delivery policy. Tasks are ordered
by dependency. A later level should not start its browser packaging before its
static lesson and local numerical path are complete.

## Track A: close the current lessons

### A1. Static-first review

- Check that the L0 and L1 HTML pages explain the question, boundary,
  fit/validation split, evidence, limits, and local command without opening
  Marimo.
- Check every video link and report link from the lesson page.
- Add a short “When to use local mode” block to each lesson.
- Record the review URLs and any learner feedback in the verification records.

**Depends on:** existing L0/L1 pages and rendered clips.

### A2. Make WASM exports self-contained

- Package each lesson's local numerical module into the export, or refactor the
  lesson module so the export can inline it safely.
- Declare/install the browser dependencies (`numpy`, `scipy`, `matplotlib`, and
  any lesson-specific packages) through the supported Marimo/Pyodide path.
- Move lesson data/config files into the export's public data layout where they
  are needed.
- Add a repeatable export command and keep generated exports out of the source
  tree until the deployment layout is decided.

**Depends on:** A1; validated by the existing L0/L1 browser probes.

### A3. Bounded browser interaction

- Expose only one or two safe controls per lesson.
- Keep timeline, signal, and split selectors replay-only.
- Show loading, success, and failure states for browser fitting.
- Measure cold-start time, completed-run time, browser memory, and network
  failures on the supported browsers.
- Label the WASM page as an optional browser experiment and link to local mode
  for longer runs.

**Depends on:** A2.

### A4. Shared static deployment

- Place the static lesson pages, videos, reports, and optional WASM exports in
  one GitHub Pages tree.
- Deduplicate the common Marimo assets between L0 and L1 exports.
- Add a build/check job that verifies links, asset paths, and total published
  size without running a Python server.

**Depends on:** A2 and A3.

## Track B: repeat the pattern for the next lesson

### B1. Choose one bounded mismatch question

Use the next documented actuator effect, preferably friction or saturation,
only after stating why L1's delay lesson cannot answer it. Freeze the lesson
contract and the execution budget before implementation.

### B2. Local benchmark and report

- Build the CPU reference model, frozen config, fit/validation dataset, and
  focused leakage/numerical tests.
- Generate the report, metrics, and teaching visuals.
- Document the full local command and expected resources.

### B3. Static narrative and video

- Explain the new boundary and omitted effects in HTML.
- Produce videos for the failure mechanism and the validation evidence.
- Make the static page sufficient for a learner to understand the result.

### B4. Browser decision

- Run the WASM checklist against package support, dataset size, runtime,
  memory, and browser APIs.
- Choose one outcome explicitly: bounded WASM fit, WASM replay with local fit,
  or static-only browser surface.
- Record the decision and the reason in the lesson plan.

### B5. Local extension

- Add larger data, longer optimization, native simulator, or GPU instructions
  when the lesson needs them.
- Keep the local path on the same experiment contract as the static and WASM
  surfaces.

## Track C: scale beyond single-body lessons

### C1. Fixed-base leg (L2)

- Static/video lesson introduces coupling and parameter correlation.
- Browser surface shows precomputed trajectories, residuals, and small replay
  controls by default.
- Local simulator owns the fitting workload and larger data.

### C2. Contact (L3)

- Static/video lesson isolates contact as a new uncertainty class.
- Browser surface remains static or replay-only unless a toy contact case fits
  the bounded budget.
- Local simulator handles contact fitting and condition matrices.

### C3. Whole robot (L4/L5)

- Static/video pages explain component-first versus global fitting and show
  report summaries.
- Browser surface is a result explorer with precomputed artifacts.
- Local or scheduled CPU/GPU jobs handle fitting, caching, and large data.

### C4. Hardware track

- HTML/video carries safety, procedure, and interpretation.
- No hardware execution is offered from GitHub Pages or WASM.
- Local tools and controlled hardware services own acquisition and fitting.

## Cross-cutting verification task

For every lesson, retain three independent checks:

1. Static page and video links work with only an HTTP server.
2. The declared browser surface passes its cold-load and bounded interaction
   check, or the lesson explicitly has no WASM surface.
3. The local command reproduces the checked-in report and metrics.

The task is complete only when all three outcomes are recorded in the lesson's
verification document.
