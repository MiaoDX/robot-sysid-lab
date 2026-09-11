# Synthetic Lab and Knowledge Roadmap

This document defines the current project direction for `robot-sysid-lab`.

The repository is intended to be both:

1. a **knowledge base for robotics engineers learning practical SysID**, and
2. a **simulation-first research lab** where system-identification methods can be tested against complete, configurable ground truth.

The project should not be organized primarily around a generic software framework. Reusable abstractions are useful, but they should be derived from concrete labs and repeated workflows.

## 1. Project thesis

A useful robotics SysID workflow should teach and test the following loop:

```text
Build synthetic truth
  -> hide the truth from the identification pipeline
  -> design informative experiments
  -> select realistic observations
  -> choose a student hypothesis class
  -> estimate parameters
  -> diagnose residuals and identifiability
  -> validate on unseen conditions
  -> scale to a more complex robot system
```

Simulation is the primary laboratory because it gives us unusually strong experimental control:

- complete access to true physical and simulator parameters;
- complete access to latent states and internal forces when needed for analysis;
- arbitrary excitation, reset, posture, payload, contact, and motion generation;
- controlled addition/removal of noise, delay, quantization, saturation, and unobserved conditions;
- repeatable comparisons across student models and estimation methods;
- direct measurement of parameter-recovery error when recovery is meaningful.

The synthetic teacher is therefore treated as a controlled stand-in for reality, not merely as a unit test.

## 2. Knowledge track

The knowledge track should be concise enough for algorithm engineers but complete enough to support the labs.

### K0 — Why SysID matters in robotics

Questions to answer:

- Why is CAD alone not a complete robot model?
- Why can trajectory matching succeed with physically wrong parameters?
- Why can a policy fail to transfer even when one trajectory matches well?
- Why is wide domain randomization not a replacement for understanding the plant?

### K1 — SysID fundamentals

Core vocabulary:

```text
plant
input
state
observation
model
parameter
noise
experiment
estimator
validation
```

Key distinction:

```text
model-structure selection != parameter estimation
```

### K2 — Robot dynamics for identification

Cover only the dynamics needed to reason about the benchmarks:

```text
M(q) qdd + C(q, qd) qd + g(q) + tau_f = tau + J_c^T lambda
```

Topics:

- mass, CoM, inertia;
- reflected inertia;
- gravity and dynamic coupling;
- actuator torque production;
- friction and dissipation;
- compliance and backlash;
- contact forces.

### K3 — Actuator modeling

Build a model ladder from simple to rich:

```text
ideal actuator
  -> scale / bias / delay
  -> saturation and velocity-dependent limits
  -> viscous + Coulomb friction
  -> Stribeck / asymmetry / load dependence
  -> reflected inertia / motor-side dynamics
  -> compliance / backlash / resonance
  -> voltage / thermal / hysteresis effects when evidence requires them
```

BAM is a primary reference for this section and for the actuator lab.

### K4 — Experiment design and identifiability

Teach why data quality depends on what motion was executed, not only how much data was collected.

Example excitation classes:

- slow sine;
- chirp;
- multisine;
- step and reversal;
- free decay/backdrive where appropriate;
- PRBS-like excitation;
- later, information-driven active excitation.

Key ideas:

- persistent excitation;
- sensitivity;
- parameter correlation;
- practical identifiability;
- observability of hidden effects under different operating conditions.

### K5 — Estimation and optimization

Provide enough background to understand the tradeoffs among:

- linear/weighted least squares;
- nonlinear least squares / Gauss-Newton;
- CMA-ES;
- parallel/random sampling;
- Bayesian optimization where appropriate;
- gradient-based/differentiable methods.

The important teaching goal is to distinguish:

```text
optimizer failure
from
model failure
from
uninformative experiment
```

PACE is a useful reference for evolutionary whole-system fitting.

### K6 — Validation and residual diagnostics

Every team member should internalize:

```text
low training error != validated model
```

Validation dimensions should include different:

- motions;
- frequencies;
- directions;
- postures;
- payloads;
- controller gains;
- contact conditions;
- voltage/temperature conditions where modeled.

Residual analysis should connect patterns to hypotheses about missing physics.

### K7 — Physical vs effective parameters

A central theme across the project:

- **physical parameter** — independently meaningful real quantity;
- **effective parameter** — simulator value that improves prediction but may absorb omitted physics;
- **nuisance parameter** — needed to explain observations but not itself a downstream target;
- **uncertain parameter** — quantity whose range matters more than a single point estimate.

### K8 — SysID to sim-to-real

Connect:

