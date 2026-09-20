# L1: Servo-driven loaded pendulum

L1 adds one machine-shaped mismatch to the complete L0 loop. A fixed base holds
a rotary arm and a known point payload. A position command `q_des` goes through
a fixed PD controller, and the controller's torque command is delayed before it
drives the gravity-loaded pendulum.

The question this lab asks:

> A delay is invisible in a drawing of the machine. Can it still be identified
> from the motion it causes?

The delay is an **effective parameter of this command boundary and sampling
setup** — not a motor electromagnetic time constant.

## Read this in order

Keep the [fixed report](../../../reports/l1_servo_loaded_pendulum/report.md) open
while you read. The goal is to explain the evidence, not to memorize the fitted
numbers.

1. [Meet the machine and the question](00-orientation.md)
2. [From command to delayed torque](01-command-to-torque.md)
3. [Fit, validation, and residual phase](02-fit-validation-residuals.md)
4. [Exercise, limits, and the bridge to L2](03-exercise-and-limits.md)

## Try it yourself

The [Marimo app](../../../apps/l1_servo_loaded_pendulum.py) is the guided path.
It has one fit-affecting control, **Initial delay**, and an explicit **Run
identification** action. Changing that control marks the completed result
stale; the orange baseline changes only when you submit, and the blue result
does not move until you do.

```bash
python -m pip install -r requirements-interactive.txt
python -m marimo run apps/l1_servo_loaded_pendulum.py --host 0.0.0.0 --port 2719
```

The [notebook](../../../notebooks/l1_servo_loaded_pendulum.ipynb) exposes the
same completed run cell by cell if you would rather inspect than click.

## Before you start

You need basic Python and the ability to read a curve over time. No robot
middleware, simulator, or GPU is required.

## Reproduction and acceptance

Your run reproduces the report with:

```bash
python -m synthetic.l1_servo_loaded_pendulum --output-dir reports/l1_servo_loaded_pendulum
```

Everything an implementer or verifier needs — the gate-by-gate evidence, the
privileged-signal contract, the clean-environment commands, and the independent
learner checklist — lives with the verification record:

**[L1 implementation verification](../../../reports/l1_servo_loaded_pendulum/verification.md)**