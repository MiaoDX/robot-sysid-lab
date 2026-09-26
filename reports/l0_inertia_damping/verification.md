# L0 implementation verification

Verified 2026-09-16/17 against the implementation. Engineering checks pass.
**Independent learner acceptance remains open.** The canonical scope is the
[first-lab contract](../../docs/08_happy_path_and_identifiability.md#2-first-happy-path-benchmark-one-default-experiment),
and changing delivery status is recorded in [STATUS.md](../../STATUS.md).

This file holds the material an implementer or verifier needs. The
[lesson set](../../docs/lessons/l0/README.md) is the learner-facing path and
does not repeat it.

## Evidence

| Area | Evidence | Result |
|---|---|---|
| Numerical baseline | `python -m pytest -q`; forward model compared with the constant-input analytical reference; finite-output, invalid-input, zero-input dissipation, and repeatability checks | Passed |
| Recovery | Documented headless command regenerates the report and recovers `J = 0.065`, `b = 0.055` | Passed |
| Reproduction | Report, `report.png`, and `metrics.json` regenerate from the frozen config; notebook JSON validates | Passed |
| Interaction | Maintainer browser walkthrough on Marimo 0.24.2: desktop and 375 px layouts rendered without application console errors; changing Initial-model inertia from `0.095` to `0.120` updated preview metrics and marked the Identified result stale; **Run identification** restored a current result | Passed |
| Learning | Lesson set, guided app, and independent-reader checklist exist; no independent reader's answers have been received | **Open** |

The maintainer browser walkthrough verifies the interaction mechanics only. It
does not count as the required independent-reader feedback.

## Commands

```bash
python -m pip install -r requirements-dev.txt -r requirements-interactive.txt
python -m pytest -q
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
python -m marimo run apps/l0_inertia_damping.py --port 2718
```

If a ROS shell exports `PYTHONPATH`, prefix these commands with `env -u PYTHONPATH`
to keep system plugins out of the environment.

## Privileged-signal contract

The fitting API receives observations (`t`, applied torque `u`, position `q`,
velocity `qd`) and the public parameter bounds. It cannot receive the Oracle
parameters, the validation split, or validation metrics. The reported run keeps
Oracle truth in the generator and evaluator path only.

## Learner acceptance walkthrough

This is the human half of the acceptance criteria. Use it with a reader who did
not implement L0, and record their answers and any confusing point rather than
marking the checklist complete.

1. Before fitting, point to where the orange Initial model first separates from
   the black True-system curve.
2. Regenerate the default run and explain which two parameter values fitting
   changed.
3. Explain why the chirp is fitting data and the multisine remains held out
   until evaluation.
4. Change one Initial-model slider, predict the orange curve's response, and
   then press **Run identification**. Confirm that blue remains the previous
   result until the button is pressed.
5. Name at least three omitted effects and explain why this matched, noise-free
   result does not establish transfer to a real robot.

A pass requires all five tasks without implementation-author coaching. Treat a
miss as lesson feedback: record it, improve the relevant explanation, and repeat
the missed task with another reader.