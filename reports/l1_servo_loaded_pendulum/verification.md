# L1 implementation verification

Verified 2026-09-17 against the implementation, not the earlier scaffolding.
Engineering gates pass. **Independent learner acceptance remains open.**
The canonical scope is [the plan](../../docs/plans/l1-servo-loaded-pendulum.md).

| Plan gate | Evidence | Result |
|---|---|---|
| 1. Machine/state agreement | `test_replay_views_use_all_recorded_roles_without_running_models`: both splits, all three roles, four sample indices; checks SVG endpoint coordinates and recorded q/qd/tip velocity. Rendering and summary run with simulation/fitting disabled. Browser frame follows timeline and split. | Passed |
| 2. Numerical behavior | Full-PD delay regression, independent solve_ivp gravity reference, held-out q and qd RMSE reduction tests. Default validation q RMSE ≈ 0.03085465 rad and qd ≈ 0.49007 rad/s fall to floating-point residuals; threshold ≥ 90%. | Passed |
| 3. Delay evidence | Delay recovery 0.08000 s within 1 ms across independent starts; nine-point fit-only local loss slice, report calls delay effective and boundary-dependent. | Passed |
| 4. No leakage | Fitter accepts Observations and PublicModel; rejects Config; observations have exactly t/q_des/q/qd. Regression disables generator/config/evaluation entry points during fitting. Validation and privileged histories remain outside this API. | Passed |
| 5. Interaction semantics | Real Chromium flow below; Marimo dependency graph test separates submit from replay. | Passed |
| 6. Reproduction | Fresh venv full tests, report regeneration and executed notebook below. Metrics agree within 1e-8 absolute tolerance across tested library versions; report text identical. | Passed |
| 7. Learning | Four ordered lesson pages plus guided app and independent-reader checklist. Maintainer exercised controls and read the narrative. No independent reader's answers or feedback have been received. | **Open** |
| 8. Scope | Report, app and lesson state synthetic ideal observation, post-PD torque delay only, omitted real effects, no motor-electromagnetic/whole-robot simulation or hardware-transfer claim. | Passed |

## Commands and fresh CPU environment

From the repository root:

```bash
python -m pytest -q
python -m synthetic.l1_servo_loaded_pendulum --output-dir reports/l1_servo_loaded_pendulum
python -m json.tool notebooks/l1_servo_loaded_pendulum.ipynb >/dev/null
python -m marimo check apps/l1_servo_loaded_pendulum.py
```

Result: **30 tests passed**, report and notebook JSON regenerated/validated, no
Marimo check issues. The suite includes L0 regressions, L1 numerical/leakage/replay
contracts, and the optional Marimo dependency-graph check. There is no remaining
ROS import-path blocker when using the documented `python -m pytest` command.

Fresh environment reproduction:

```bash
python -m venv /tmp/robot-sysid-l1-clean
env -u PYTHONPATH /tmp/robot-sysid-l1-clean/bin/python -m pip install -r requirements-dev.txt -r requirements-interactive.txt
env -u PYTHONPATH /tmp/robot-sysid-l1-clean/bin/python -m pytest -q
env -u PYTHONPATH /tmp/robot-sysid-l1-clean/bin/python -m synthetic.l1_servo_loaded_pendulum --output-dir /tmp/l1-clean-report
env -u PYTHONPATH /tmp/robot-sysid-l1-clean/bin/python -m jupyter nbconvert --execute --to notebook notebooks/l1_servo_loaded_pendulum.ipynb --output l1-executed.ipynb --output-dir /tmp --ExecutePreprocessor.timeout=120
```

Fresh venv: **30 passed in 12.65 s**, executed notebook `/tmp/l1-executed.ipynb`
without a missing kernel. Both environments used Python 3.13.2 and Marimo 0.24.2.
Original environment: NumPy 2.4.0, SciPy 1.17.0, Matplotlib 3.10.8, pytest 9.0.2.
Fresh environment: NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2, pytest 9.1.1.
The fresh report's numerical JSON agrees within 1e-8 absolute tolerance; report
Markdown is byte-identical. PNG bytes differ across these renderer versions;
visual contents are the contract. Same-environment metrics regeneration is
covered by tests. Notebook execution emits an ipykernel transport warning; it
completes successfully. `env -u PYTHONPATH` isolates inherited ROS packages.

