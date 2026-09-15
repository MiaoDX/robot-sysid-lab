# L0: A first system identification experiment

`L0` means **Lab 0**: the smallest complete SysID loop in the synthetic-lab
track. The [course overview](../../course/index.html) shows how this lab relates
to the `K0-K8` knowledge track and the later `L1-L6` and `H0-H2` stages.

This lesson set begins with why robot system identification is useful, what it
produces, and the engineering loop it follows. It then uses a deliberately
small plant so every part of that loop is visible. We identify inertia `J` and
viscous damping `b` from known applied torque and ideal position/velocity
observations.

## Learning path

1. Open the Marimo course and follow its continuous path from Why to Limits.
2. [Orientation: what is being identified?](00-orientation.md)
3. [From physics to data: why inertia and damping matter](01-physics-to-data.md)
4. [From fit to held-out validation](02-fit-to-validation.md)
5. [Assumptions, limits, and the next lesson](03-assumptions-and-next-step.md)

The [static report](../../../reports/l0_inertia_damping/report.md) is the
recorded result for the default configuration. The [Jupyter lab](../../../notebooks/l0_inertia_damping.ipynb)
lets you inspect and change the same pipeline cell by cell.

The [Marimo interactive course](../../../apps/l0_inertia_damping.py) is the
guided entry point. It explains why SysID matters, declares the model boundary,
and embeds the experiment and its evidence in one vertically scrolling lesson.
The chapter rail is for orientation. Fit and Validation stay visible side by
side. Constrained sliders update the orange Initial model immediately; fitting
runs only when you press **Run identification**, which updates the blue result.
Install and launch it
from the repository root with:

```bash
python -m pip install -r requirements-interactive.txt
marimo run apps/l0_inertia_damping.py
```

Marimo and Jupyter call the same numerical implementation. They provide guided
and inspectable views of one experiment contract rather than separate labs.

## Before you start

You need basic Python and the ability to read a curve over time. No robot
middleware, simulator, or GPU is required. From the repository root:

```bash
python -m pip install -r requirements.txt
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
```

Read the lessons in order. Keep the report open while reading the questions;
the goal is to explain the evidence, not to memorize the fitted numbers.
