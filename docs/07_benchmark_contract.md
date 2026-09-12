# Benchmark Contract: Truth, Observations, Estimation, and Evaluation

This document defines the benchmark contract that every serious `robot-sysid-lab` experiment should follow.

The project already defines a simulation-first learning ladder, Oracle/Student methodology, whole-robot experiment protocols, visualization/reporting requirements, and a visual learning experience. The remaining architectural requirement is to make the benchmark itself precise:

```text
What is the hidden truth?
What may the identification algorithm observe?
What is allowed to vary during fitting?
How is success evaluated?
```

Without these contracts, it is easy to build visually compelling demonstrations that are difficult to compare, accidentally leak privileged information, or conflate model quality with optimizer quality.

The benchmark should therefore be organized around four explicit contracts:

```text
Oracle Definition
       ↓
Dataset / Observation Contract
       ↓
Model + Estimation Protocol
       ↓
Evaluation Protocol
```

These contracts should be fixed before large-scale benchmark implementation begins.

---

## 1. Core benchmark philosophy

The benchmark is intended to answer three different questions:

1. **Can we recover meaningful hidden parameters when recovery is identifiable?**
2. **Can the Student predict unseen Oracle behavior even when parameter recovery is not literal?**
3. **Does the identified Student improve downstream control or RL transfer back to the Oracle?**

These questions are related but not equivalent.

A method may recover physical parameters accurately yet still provide poor prediction because its model class omits important dynamics. Another method may find physically inaccurate effective parameters that predict the deployment region very well. A third model may have good short-horizon prediction but still produce a policy that fails when trained inside it.

The benchmark should therefore report these outcomes separately rather than collapsing them into one headline score.

---

# 2. Oracle Definition Contract

The Oracle is the synthetic world treated as hidden ground truth for a benchmark instance.

It should be defined as more than a parameter vector.

A useful conceptual decomposition is:

```text
Oracle
├── Mechanical plant
├── Actuator / transmission
├── Controller / firmware behavior
├── Sensor model
├── Communication / timing model
├── Contact / environment
├── Numerical simulator configuration
└── Initial condition and hidden context
```

This is important because two worlds with the same nominal masses and friction coefficients can behave differently due to controller rates, actuator saturation, observation delay, solver settings, or contact semantics.

## 2.1 Mechanical truth

Examples:

- link mass;
- CoM;
- inertia tensor;
- geometry;
- joint limits;
- reflected inertia;
- passive compliance;
- backlash or additional hidden DoFs.

## 2.2 Actuator truth

Examples:

- torque/current scale;
- bias;
- viscous friction;
- Coulomb friction;
- Stribeck friction;
- asymmetric friction;
- load dependence;
- velocity-dependent torque limits;
- saturation;
- command delay;
- voltage effects;
- temperature dependence;
- transmission compliance or hysteresis.

## 2.3 Controller / firmware truth

Where the plant boundary includes an embedded or low-level controller, the Oracle should explicitly include its behavior.

Examples:

```text
PD / impedance controller
command filtering
rate limiting
firmware compensation
clipping
anti-windup behavior
current-loop bandwidth
```

The benchmark must document the command interface that is considered the input to the plant.

## 2.4 Sensor truth

Examples:

- encoder quantization;
- encoder noise;
- velocity filtering or finite-difference estimation;
- IMU noise and bias;
- current / torque estimate bias;
- force sensor noise;
- sensor-side delay.

## 2.5 Communication and timing truth

Timing should be explicit rather than hidden inside a single generic `delay` parameter.

Possible rates include:

```text
physics integration rate
actuator/controller rate
sensor sampling rate
policy rate
logging rate
```

Possible timing effects include:

- command latency;
- measurement latency;
- timestamp offset;
- jitter;
- asynchronous sampling;
- packet drop or stale commands where relevant.

Synthetic experiments are a particularly good place to teach that command delay and measurement delay are not automatically the same problem.