```text
calibration
  -> identified nominal model
  -> quantified remaining uncertainty
  -> targeted domain randomization / robust control
```

The goal is not to eliminate uncertainty, but to avoid using unnecessarily broad randomization to hide systematic model errors that could have been diagnosed.

## 3. Synthetic lab ladder

### L0 — 1-DoF analytical concepts

Purpose: a teaching microscope, not a realistic motor model.

Questions:

- What does inertia look like in data?
- When is damping visible?
- What does delay do to phase?
- Why does slow excitation hide inertial effects?
- How do friction and saturation change residuals?

The implementation should remain intentionally small and be rebuilt only after the benchmark contract is agreed.

### L1 — synthetic actuator

Purpose: reproduce and extend the kinds of actuator-model studies seen in BAM while retaining full hidden truth.

Teacher effects may include:

- torque scale and bias;
- command/measurement delay;
- saturation and velocity-dependent limits;
- viscous/Coulomb/Stribeck friction;
- directional and load dependence;
- reflected inertia;
- backlash/compliance;
- voltage/temperature dependence.

Student models should be progressively enriched and compared on held-out conditions.

Key benchmark dimensions:

- matched versus mismatched model structure;
- excitation choice;
- observation availability;
- parameter recovery versus predictive performance;
- estimator behavior.

### L2 — fixed-base articulated leg

Purpose: introduce multi-body coupling while excluding contact and floating-base uncertainty.

Canonical experiment matrix:

| Case | Actuator model | Rigid-body model | Main question |
|---|---|---|---|
| A | correct | wrong | can link/body errors be recovered without corrupting actuator parameters? |
| B | wrong | correct | how do actuator errors appear across posture and frequency? |
| C | wrong | wrong | what compensating solutions appear? |
| D | partially constrained | partially constrained | how much do lower-level priors help? |

This level should introduce practical identifiability, sensitivity analysis, and parameter-sharing rules explicitly.

### L3 — leg with contact

Purpose: add one new uncertainty class only after free-space prediction is acceptable.

Teacher effects may include:

- ground friction;
- contact stiffness/damping;
- sole compliance;
- foot geometry;
- stick/slip transition.

Key lesson:

```text
actuator okay?
  -> rigid-body subsystem okay?
  -> contact model okay?
```

Do not let contact parameters compensate for previously known free-space errors.

### L4 — whole Microduck

Purpose: first whole-robot synthetic benchmark and first direct comparison between component-first and global-fitting workflows.

#### Route A — component first

```text
actuator ID
  -> subsystem validation
  -> constrain lower-level parameters
  -> whole-robot residual matching
```

#### Route B — global fit

```text
whole-robot trajectories
  -> compact simulator parameterization
  -> PACE-style optimization
```

Compare:

- training and validation error;
- parameter correctness/interpretability;
- optimization difficulty;
- robustness across motion families;
- sensitivity to model mismatch;
- downstream simulation behavior.

### L5 — Microban small humanoid

Microban is the designated small-humanoid platform for this project.

The main questions are scaling and hierarchy rather than adding many new physical effects.

Study:

- actuator-family shared parameters;
- per-joint residual parameters;
- grouped versus fully independent parameterization;
- high-dimensional identifiability;
- component priors versus unconstrained global fitting;
- whole-body motion diversity and held-out validation.

Representative strategies:

```text
A: all parameters independent per joint
B: actuator-family shared parameters + small per-joint residuals
C: compact whole-robot effective parameter fit
```

### L6 — sim-to-sim mismatch

Purpose: move beyond same-implementation teacher/student benchmarks.

Possible comparisons:

- custom rich actuator teacher versus native MuJoCo student parameters;
- different integration/time-step assumptions;
- MuJoCo CPU versus MuJoCo Warp where parameter semantics align;
- different contact implementations.

This level approximates an essential sim-to-real property: the student model class never exactly contains reality.

### Later — hardware validation

Real actuator benches and robots remain important, but they are not required to justify the simulation-first track.

Hardware work should reuse the same concepts and reporting contracts developed in synthetic labs:

- explicit plant boundary;
- experiment and observation schema;
- model hierarchy;
- held-out validation;
- residual diagnostics;
- uncertainty reporting.

## 4. Benchmark families that cut across labs

### B1 — model mismatch

Deliberately remove one or more teacher effects from the student model and characterize compensating solutions.

Examples:

```text
truth has delay; student does not
truth has backlash; student does not
truth has Stribeck/load dependence; student uses Coulomb + viscous
truth body mass is wrong; student is allowed to change torque scale
```

### B2 — excitation design

For the same truth/model pair, compare excitation families and measure:

- parameter error;
- held-out error;
- sensitivity / Fisher-information-like metrics;
- parameter correlation or uncertainty proxies.

### B3 — observation ablation

Synthetic truth can expose every internal signal, so use that privilege to study what happens when signals are removed.

Start from an omniscient analysis dataset:

```text
q, qd, qdd, true torque, motor current, controller output, contact force, latent states
```

Then restrict the student to realistic observation sets such as:

```text
command + encoder
command + encoder + current estimate
command + encoder + external force/torque where available
```

Add noise, quantization, filters, and timing uncertainty as explicit experiment factors.

### B4 — optimizer comparison

Compare estimators only under a fixed model/data contract. Report compute budget as well as fit quality so optimizer failure is not confused with model quality.

### B5 — cross-condition validation

Every serious benchmark should reserve conditions that were not used for fitting. The held-out axis should match the expected deployment variation.

## 5. Truth difficulty levels

Use a common difficulty vocabulary across labs:

| Level | Teacher/student relationship | Purpose |
|---|---|---|
| 0 | same structure | implementation and basic recovery |
| 1 | teacher slightly richer | model selection and residual diagnosis |
| 2 | strong structural mismatch | effective parameters and compensation |
| 3 | hidden condition dependence | dataset shift and missing context |
| 4 | different implementation/backend | sim-to-sim approximation of real model mismatch |

## 6. Supporting software modules

The lab needs should drive the reusable code. The likely modules are:

```text
Experiment / Excitation
Plant / Teacher
Observation policy
Dataset
Student Model
ParameterSchema
SimulatorBackend
Loss
Estimator
Validation
Report
```

These are supporting abstractions rather than the primary project story.

### Experiment / Data

Defines excitation, initial conditions, operating conditions, observations, timing, and metadata.

### Plant / Teacher

Defines the hidden ground-truth system and its command interface.

### Model library

Contains progressively richer student models for actuators, friction, transmission, rigid-body effects, and contact.

### Parameterization / Identifiability

Defines units, bounds, priors, sharing rules, physical/effective semantics, and practical-identifiability diagnostics.

### Estimation

Keeps optimizer choice replaceable and thin.

### Validation / Report

Makes held-out performance, residuals, sensitivity, parameter stability, and ground-truth comparison first-class outputs.

## 7. Implementation sequence

The implementation should proceed from benchmark contracts rather than from a generic framework skeleton.

### Phase 0 — stabilize the learning and benchmark specification

Deliverables:

- knowledge syllabus;
- lab ladder;
- truth difficulty levels;
- common experiment/result vocabulary;
- success metrics for parameter recovery and prediction.

### Phase 1 — rebuild the minimal 1-DoF lab

Only after the specification is stable:

- implement a correct minimal teacher/student example;
- make experiment, observation, fit, validation, and truth comparison explicit;
- use it to establish reporting conventions.

### Phase 2 — synthetic actuator benchmark

Build the first serious reusable benchmark and reproduce BAM-like questions with known ground truth.

This phase should determine which abstractions are genuinely reusable.

### Phase 3 — fixed-base leg and contact

Add multibody coupling first, then contact as a separately diagnosable uncertainty class.

### Phase 4 — Microduck whole-robot benchmark

Compare component-first and PACE-style global fitting on the same synthetic truth.

### Phase 5 — Microban scaling benchmark

Study parameter sharing, hierarchy, and high-dimensional identifiability on a small humanoid.

### Phase 6 — cross-simulator and later hardware studies

Use different numerical/model implementations, then reuse the same methodology on real systems.

## 8. Design principles

1. **Synthetic is a first-class research environment.** Do not treat it only as a temporary stepping stone to hardware.
2. **Knowledge and executable labs should map to each other.** Every important concept should have a concrete experiment where possible.
3. **Teacher truth may be complex, but student observations should be realistic.** Hidden truth is for evaluation, not fitting.
4. **Do not always let teacher and student share the same model.** Matched structure is a baseline, not the final benchmark.
5. **Experiment design is part of SysID.** More optimizer iterations cannot recover information that the experiment never revealed.
6. **Validation is part of the result.** A fitted parameter file without held-out evidence is incomplete.
7. **Separate physical and effective parameters.** Both can be useful, but they answer different questions.
8. **Scale hierarchically.** Actuator -> leg -> contact -> Microduck -> Microban is intended to isolate new uncertainty classes instead of introducing everything at once.
9. **Framework abstractions should emerge from repeated labs.** Avoid premature generalization.
10. **The eventual target is predictive simulation for robotics.** Ground-truth recovery is valuable when identifiable, but the model must ultimately be judged by useful held-out behavior for control/RL.
