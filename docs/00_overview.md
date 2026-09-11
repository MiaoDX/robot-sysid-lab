# Robot System Identification: Overview

This repository treats robot system identification as a **modeling and validation workflow**, not merely an optimizer wrapped around a simulator.

## The five-part loop

```text
Plant -> Experiment -> Model Class -> Parameter Estimation -> Validation
```

- **Plant**: the system that generates data. It may be a real actuator, an articulated mechanism, a whole robot, or a hidden synthetic teacher simulator.
- **Experiment**: the excitation and measurements used to reveal the plant dynamics.
- **Model class**: the family of models we are willing to consider, such as ideal torque control, Coulomb friction, Stribeck friction, a two-mass flexible transmission, or a simulator parameterization.
- **Parameter estimation**: fitting the free parameters inside the chosen model class.
- **Validation**: testing whether the fitted model predicts data that was not used for fitting.

The central warning is simple:

> An optimizer can only find the best model inside the hypothesis class it was given.

If the real plant is not represented by that class, optimization may return **effective or compensating parameters** that fit one dataset but do not correspond to physical quantities and may fail under new conditions.

## What this project covers

The intended learning path is staged:

1. **1-DoF analytical plant** — inertia, damping, friction, delay, saturation, excitation, and identifiability.
2. **Single actuator** — realistic servo/motor behavior and BAM-style model selection.
3. **Multi-joint fixed-base limb** — coupling, gravity, rigid-body parameters, and parameter interaction.
4. **Limb with contact** — contact force, friction, compliance, and environment uncertainty.
5. **Whole synthetic robot** — PACE-style trajectory matching with known hidden ground truth.
6. **Small humanoid** — larger parameter spaces and hierarchy from component to whole robot.
7. **Real hardware** — unknown unknowns, timing, thermal effects, manufacturing variation, and firmware behavior.
8. **Humanoid migration** — PMSM/BLDC + FOC, reducer dynamics, whole-body matching, and narrow domain randomization.

## Important distinctions

### Calibration vs system identification

Calibration removes deterministic measurement and coordinate errors: encoder zero, direction, scale, torque offset, timing alignment, and similar quantities. SysID estimates dynamic behavior. Mixing the two makes both harder to interpret.

### Physical identification vs simulator matching

A physically identified parameter should correspond to a real quantity such as torque constant, inertia, or friction coefficient. A simulator-matching parameter only needs to make simulated behavior predict the real system in the operating region of interest.

This distinction matters for PACE-style fitting. A MuJoCo `armature` value that improves trajectory matching is not automatically a direct measurement of the physical rotor inertia.

### Component ID vs whole-system ID

BAM-style actuator identification and PACE-style whole-robot matching operate at different boundaries. A useful engineering pipeline often performs component-level characterization first, then uses whole-system fitting for residual mismatch.

## Success criteria

A useful identified model should satisfy more than a low training loss. We want:

- good held-out prediction,
- stable parameters across related datasets,
- residuals without obvious structure,
- sensible frequency response,
- enough parameter sensitivity to justify estimation,
- minimal unnecessary complexity,
- and a clear statement of which parameters are physical versus effective.

The goal is not to recover every property of reality. The goal is to obtain the **simplest model that is predictive enough for the downstream control or RL task**.