## 2.6 Environment / contact truth

Examples:

- friction;
- contact solver configuration;
- contact softness or compliance representation;
- foot collision geometry;
- terrain geometry;
- external disturbances;
- payloads.

## 2.7 Numerical truth

A simulator configuration is part of the Oracle definition when the benchmark depends on it.

Record at least:

- simulator/backend version;
- timestep;
- integration method where configurable;
- solver iterations/tolerances where relevant;
- contact settings;
- deterministic/random seeds.

The Oracle is a benchmark truth, not a claim that one simulator is absolute physical reality.

---

# 3. Oracle construction strategies

Not all Oracle instances should be created the same way.

The project should support three complementary construction modes.

## 3.1 Hand-designed truth

Purpose: teaching and tightly controlled experiments.

Example:

```text
delay = 15 ms
backlash = 1 deg
friction = known nonlinear curve
```

Advantages:

- easy to explain;
- easy to isolate one effect;
- useful for knowledge pages and first labs.

Disadvantage:

- may become overly convenient or unrealistic if used as the only benchmark source.

## 3.2 Plausible robot truth

Purpose: realistic synthetic studies tied to Microduck and Microban.

Truth values may be based on:

- CAD-derived rigid-body data;
- known hardware specifications;
- upstream actuator models such as BAM configurations;
- plausible measured or literature-supported ranges;
- existing robot simulation configurations.

This mode should create Oracles that are intentionally plausible without pretending that their synthetic values are validated measurements of a particular physical robot unless they actually are.

## 3.3 Oracle distribution

Purpose: prevent overfitting a SysID pipeline to one hand-picked truth.

Instead of evaluating only one Oracle:

```text
Oracle #001
Oracle #002
...
Oracle #N
```

sample from a documented distribution of plausible worlds.

Conceptually:

```text
Oracle distribution
        ↓ sample
hidden Oracle instance
        ↓
experiment
        ↓
SysID
        ↓
evaluation
```

The distribution may vary:

- parameter values;
- omitted/hidden physical effects;
- payload;
- voltage;
- contact properties;
- sensor quality;
- timing;
- numerical implementation in advanced sim-to-sim cases.

This is a later benchmark stage, but the configuration format should not assume there is only one canonical truth.

---

# 4. Oracle difficulty levels

The existing truth difficulty vocabulary should be retained and connected to Oracle construction.

| Level | Relationship | Typical purpose |
|---|---|---|
| T0 | Teacher and Student share the same model structure | implementation/recovery sanity check |
| T1 | Oracle contains one or two extra effects | model selection and residual diagnosis |
| T2 | strong structural mismatch | effective parameters and compensation |
| T3 | hidden condition dependence | dataset shift and missing context |
| T4 | different implementation/backend | sim-to-sim model mismatch |

A benchmark should explicitly declare its truth difficulty.

---

# 5. Dataset Contract

Every dataset must be replayable and auditable.

A dataset is not merely a matrix of observations. It should carry the experimental conditions required to reproduce the rollout.

Recommended metadata includes:

```text
experiment_id
oracle_id
robot/model version
simulator/backend version
random seed
initial condition
control interface
control rates
sensor rates
policy/controller identity
command trajectory
observation schema
operating condition
payload/environment
```

For policy-generated data, also record:

```text
policy checkpoint / hash
policy observation normalization
policy command sequence
policy control frequency
action scaling and clipping
```

For repeated experiments, each rollout should have a stable identifier.

---

# 6. Student-visible vs Oracle-privileged data

The benchmark must separate these two categories structurally.

## 6.1 Student-visible data

This is the only information that the identification pipeline may use.

Examples might include:

```text
commands
encoder position
estimated velocity
IMU
current estimate
controller gains
known experiment metadata
```

The exact set depends on the benchmark observation level.

## 6.2 Oracle-privileged data

This is available only for evaluation, visualization, debugging, or deliberately privileged baseline experiments.

