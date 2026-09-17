# L1: Servo-driven loaded pendulum

L1 adds one machine-shaped mismatch to the complete L0 loop. A fixed base holds
a rotary arm and known point payload. A position command `q_des` passes through
a fixed PD controller; the controller torque command is delayed before it drives
the gravity-loaded pendulum. The delay is an **effective parameter of this
command boundary and sampling setup**, not a motor electromagnetic time
constant.

## Learning path

Read the pages in order while keeping the [fixed report](../../../reports/l1_servo_loaded_pendulum/report.md)
open:

1. [Meet the machine and the question](00-orientation.md)
2. [From command to delayed torque](01-command-to-torque.md)
3. [Fit, validation, and residual phase](02-fit-validation-residuals.md)
4. [Exercise, limits, and the bridge to L2](03-exercise-and-limits.md)

The [notebook](../../../notebooks/l1_servo_loaded_pendulum.ipynb) exposes the
run artifact and plotting functions cell by cell. The [Marimo app](../../../apps/l1_servo_loaded_pendulum.py)
is the guided path. Install its optional dependencies and launch it from the
repository root:

```bash
python -m pip install -r requirements-interactive.txt
python -m marimo run apps/l1_servo_loaded_pendulum.py --host 0.0.0.0 --port 2719
```

The app has one fit-affecting control, **Initial delay**, and an explicit
**Run identification** action. Changing that control marks the completed result stale; the displayed orange
baseline changes only when the new setup is submitted. It must not imply a new fit until
the action is pressed. Timeline, split, and signal controls replay the
completed run and do not submit work.

For a headless reproduction, install the CPU development environment and run:

```bash
python -m pip install -r requirements-dev.txt
python -m synthetic.l1_servo_loaded_pendulum \
  --output-dir reports/l1_servo_loaded_pendulum
python -m json.tool notebooks/l1_servo_loaded_pendulum.ipynb >/dev/null
```

For a fresh CPU environment, create `python -m venv /tmp/robot-sysid-l1-clean`
and use `/tmp/robot-sysid-l1-clean/bin/python` for the commands above. If a ROS
shell exports `PYTHONPATH`, prefix these commands with `env -u PYTHONPATH` to
keep system plugins out of the environment. Numerical outputs across library
versions use 1e-8 absolute tolerance; PNG bytes may vary with rendering libraries.

The command reads the checked-in configuration and writes `report.md`,
`report.png`, and `metrics.json`. It is deterministic within the documented
floating-point tolerance and does not require ROS, a GPU, or a simulator
backend.

## What the estimator can see

The public fitting interface receives only `t`, `q_des`, encoder position `q`,
and velocity `qd` derived from that ideal encoder. It cannot receive Oracle
parameters, the hidden delayed-command buffer, true actuator torque, the
validation observations, or validation metrics. The report labels torque and
delayed command as Oracle-only diagnostics whenever they are shown.

## Learner acceptance walkthrough

Ask an independent reader to complete these tasks without implementation
coaching. Record what they actually did and any confusion in the project
closeout record; do not mark a task complete merely because the checklist was
printed.

1. Point to the fixed base, servo axis/body, arm, payload, gravity arrow, and
   angle convention in the machine view. Explain that the geometry is a
   deterministic 2D teaching view and uses the same recorded `q` state as the
   plots.
2. Trace `q_des -> fixed PD -> delayed command -> actuator torque -> pendulum`.
   State where the delay is inserted and why a CAD or controller model can
   predict the wrong motion when timing is omitted.
3. Identify which trajectory is fit data and which is held out. Explain why
   the zero-delay Initial model can look plausible while accumulating phase
   error, and what improvement in Identified validation supports the fitted
   delay.
4. Change the Initial delay (or the excitation if exposed), predict what the
   orange baseline and residual should do, and press **Run identification**.
   Confirm that the prior blue result remains the result until the action runs.
5. Interpret one residual pattern: repeating signed lobes around reversals are
   a phase or timing clue; a residual correlated with velocity can arise from a
   time shift and does not by itself identify friction. Name at least three omitted effects and explain
   why this lesson does not establish hardware transfer.

If a reader misses a task, record the wording that failed, revise the relevant
page or app copy, and repeat the task with another reader. This is evidence for
the lesson, not a pre-filled signoff.

## Scope boundary

L1 introduces exactly one hidden actuator effect: command delay after the fixed
PD law. Arm mass, point payload, arm length, gravity, gains, integration step,
and ideal encoder definition are fixed and known. It does not model torque
scale or bias, saturation, velocity limits, Coulomb/Stribeck/asymmetric
friction, compliance, backlash, reflected motor inertia, voltage, temperature,
sensor noise, contact, payload shifts, Microduck assets, MuJoCo/MJLab, hardware
collection, or whole-robot fitting. Friction and saturation are the next
actuator bridge; the following structural lesson is a fixed-base leg.
