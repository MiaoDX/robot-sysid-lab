# Synthetic SysID Lab

The synthetic track is a first-class part of this repository, not just a preliminary sanity check before hardware.

Its purpose is to create controlled robot-identification problems where the complete hidden ground truth is available to the lab author while the identification pipeline only receives realistic commands and observations.

## Teacher / student setup

```text
Teacher world
  - complete ground truth θ*
  - rich internal states
  - configurable hidden physics
        ↓
Experiment
  - excitation
  - initial state
  - posture/load/contact condition
  - observation policy
        ↓
Dataset
        ↓
Student model
  - intentionally limited hypothesis class
        ↓
Estimator
        ↓
Validation + diagnosis
        ↓
Compare against held-out behavior and θ*
```

The teacher may expose every internal signal to the benchmark infrastructure, but the student should only receive the subset declared by the experiment. This lets us study both model uncertainty and observation limitations.

## Why simulation is the main laboratory

Simulation lets us answer questions that are difficult or impossible to isolate on hardware:

- Is a parameter truly identifiable from this experiment?
- Did optimization fail, or is the student model structurally wrong?
- Which richer physical effect creates a particular residual pattern?
- How much does velocity, torque, current, contact force, or another observation help?
- What happens if measurements are noisy, delayed, quantized, or missing?
- Which excitation makes a parameter observable?
- Can a wrong student model match one motion by compensating with another parameter?
- Does component-level identification make whole-robot fitting easier and more stable?

Because the ground truth is known, synthetic labs can evaluate both **parameter recovery** and **predictive performance**.

## Avoid the inverse crime

Teacher and student should not always share the same equations and numerical implementation.

Matched teacher/student models are useful as a Level-0 correctness test, but advanced benchmarks should deliberately introduce differences such as:

- Stribeck truth versus Coulomb/viscous student friction;
- backlash or compliance present only in the teacher;
- load-, voltage-, or temperature-dependent behavior hidden from the student;
- richer actuator limits in the teacher;
- different simulator backends or numerical settings;
- sensor and command timing not represented by the student.

The purpose is to reproduce a central feature of sim-to-real: reality is never exactly inside the hypothesis class.

## Lab ladder

### Lab 0 — 1-DoF analytical concepts

Use a transparent system as a teaching microscope for:

- inertia and acceleration;
- viscous and Coulomb friction;
- delay and phase;
- saturation;
- noise and observation quality;
- excitation and practical identifiability.

This lab should be small and concept-driven rather than treated as a realistic actuator simulator.

### Lab 1 — synthetic actuator

Build a BAM-inspired teacher with configurable effects such as:

- torque scale and bias;
- command/measurement delay;
- torque/current saturation;
- velocity-dependent torque limits;
- Coulomb, viscous, Stribeck, asymmetric, and load-dependent friction;
- reflected inertia;
- backlash/compliance;
- voltage or temperature dependence when useful.

Compare progressively richer student models and test which residual evidence justifies each increase in complexity.

### Lab 2 — fixed-base articulated leg

Introduce multi-body dynamics without contact or floating-base ambiguity:

- joint coupling;
- gravity and posture dependence;
- link mass/CoM/inertia;
- multiple actuator models;
- parameter sharing and correlation.

Canonical benchmark cases:

1. actuator correct / body wrong;
2. body correct / actuator wrong;
3. both wrong;
4. different excitation and posture sets.

This layer should make parameter compensation visible before whole-robot complexity is introduced.

### Lab 3 — leg with contact

After free-space prediction works, add one new uncertainty class: contact.

Candidate teacher effects include:

- ground friction;
- normal stiffness/damping;
- sole compliance;
- foot geometry;
- stick/slip transitions.

The central lesson is diagnostic ordering: do not use contact parameters to hide actuator or rigid-body errors that were already present in free space.

### Lab 4 — whole Microduck

Microduck is the first whole-robot benchmark.

Use it to compare two system-identification strategies on the same hidden teacher:

```text
Route A: component first
actuator ID -> subsystem validation -> whole-robot residual fit

Route B: global fit
whole-robot trajectories -> PACE-style simulator parameter optimization
```

Compare:

- fit and held-out prediction;
- parameter recovery/interpretability;
- optimization difficulty;
- transfer across motion families;
- sensitivity to model mismatch.

### Lab 5 — Microban small humanoid

Microban remains the small-humanoid platform for this repository.

The physics need not become dramatically richer than Microduck. The main research questions become scalability and hierarchy:

- many joints and larger parameter spaces;
- actuator-family parameter sharing;
- per-joint residuals;
- hierarchical fitting versus fully independent joint parameters;
- component priors versus unconstrained whole-robot optimization;
- high-dimensional practical identifiability.

A representative comparison is:

```text
Strategy A: every joint owns all parameters
Strategy B: actuator-family shared parameters + small per-joint residuals
Strategy C: global whole-robot simulator matching
```

### Lab 6 — sim-to-sim mismatch

Use intentionally different teacher/student implementations to approximate the fact that the real plant cannot be reproduced exactly by the student simulator.

Examples:

- custom actuator truth versus native MuJoCo student parameters;
- different time steps or integration assumptions;
- MuJoCo CPU versus MuJoCo Warp where semantics permit comparison;
- different contact/model implementations.

## Benchmark dimensions

The same lab should be reusable across several benchmark families.

### Model mismatch

Compare matched and intentionally incomplete student hypothesis classes.

### Excitation design

Compare slow sine, chirp, multisine, reversals, PRBS-like signals, random excitation, and later information-driven active excitation.

### Observation availability

Start from an omniscient synthetic dataset, then progressively hide signals:

```text
q, dq, ddq, true torque, current, contact force, internal control output
        ↓
realistic subsets such as command + encoder + current estimate
```

Add measurement noise, quantization, filters, and timing errors explicitly.

### Estimator behavior

Use the same model/data contract to compare least-squares methods, nonlinear optimization, CMA-ES, parallel sampling, and later differentiable methods. The purpose is to distinguish estimator limitations from model limitations, not to make optimizer leaderboards the primary objective.

### Cross-condition validation

Hold out frequency bands, motions, directions, postures, payloads, controller gains, contact conditions, voltage, or temperature depending on the lab.

## Truth difficulty levels

Each synthetic scenario should be configurable in increasing difficulty:

1. **Matched structure** — test basic recovery and implementation correctness.
2. **Richer truth** — add one or two effects not initially present in the student.
3. **Strong mismatch** — important teacher physics cannot be represented by the student.
4. **Hidden condition dependence** — teacher dynamics change with an unobserved variable.
5. **Implementation mismatch** — teacher and student differ numerically or structurally even when parameter names look similar.

## What a lab should produce

A synthetic benchmark should eventually report:

- teacher configuration and hidden truth (available to evaluation, not fitting);
- experiment and observation configuration;
- student model class and free parameters;
- fit loss and compute budget;
- held-out and cross-condition prediction;
- ground-truth parameter error where meaningful;
- parameter sensitivity/correlation diagnostics;
- residual plots/statistics;
- and a short explanation of what failed: excitation, identifiability, model structure, estimator, or numerical implementation.

## Implementation policy

The lab design comes before any particular code architecture. Supporting abstractions such as `Dataset`, `Model`, `ParameterSchema`, `Excitation`, `Estimator`, and `Validation` should emerge from repeated lab needs rather than forcing the labs to fit a premature framework.

See [the project roadmap](../docs/03_synthetic_lab_roadmap.md) for the planned knowledge/lab mapping and implementation sequence.