Examples:

```text
true acceleration
true actuator torque
true friction force
true contact force
latent backlash state
motor-side hidden state
exact hidden parameter vector
solver-internal contact state
```

The fitting code should not accidentally receive this data through a common state object.

A useful implementation principle is to write separate artifacts/namespaces for:

```text
observations/
privileged_truth/
```

rather than rely only on developer discipline.

---

# 7. Observation levels

Use standardized observation regimes so methods can be compared under clearly stated information availability.

## O0 — privileged

All or nearly all simulator states required to make the problem easy to inspect.

Purpose:

- debugging;
- teaching;
- implementation baselines;
- separating estimator problems from observation problems.

O0 should not be presented as a realistic hardware benchmark.

## O1 — realistic-rich

Representative example:

```text
command
encoder position
velocity estimate
current / load estimate
IMU
known controller state/gains
```

Purpose:

- emulate a robot with good engineering telemetry.

## O2 — realistic-minimal

Representative example:

```text
command
encoder
IMU
```

Purpose:

- test what remains identifiable without rich actuator telemetry.

Additional observation regimes may be introduced for specific hardware interfaces, but the project should use a small standardized vocabulary instead of ad hoc signal lists in every lab.

---

# 8. Observation ablation is itself a benchmark

Synthetic simulation gives complete latent access, so the project should explicitly study how much information is lost when signals are removed.

Example progression:

```text
O0: command + q + qd + qdd + true torque
O1: command + q + qd + current estimate + IMU
O2: command + q + IMU
```

Then compare:

- recoverable parameters;
- predictive error;
- uncertainty;
- failure modes;
- required excitation.

This teaches that sensor/telemetry design is part of system-identification system design.

---

# 9. Model + Estimation Protocol

Every benchmark run should explicitly separate the following choices:

```text
Student model class
ParameterSchema
Estimator
Optimization budget
Loss
Initialization / priors
```

This prevents statements such as "model A is better than model B" when the models were fitted with very different compute budgets or priors.

## 9.1 Student model class

The model specifies which effects are representable.

Examples:

```text
ideal actuator
Coulomb + viscous
Stribeck
delay
backlash
rigid-body residual parameters
contact parameters
```

## 9.2 ParameterSchema

The schema should define:

- units;
- bounds;
- priors;
- sharing rules;
- fixed parameters;
- physical/effective/nuisance semantics;
- transform used by the optimizer where applicable.

## 9.3 Estimator

Examples:

- least squares;
- nonlinear least squares;
- CMA-ES;
- random/parallel search;
- gradient-based estimation;
- Bayesian optimization;
- later active SysID loops.

The estimator should be replaceable without changing the benchmark definition.

## 9.4 Compute budget

Optimizer comparisons must report budget.

Possible normalized budgets include:

```text
number of simulator evaluations
wall-clock time
GPU-seconds / CPU-seconds
number of trajectories consumed
```

A larger search budget should not be silently treated as a better model.

---

# 10. Three benchmark categories must remain separate

The project should distinguish at least three types of comparison.

## 10.1 Model benchmark

Fix:

```text
Oracle
Dataset
Estimator
Budget
```

Vary:

```text
Student model class
```

Question:

> Which model structure predicts the Oracle best under a controlled fitting procedure?

Example:

```text
Coulomb + viscous
vs
Stribeck
vs
Stribeck + load dependence
```

## 10.2 Estimation-algorithm benchmark

Fix:

```text
Oracle
Dataset
Student model class
ParameterSchema
Loss
```

Vary:

```text
Estimator
```

Question:

> Which estimation strategy finds useful parameters most reliably and efficiently?

Example:

```text
nonlinear least squares
vs
CMA-ES
vs
gradient-based optimization
```

## 10.3 End-to-end SysID benchmark

Allow the pipeline to vary:

```text
experiment design
observation strategy
model class
estimator
```

