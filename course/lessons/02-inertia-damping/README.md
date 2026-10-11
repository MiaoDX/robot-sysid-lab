# L0 · Supplementary notes and code

The [L0 lesson](index.md) contains the full explanation, videos, validation results, and exercises. This page provides notes organized by topic and links for running or inspecting the experiment.

## Look up a topic

- [The system, observations, and unknowns](00-orientation.md)
- [Inertia, damping, and input choice](01-physics-to-data.md)
- [Fitting, validation, and residuals](02-fit-to-validation.md)
- [Assumptions and the next step](03-assumptions-and-next-step.md)

## Inspect the results

The [full report](../../../artifacts/02-inertia-damping/report.md) includes parameters, plots, errors, and experiment conditions. Open the [full-size figure](../../../artifacts/02-inertia-damping/report.png) alongside it, or open the [Marimo app](../../../apps/02_inertia_damping.py) to inspect the computation step by step.

## Run an experiment

Running the code requires a basic Python environment. The experiment uses a CPU and needs no robot middleware or GPU. From the repository root:

```bash
python -m pip install -r requirements-interactive.txt
uv run sysid-lab run 02 --output-dir .tmp/02-inertia-damping
python -m marimo run apps/02_inertia_damping.py --host 0.0.0.0 --port 2718
```

The [end of the lesson](index.md#local-experiment) guides the app exercise. Predict how the curves will change before adjusting a parameter, then compare fitting and validation after running it.

## Reproduction record

The [artifact manifest](../../../artifacts/02-inertia-damping/manifest.json) records the generated files, roles, checksums, and provenance for inspecting the implementation.