## Real browser walkthrough

Launch from root after installing `requirements-interactive.txt`:

```bash
python -m marimo run apps/l1_servo_loaded_pendulum.py --headless --port 2719
```

Browser: gstack Chromium fallback at `http://localhost:2719/`. Controls live in
Marimo shadow DOM; use shadow-piercing CSS selectors such as
`marimo-button button`, rather than relying on a flat document button search.

1. Initial state says **Not run**, completed run #0. Pressed Run identification.
   Run #1 succeeded at `2026-09-17T11:59:18.993+08:00`, elapsed **0.176 s**.
2. Used keyboard ArrowRight twice on Initial delay (0 → 0.010 s). Status became
   **Stale**; receipt and displayed completed baseline stayed at run #1.
3. Submitted again. Run #2 succeeded at `2026-09-17T11:59:20.064+08:00`, elapsed
   **0.166 s**. Completed Initial delay changed to 0.010 s. Identified delay
   remained 0.080 s. This is below the five-second Job-mode threshold.
4. Scrubbed timeline from 50% to 100%, switched validation → fit, selected
   Residual vs velocity. Frame changed from t=4 s to fit t=8 s; run #2 receipt
   and completion time stayed identical. Earlier pass also replayed t=0.080 s.
5. Selected Angular velocity, Torque diagnostics, Residual vs time, and Angle,
   then returned to validation. Each view rendered; receipt remained identical.
6. Checked 320, 375, 414, 768, and 1440 px widths. `body.scrollWidth` and
   `#App.scrollWidth` equaled the viewport width at every size. Fit/validation
   plots stack on narrow screens. The recorded frame values also appear as a
   readable HTML table below the machine diagram.
7. Final flow had **no application console errors or kernel-not-found errors**.
   Marimo emitted only warnings about its preloaded `gradient` and `noise`
   images being unused. Development restart connection warnings were cleared
   before this final pass and are not counted as the supported running flow.

Screenshots of the final replay surface:

- [320 px](browser-320.png)
- [768 px](browser-768.png)
- [1440 px](browser-1440.png)

## Privileged-signal contract

The public fitting interface receives only `t`, `q_des`, encoder position `q`,
and velocity `qd` derived from that ideal encoder. It cannot receive Oracle
parameters, the hidden delayed-command buffer, true actuator torque, the
validation observations, or validation metrics. The report labels torque and
delayed command as Oracle-only diagnostics whenever they are shown.

## Learner acceptance walkthrough

This is the human half of gate 7, and the maintainer/browser checks above do not
substitute for it. Ask an independent reader to complete these tasks without
implementation coaching, and record what they actually did — including the exact
wording that confused them. Do not mark a task complete merely because the
checklist was printed.

1. Point to the fixed base, servo axis/body, arm, payload, gravity arrow, and
   angle convention in the machine view. Explain that the geometry is a
   deterministic 2D teaching view and uses the same recorded `q` state as the
   plots.
2. Trace `q_des -> fixed PD -> delayed command -> actuator torque -> pendulum`.
   State where the delay is inserted and why a CAD or controller model can
   predict the wrong motion when timing is omitted.
3. Identify which trajectory is fit data and which is held out. Explain why the
   zero-delay Initial model can look plausible while accumulating phase error,
   and what improvement in Identified validation supports the fitted delay.
4. Change the Initial delay (or the excitation if exposed), predict what the
   orange baseline and residual should do, and press **Run identification**.
   Confirm that the prior blue result remains the result until the action runs.
5. Interpret one residual pattern: repeating signed lobes around reversals are a
   phase or timing clue; a residual correlated with velocity can arise from a
   time shift and does not by itself identify friction. Name at least three
   omitted effects and explain why this lesson does not establish hardware
   transfer.

If a reader misses a task, record the failed wording, revise the relevant page
or app copy, and repeat the task with another reader. This is evidence for the
lesson, not a pre-filled signoff. Record the answers here or in `STATUS.md`.