Question:

> Which complete workflow produces the most useful predictive simulator under a defined data and compute budget?

This is the appropriate category for comparing full SysID approaches.

The report must say which category is being evaluated.

---

# 11. Evaluation Protocol

Evaluation should be layered rather than represented by one aggregate score.

The main layers are:

```text
E0 Parameter
E1 Signal
E2 Dynamics
E3 Contact
E4 Whole-body behavior
E5 Task/control
E6 Transfer
```

Not every lab uses every layer.

## E0 — Parameter recovery

Use only when parameters are meaningfully comparable between Oracle and Student.

Possible metrics:

- absolute error;
- relative error;
- normalized error over allowed range;
- group-wise error;
- recovered uncertainty / coverage when available.

Parameter recovery should be marked `N/A` where the Student parameter has no direct physical correspondence to Oracle truth.

Effective simulator parameters must not be scored as though they were physical measurements.

## E1 — Signal prediction

Evaluate observable trajectories such as:

```text
q
qd
current / torque estimate
IMU channels
base pose/velocity
```

Possible metrics:

- MAE;
- RMSE;
- normalized error;
- phase/time alignment diagnostics where appropriate.

Always report held-out conditions separately from fitting data.

## E2 — Dynamics prediction

Examples:

- frequency-response error;
- phase error;
- residual correlation;
- prediction-horizon curves;
- short-window rollout divergence;
- energy/dissipation diagnostics where relevant.

This level is often more diagnostic than a raw trajectory RMSE.

## E3 — Contact prediction

Where contact is present, consider:

- contact timing;
- stance/swing classification;
- normal-force prediction;
- tangential force where comparable;
- slip velocity;
- CoP trajectory where meaningful;
- impact/rebound behavior.

Contact metrics should not be used in free-space benchmarks.

## E4 — Whole-body behavior

Examples:

- base trajectory;
- base orientation;
- CoM behavior;
- foot trajectory;
- gait timing;
- fall/divergence events;
- joint/body error heatmaps.

## E5 — Closed-loop task/control

Run a fixed controller or policy independently in Oracle and Student.

Examples:

- velocity tracking;
- standing stability;
- disturbance rejection;
- action magnitude/smoothness;
- task success rate;
- energy proxy.

This evaluates behavioral similarity of the two closed-loop systems, not same-input open-loop prediction.

## E6 — Policy/control transfer

Train a new controller/policy in the identified Student and evaluate it in the Oracle.

Compare against controlled baselines such as:

```text
policy trained in nominal Student
policy trained in partially identified Student
policy trained in fully identified Student
policy trained directly in Oracle (reference)
```

Report multiple training seeds where RL variance is material.

This is the strongest downstream test of whether the identified simulator is useful for sim-to-real-style learning.

---

# 12. No single benchmark score by default

Avoid immediately constructing:

```text
SysID Score = 0.31 * parameter + 0.42 * trajectory + ...
```

Such a number hides important tradeoffs and encourages optimizing benchmark weights rather than understanding the system.

Default reports should show a metric vector/dashboard.

A later challenge or leaderboard may define a task-specific aggregate score if there is a clear operational reason, but the underlying metrics must remain visible.

---

# 13. Fit, validation, and test splits

The project should distinguish three uses of data.

## Fit

Used directly by the estimator.

## Validation

Used for:

- model-class selection;
- hyperparameter choice;
- deciding whether additional model complexity is justified.

## Test

Held until the final method configuration is chosen.

Synthetic benchmarks should split by meaningful condition, not merely randomly split adjacent timesteps from the same trajectory.

Useful held-out axes include:

- frequency;
- motion family;
- posture;
- amplitude;
- direction;
- payload;
- voltage;
- contact condition;
- terrain;
- policy/task;
- Oracle instance.

This is much stronger than random sample-level train/test splits.

---

# 14. Cross-condition generalization matrix

