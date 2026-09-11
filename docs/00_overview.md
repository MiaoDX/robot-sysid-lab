# Robot System Identification: Overview

This repository treats robot system identification as both a **team-learning discipline** and a **modeling/validation workflow**. The near-term focus is deliberately simulation-first: build synthetic worlds whose complete ground truth is known, then restrict what the identification algorithm can observe and test which models, experiments, and estimators recover useful behavior.

## Two first-class tracks

### Knowledge track

The knowledge track gives RL, WBC, simulation, planning, and control engineers a common language for reasoning about robot plants. It covers:

1. why SysID matters for robotics and sim-to-real;
2. plant, state, observation, model, parameter, and noise;
3. robot dynamics needed for identification;
4. actuator, friction, saturation, delay, compliance, and backlash models;
5. experiment design, persistent excitation, sensitivity, and identifiability;
6. estimation methods and optimizer failure modes;
7. held-out validation, residual analysis, and frequency response;
8. physical versus effective simulator parameters;
9. the relationship among calibration, SysID, domain randomization, and robust control/RL.

The goal is not to make every engineer a SysID specialist. The goal is to make model assumptions, data requirements, and validation evidence explicit in day-to-day robotics work.

### Synthetic lab track

The synthetic track uses a teacher/student setup:

```text
Teacher world with known truth
        ↓
hide θ* and internal states as appropriate
        ↓
design excitation and observations
        ↓
Dataset
        ↓
Student hypothesis class
        ↓
Parameter estimation
        ↓
Validation and diagnosis
        ↓
compare prediction and recovered parameters against truth
```

Simulation is especially valuable here because we can:

- inspect every true parameter and latent state;
- collect arbitrary motions, loads, postures, contacts, and operating conditions;
- independently control process noise, measurement noise, quantization, and timing;
- deliberately make the teacher richer than the student;
- compare excitation strategies using exactly the same ground truth;
- distinguish optimizer failure from model-structure failure;
- and scale the same methodology from one degree of freedom to a humanoid.

Synthetic experiments remain a first-class part of the project even after real-hardware work begins.

## The core loop

```text
Plant -> Experiment -> Observation -> Model Class -> Parameter Estimation -> Validation
```

- **Plant**: the hidden teacher system or later a real robot subsystem.
- **Experiment**: excitation, initial conditions, operating conditions, and reset protocol.
- **Observation**: exactly which signals are visible to the identification pipeline.
- **Model class**: the family of student models we are willing to consider.
- **Parameter estimation**: fitting the free parameters inside the chosen class.
- **Validation**: testing on trajectories or conditions not used for fitting.

The central warning is:

> An optimizer can only find the best model inside the hypothesis class it was given.

A low fit loss can still correspond to the wrong physics, non-identifiable parameters, compensating parameters, or a model that fails under new conditions.

## Synthetic progression

The planned progression introduces only a small number of new uncertainty classes at each level:

1. **1-DoF analytical system** — inertia, damping, friction, delay, saturation, excitation, observation, and identifiability.
2. **Synthetic actuator** — BAM-style rich actuator effects: torque scale, saturation, Stribeck/load-dependent friction, asymmetry, backlash/compliance, timing, and sensor availability.
3. **Fixed-base articulated leg** — coupling, gravity, rigid-body parameters, actuator/body compensation, and multi-joint experiment design.
4. **Leg with contact** — ground friction, compliance/damping, foot geometry, and separation of contact error from actuator/body error.
5. **Whole Microduck** — compare component-first identification with PACE-style whole-robot residual matching.
6. **Microban small humanoid** — parameter sharing across actuator families, hierarchical fitting, scalability, and high-dimensional identifiability.
7. **Sim-to-sim mismatch** — different teacher/student implementations or numerical settings to approximate the fact that reality is never exactly inside the student simulator.
8. **Real hardware validation** — apply the methodology learned in synthetic labs to actuator benches and robots once the experimental and validation contracts are mature.

## Difficulty levels inside each lab

Each lab should support multiple teacher/student relationships rather than a single benchmark:

- **Level 0: matched structure** — teacher and student share the model class; test basic parameter recovery.
- **Level 1: richer truth** — teacher contains one or two additional effects; study model selection and residual signatures.
- **Level 2: strong model mismatch** — student cannot represent important teacher physics; study effective/compensating parameters.
- **Level 3: hidden condition dependence** — parameters change with temperature, voltage, load, direction, or other unobserved conditions.
- **Level 4: implementation mismatch** — teacher and student use different simulator/model implementations or numerical settings.

## Important distinctions

### Calibration vs system identification

Calibration removes deterministic measurement and coordinate errors: encoder zero, direction, scale, torque offset, timing alignment, and similar quantities. SysID estimates dynamic behavior. Mixing the two makes both harder to interpret.

### Physical identification vs simulator matching

A physically identified parameter should correspond to a real quantity such as torque constant, inertia, or friction coefficient. A simulator-matching parameter only needs to make simulated behavior predict the teacher/real system in the operating region of interest.

A MuJoCo `armature` value that improves trajectory matching, for example, is not automatically a direct measurement of physical rotor inertia.

### Component ID vs whole-system ID

BAM-style actuator identification and PACE-style whole-robot matching operate at different boundaries. The synthetic labs should compare both strategies directly, especially on Microduck and Microban:

```text
component / actuator-family ID
  -> constrain lower-level parameters
  -> subsystem validation
  -> whole-robot residual matching
```

versus a less constrained global fit.

### Parameter recovery vs predictive modeling

Ground-truth recovery is uniquely measurable in synthetic labs and should be reported when meaningful. It is not the only success criterion. A model can be useful for control or RL even when some fitted parameters are effective rather than literal, provided its predictive limits are understood.

## What every lab should report

A useful lab result should include more than the best fit loss:

- held-out trajectory and cross-condition prediction;
- ground-truth parameter error where the parameter is identifiable and semantically comparable;
- parameter sensitivity/correlation or another practical-identifiability diagnostic;
- residual structure versus state, load, direction, time, and frequency where relevant;
- parameter stability across datasets/seeds;
- comparison across model classes and excitation choices;
- and a clear statement of which fitted values are physical, effective, or weakly identifiable.

The project goal is not to recover every property of reality. It is to teach and test how to obtain the **simplest model that is predictive enough for the downstream control or RL task, with explicit evidence for where that model works and where it does not**.
