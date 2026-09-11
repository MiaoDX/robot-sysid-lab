# Synthetic SysID Sandbox

This track uses a **teacher/student** setup.

- The **teacher plant** is white-box to the course author but hidden from the identification algorithm.
- The **student model** starts intentionally simpler and is progressively enriched.
- The SysID algorithm receives only commands and measurements.

This makes it possible to test parameter recovery, model mismatch, identifiability, experiment design, and validation while still knowing the true hidden parameters.

## Why start in simulation

Synthetic experiments let us separate algorithmic failure from hardware uncertainty. We can intentionally create cases where:

- the student has the correct structure but unknown parameters;
- the student has the wrong structure;
- several parameter sets explain the same trajectory;
- one excitation is uninformative while another is informative;
- a model fits training data but fails on held-out conditions.

## Recommended progression

1. 1-DoF rigid actuator with inertia and damping.
2. Add Coulomb friction and delay to the teacher only.
3. Add saturation and asymmetric friction.
4. Add backlash or compliance to create a true structure mismatch.
5. Move to a fixed-base articulated leg.
6. Move to whole Microduck / small humanoid teacher models.

## Avoid the inverse crime

Do not make teacher and student identical except for parameter values in every exercise. That makes recovery artificially easy. Advanced labs should deliberately use different model structures or even different numerical implementations.

## Proposed framework vocabulary

```text
Plant
Dataset
Model
ParameterSchema
Excitation
SimulatorBackend
Loss
Optimizer
Validation
Report
```

These objects should remain independent so that the same experiment can compare random search, least-squares methods, CMA-ES, sampling, or differentiable optimization.

See `one_dof_lab.py` for the minimal executable example.