Serious benchmarks should eventually provide a matrix such as:

| Fit condition | Validation/test condition | Question |
|---|---|---|
| slow sine | fast chirp | did friction fitting generalize to inertia-dominated motion? |
| unloaded | loaded | is load dependence missing? |
| one posture | another posture | are body/actuator effects confused? |
| fixed base | stance | does free-space actuator ID survive loading/contact? |
| straight walking | turning | does the model generalize across task dynamics? |
| one Oracle | another Oracle | is the method overfit to one synthetic truth? |

This matrix should become especially important for Microduck and Microban.

---

# 15. Noise, sensor, and timing benchmark family

Once the noiseless/ideal observation baseline works, introduce measurement realism in stages.

Suggested progression:

```text
N0 noiseless synchronized observations
N1 sensor noise + quantization
N2 filtered/estimated velocity
N3 command + measurement latency
N4 asynchronous rates + jitter
N5 missing/stale samples where relevant
```

Do not introduce all effects at once.

Useful research questions include:

- when does finite-difference velocity dominate parameter error?
- can command delay and measurement delay be separated?
- what happens when policy and actuator rates differ?
- how much does timestamp error bias phase/delay identification?

These experiments should reuse the same Oracle/Student and evaluation contracts rather than become a separate framework.

---

# 16. Model-selection protocol

The model ladder should support a disciplined rule for deciding when to add complexity.

Manual residual diagnosis remains valuable and should be the primary teaching method initially.

Example:

```text
H2 fails validation
residual depends on velocity reversal
        ↓
hypothesis: current friction model is inadequate
        ↓
try H3 with richer friction
```

Later, advanced experiments may compare formal selection criteria such as:

- validation error;
- complexity penalty;
- residual whiteness/structure;
- parameter stability across datasets;
- cross-condition consistency.

The project should avoid automatic complexity growth that improves training loss while making the model uninterpretable or weakly identifiable.

A good model-selection result should answer:

> What new evidence justified the additional model degree of freedom?

---

# 17. Active SysID roadmap

Active experiment design should be an explicit advanced direction but not a prerequisite for the first implementation.

The basic idea is:

```text
current uncertainty
       ↓
choose informative next experiment
       ↓
collect new data
       ↓
update model / uncertainty
       ↓
repeat
```

Conceptually:

```text
u* = argmax InformationGain(u)
```

Examples:

- if inertia is uncertain, choose high-acceleration excitation;
- if low-speed friction is uncertain, choose slow direction reversals;
- if two joint parameters are correlated, choose postures/motions that separate their sensitivities;
- on Microban, choose stable whole-body actions that selectively excite poorly identified joints or parameter groups.

Active SysID is where references such as SPI-Active become directly relevant.

Initial active experiments should remain in synthetic fixed-base settings before being combined with contact and locomotion constraints.

---

# 18. Reproducibility contract

A benchmark result should be reproducible from saved artifacts whenever practical.

Minimum requirements should include:

- repository commit;
- simulator/backend version;
- dependency lock/environment information;
- Oracle config;
- Student config;
- ParameterSchema;
- observation level;
- dataset/rollout IDs;
- estimator config;
- compute budget;
- random seeds;
- metrics;
- visualization/report artifacts.

Policy-based experiments additionally require policy checkpoint identity and observation/action preprocessing metadata.

If exact bit-level reproducibility is not possible across GPU/backends, document the expected reproducibility level and compare statistically.

---

# 19. Suggested benchmark result schema

A run should conceptually produce:

```text
BenchmarkResult
├── benchmark identity
├── Oracle identity / truth difficulty
├── observation level
├── dataset identity
├── Student model identity
├── estimator identity and budget
├── fitted parameters
├── parameter semantics
├── fit metrics
├── validation metrics
├── test metrics
├── prediction-horizon metrics
├── optional contact metrics
├── optional closed-loop metrics
├── optional policy-transfer metrics
├── warnings / identifiability notes
└── visualization/report references
```

