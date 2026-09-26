# L1 · Supplementary notes and code

The [L1 lesson](index.md) contains the full explanation, videos, validation results, and exercises. This page provides notes organized by topic and links for running or inspecting the experiment.

## Look up a topic

- [The machine and its dynamics](00-orientation.md)
- [From position command to torque](01-command-to-torque.md)
- [Fitting, validation, and phase error](02-fit-validation-residuals.md)
- [Exercises and the scope of the result](03-exercise-and-limits.md)

## Inspect the results

The [delay report](../../../reports/l1_servo_loaded_pendulum/report.md) and [friction report](../../../reports/l1_friction/report.md) include parameters, plots, errors, and experiment conditions. Download the [delay notebook](../../../notebooks/l1_servo_loaded_pendulum.ipynb) or [friction notebook](../../../notebooks/l1_friction.ipynb) to inspect each computation step by step.

## Run an experiment

Running the code requires a basic Python environment. The experiment uses a CPU and needs no robot middleware or GPU. From the repository root:

```bash
python -m pip install -r requirements-interactive.txt
python -m synthetic.l1_servo_loaded_pendulum --output-dir reports/l1_servo_loaded_pendulum
python -m synthetic.l1_friction --output-dir reports/l1_friction
python -m marimo run apps/l1_servo_loaded_pendulum.py --host 0.0.0.0 --port 2719
```

The [end of the lesson](index.md#local-experiment) guides the app exercise. Predict how the curves will change before adjusting a parameter, then compare fitting and validation after running it.

## Reproduction record

The [engineering verification record](../../../reports/l1_servo_loaded_pendulum/verification.md) keeps experiment checks, reproduction commands, and learner feedback tasks for inspecting the implementation.
