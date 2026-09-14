# L0: A first system identification experiment

This lesson set starts with a deliberately small plant so the reasoning is
visible. We identify inertia `J` and viscous damping `b` from known applied
torque and ideal position/velocity observations.

## Learning path

1. [Orientation: what is being identified?](00-orientation.md)
2. [From physics to data: why inertia and damping matter](01-physics-to-data.md)
3. [From fit to held-out validation](02-fit-to-validation.md)
4. [Assumptions, limits, and the next lesson](03-assumptions-and-next-step.md)

The [static report](../../../reports/l0_inertia_damping/report.md) is the
recorded result for the default configuration. The [Jupyter lab](../../../notebooks/l0_inertia_damping.ipynb)
lets you change one nominal value and see the same pipeline run again.

For review, the [Marimo interactive preview](../../../apps/l0_inertia_damping.py)
offers a more application-like lesson: constrained sliders update the model,
plots, metrics, and explanation reactively without manually rerunning cells.
Install and launch it from the repository root with:

```bash
python -m pip install -r requirements-interactive.txt
marimo run apps/l0_inertia_damping.py
```

This is a candidate presentation surface for comparison with Jupyter. Both
call the same numerical implementation; choosing one does not change the
experiment contract.

## Before you start

You need basic Python and the ability to read a curve over time. No robot
middleware, simulator, or GPU is required. From the repository root:

```bash
python -m pip install -r requirements.txt
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
```

Read the lessons in order. Keep the report open while reading the questions;
the goal is to explain the evidence, not to memorize the fitted numbers.