The exact serialization format should be derived from the first implemented labs rather than designed exhaustively now.

---

# 20. Benchmark completion criteria

A benchmark should not be considered complete simply because optimization produced parameters.

For a serious benchmark instance, require:

1. Oracle definition is versioned.
2. Student-visible observations are explicitly declared.
3. Privileged truth is isolated from the estimator.
4. Fit and held-out conditions are distinct.
5. Student model and free parameters are documented.
6. Estimator budget is documented.
7. Parameter recovery is reported where meaningful.
8. Predictive validation is reported.
9. Residual/diagnostic plots are generated.
10. Whole-robot experiments include synchronized behavioral visualization.
11. Limitations and unidentifiable parameters are stated.
12. RL/control transfer is reported only when the benchmark is intended to make downstream transfer claims.

---

# 21. Priority: what must be settled before implementation

## P0 — benchmark foundation

These should be stable before rebuilding the first executable labs:

### P0.1 Oracle contract

- what constitutes truth;
- how truth is versioned;
- how truth difficulty is declared.

### P0.2 Observation contract

- Student-visible vs privileged signals;
- standard observation levels;
- timing and metadata semantics.

### P0.3 Evaluation contract

- parameter vs predictive vs downstream metrics;
- fit/validation/test separation;
- benchmark category declaration.

Once these are stable, the first 1-DoF and actuator implementations can serve as executable tests of the contract.

## P1 — first serious actuator/robot benchmarks

Develop alongside L1/L2/L3:

- sensor/noise/timing realism;
- structured model-selection rules;
- Oracle distributions over repeated trials;
- reproducibility tooling.

## P2 — advanced research labs

Add after the base pipeline is reliable:

- active SysID;
- large Oracle-distribution studies;
- cross-engine benchmarks;
- automated experiment selection;
- downstream RL transfer suites.

---

# 22. What not to over-design yet

Do not build a large experiment-management framework before repeated experiments show which abstractions are necessary.

The eventual benchmark may need:

```text
configuration management
parallel execution
artifact storage
caching
experiment registry
W&B / MLflow integration
report comparison
```

but these should emerge from real benchmark workload.

The architecture should first optimize for methodological clarity and reproducibility, not infrastructure completeness.

---

# 23. Relationship to the lab ladder

The contract scales through all labs.

## 1-DoF

Focus on:

- T0/T1 truth;
- O0/O1 observations;
- parameter and signal metrics;
- visualization of identifiability.

## Synthetic actuator

Add:

- realistic observation levels;
- actuator model selection;
- timing/noise studies;
- multiple excitation datasets.

## Fixed-base leg

Add:

- multibody parameter correlation;
- body vs actuator compensation;
- grouped parameters;
- posture generalization.

## Contact leg

Add:

- contact metrics;
- controlled contact experiment design;
- strict separation from already validated free-space parameters.

## Microduck

Add:

- whole-robot behavior;
- fixed-policy closed-loop evaluation;
- component-first vs global-fitting comparison;
- initial policy-transfer evaluation.

## Microban

Add:

- high-dimensional hierarchy;
- shared vs per-joint parameterization;
- full-body coupling;
- larger cross-condition matrix;
- scaling of estimation and data requirements.

## Sim-to-sim

Add:

- T4 truth;
- backend/interface alignment rules;
- parameter correspondence marked explicitly as physical, effective, or non-comparable.

---

# 24. Final benchmark principle

The benchmark should make it difficult to claim success for the wrong reason.

A good result should make clear:

```text
what the hidden world was
what information the method received
what model it was allowed to fit
how much compute/data it used
what it predicted correctly
what parameters were meaningful
what remained unexplained
whether downstream control improved
```

The project should ultimately teach that successful robot SysID is not "finding a low loss". It is building a predictive model under explicit information, model, and validation constraints, while understanding which conclusions the experiment actually supports.
