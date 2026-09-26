# L0 · Supplementary notes and code

The [L0 lesson](index.md) contains the full explanation, videos, validation results, and exercises. This page provides notes organized by topic and links for running or inspecting the experiment.

## Look up a topic

- [The system, observations, and unknowns](00-orientation.md)
- [Inertia, damping, and input choice](01-physics-to-data.md)
- [Fitting, validation, and residuals](02-fit-to-validation.md)
- [Assumptions and the next step](03-assumptions-and-next-step.md)

## Inspect the results

The [full report](../../../reports/l0_inertia_damping/report.md) includes parameters, plots, errors, and experiment conditions. Open the [full-size figure](../../../reports/l0_inertia_damping/report.png) alongside it, or download the [notebook](../../../notebooks/l0_inertia_damping.ipynb) to inspect the computation step by step.

## Run an experiment

Running the code requires a basic Python environment. The experiment uses a CPU and needs no robot middleware or GPU. From the repository root:

```bash
python -m pip install -r requirements-interactive.txt
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
python -m marimo run apps/l0_inertia_damping.py --host 0.0.0.0 --port 2718
```

The [end of the lesson](index.md#local-experiment) guides the app exercise. Predict how the curves will change before adjusting a parameter, then compare fitting and validation after running it.

## Reproduction record

The [engineering verification record](../../../reports/l0_inertia_damping/verification.md) keeps experiment checks, reproduction commands, and learner feedback tasks for inspecting the implementation.
