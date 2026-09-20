# L0: A first system identification experiment

`L0` means **Lab 0**: the smallest complete system-identification loop in the
synthetic-lab track. The [course overview](../../course/index.html) shows how it
relates to the `K0-K8` knowledge track and the later `L1-L6` and `H0-H2` stages.

The plant is deliberately tiny so every part of the loop is visible. We identify
inertia `J` and viscous damping `b` from a known applied torque and ideal
position and velocity observations.

The question this lab asks:

> We can measure how a joint moved. Can we work out the two numbers that made
> it move that way — and trust the answer on a motion we never fitted?

## Read this in order

Keep the [fixed report](../../../reports/l0_inertia_damping/report.md) open
while you read. The goal is to explain the evidence, not to memorize the fitted
numbers.

1. [Orientation: what is being identified?](00-orientation.md)
2. [From physics to data: why inertia and damping matter](01-physics-to-data.md)
3. [From fit to held-out validation](02-fit-to-validation.md)
4. [Assumptions, limits, and the next lesson](03-assumptions-and-next-step.md)

## Try it yourself

The [Marimo course](../../../apps/l0_inertia_damping.py) is the guided path: it
declares the model boundary and puts Fit and Validation side by side. Constrained
sliders change the orange Initial model immediately; fitting runs only when you
press **Run identification**, which updates the blue result.

```bash
python -m pip install -r requirements-interactive.txt
python -m marimo run apps/l0_inertia_damping.py --port 2718
```

The [Jupyter lab](../../../notebooks/l0_inertia_damping.ipynb) exposes the same
pipeline cell by cell if you would rather inspect than click.

## Before you start

You need basic Python and the ability to read a curve over time. No robot
middleware, simulator, or GPU is required.

## Reproduction and acceptance

Your run reproduces the report with:

```bash
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
```

Everything an implementer or verifier needs — the gate-by-gate evidence, the
privileged-signal contract, and the independent learner checklist — lives with
the verification record:

**[L0 implementation verification](../../../reports/l0_inertia_damping/verification.md)**