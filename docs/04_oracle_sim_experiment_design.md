# Oracle Simulation and Whole-Robot Experiment Design

This document expands the simulation-first direction of `robot-sysid-lab` into a concrete experimental methodology.

The central idea is to use simulation as a controlled **Oracle world**: a synthetic environment in which the complete ground truth is known to the benchmark author, but hidden from the system-identification pipeline. The student model only receives the observations and commands that would realistically be available on a robot.

This lets us study not only whether an optimizer can reduce trajectory error, but also:

- whether physical parameters are actually recoverable;
- which experiments make a parameter identifiable;
- how missing physics appears in residuals;
- how parameters compensate for one another under model mismatch;
- whether a fitted model predicts motions that were not used for fitting;
- whether an identified simulator improves downstream RL/control transfer;
- how conclusions change when teacher and student use different simulator implementations.

The intended progression remains hierarchical:

```text
single actuator
  -> fixed-base leg
  -> supported contact
  -> whole Microduck
  -> whole Microban
  -> cross-simulator mismatch
  -> later hardware validation
```

The goal is not to jump directly to whole-robot optimization. Each level should introduce only a small number of new uncertainty classes so that failure remains diagnosable.

---

## 1. What is the Oracle?

The Oracle should be treated as a complete synthetic world, not merely as a parameter dictionary.

A useful abstraction is:

```text
Oracle = {
  rigid-body model,
  actuator model,
  transmission model,
  controller implementation,
  delays,
  saturation,
  friction,
  contact model,
  sensor model,
  timing,
  numerical integration settings,
  environment parameters,
  hidden internal states
}
```

For example, a Microduck Oracle may contain:

- the true link masses, centers of mass, and inertias;
- a BAM-style actuator model;
- command delay and observation delay;
- velocity/current/voltage limits;
- Coulomb/Stribeck/load-dependent friction;
- backlash or compliance;
- battery-voltage effects;
- true foot collision geometry;
- ground friction and contact parameters;
- simulation time step and solver settings;
- true internal actuator and contact states.

The identification algorithm should not automatically receive all of this information.

Instead, the Oracle has two roles.

### 1.1 Construction truth

The benchmark author knows exactly which physical and simulator effects were inserted into the teacher.

This lets us measure:

- parameter-recovery error when the teacher/student parameterizations are compatible;
- whether the optimizer converges to a physically correct solution;
- whether multiple parameter sets explain the same data;
- which omitted effect caused a structured residual.

### 1.2 Behavioral truth

For a given initial state and command sequence, the Oracle produces a trajectory:

```text
commands
  -> hidden internal dynamics
  -> states
  -> sensor observations
  -> contact events / forces
```

This trajectory is the behavioral reference for prediction and validation.

This distinction matters because once teacher and student use different model classes or different simulators, there may be no one-to-one mapping between their parameter vectors. In those cases the primary question becomes predictive equivalence rather than exact parameter recovery.

---

## 2. Oracle truth does not mean simulator truth

The Oracle is the truth **inside one controlled benchmark**. It should not be described as an assertion that one physics engine perfectly represents reality.

Before using an Oracle as a benchmark, we should still check basic numerical quality:

- step-size sensitivity;
- integration stability;
- energy behavior where appropriate;
- contact convergence;
- deterministic/repeatable rollout under fixed seeds;
- consistency between recorded command timing and simulated actuation timing.

This is especially important for contact and friction, where numerical settings can change the observed behavior enough to become part of the effective ground truth.

For matched teacher/student studies, the Oracle is mainly a controlled test of identifiability and estimation.

For mismatched teacher/student studies, the Oracle becomes a stand-in for an imperfectly modeled real world.

---

## 3. Simulator choices

A major design choice is which simulation stack should define the Oracle and Student environments.

The project should distinguish three layers that are often conflated:

1. **physics model / engine** — how rigid-body dynamics, constraints, contacts, etc. are solved;
2. **compute implementation / backend** — CPU, Warp/GPU, JAX, etc.;
3. **robot-learning framework** — environment management, observations, rewards, RL training, domain randomization, logging.

Examples:

```text
MuJoCo             physics engine / reference implementation
MuJoCo Warp        GPU implementation of MuJoCo-style simulation
MJX-JAX            JAX implementation in the MuJoCo ecosystem
mjlab              robot-learning framework using MuJoCo Warp
MuJoCo Playground  robot-learning environments around MuJoCo backends
PhysX              different physics engine
Isaac Lab          robot-learning framework commonly using PhysX
BAM                 actuator-modeling library, not a complete robot simulator
```

### 3.1 Recommended first implementation: MuJoCo + mjlab

For the first whole-robot benchmarks, the recommended stack is:

```text
MuJoCo / MuJoCo Warp
        +
mjlab
        +
BAM-style rich actuator models where applicable
```

Reasons:

- Microduck already has an active mjlab/MuJoCo-Warp RL stack;
- Microban also has an mjlab RL stack;
- both ecosystems already use BAM-style actuator modeling;
- existing pretrained or reproducible velocity-control policies can help generate locomotion data;
- the same robot asset can be exercised in fixed-base, supported-contact, and free locomotion configurations;
- large parallel batches are valuable for parameter search and RL training.

CPU MuJoCo should remain useful as a reference/debug backend for smaller experiments and numerical checks.

### 3.2 Do not equate CPU MuJoCo vs MuJoCo Warp with a different physical world

CPU MuJoCo and MuJoCo Warp are useful for backend-consistency studies, but they are not automatically two independent physics hypotheses.

A useful progression is:

```text
A. same simulator, different parameters
B. same simulator, different model structure
C. same physics family, different implementation / timestep / numerical settings
D. genuinely different physics engines
```

We should not jump directly to D because model mismatch is easier to interpret when the numerical and API differences are controlled first.

### 3.3 Candidate second simulator: PhysX / Isaac Lab

A later cross-simulator benchmark can use PhysX through Isaac Lab.

This introduces more meaningful differences in:

- contact implementation;
- joint damping/friction semantics;
- solver behavior;
- constraint handling;
- simulator-native parameterization.

Such a benchmark is closer to the real sim-to-real condition where the student hypothesis class does not contain the teacher exactly.

However, cross-engine experiments require careful normalization of:

- joint ordering;
- coordinate conventions;
- action scaling;
- actuator interpretation;
- controller rates;
- observation timing;
- joint limits;
- collision geometry;
- reset conventions.

Otherwise a supposed physics mismatch may actually be an interface mismatch.

### 3.4 Other candidates

Newton and Genesis may be useful later for targeted studies, especially when differentiated simulation, alternative solvers, or richer multiphysics behavior becomes a concrete research question.

They should not be introduced only to increase the number of supported backends. Every new simulator should answer a specific benchmark question.

---

## 4. Three kinds of sim-to-sim studies

The phrase `sim-to-sim` should be split into three categories.

### 4.1 Model mismatch inside one engine

Example:

```text
Teacher:
  rich BAM-style actuator
  + delay
  + saturation
  + backlash
  + Stribeck/load-dependent friction

Student:
  native PD actuator
  + Coulomb/viscous friction
```

This is the preferred first mismatch experiment because the source of mismatch is interpretable.

Questions:

- which student parameters compensate for the missing teacher physics?
- can training trajectories still be matched?
- where does validation fail?
- do the fitted parameters remain stable across motion families?

### 4.2 Numerical/backend mismatch

Example:

```text
Teacher: MuJoCo Warp, one timestep/solver setting
Student: CPU MuJoCo, another timestep/solver setting
```

Questions:

- are the backends behaviorally consistent?
- how much apparent model mismatch is numerical rather than physical?
- how robust is identification to integration settings?

This is a useful engineering benchmark, but it should not be oversold as an independent-physics test.

### 4.3 Cross-engine mismatch

Example:

```text
Teacher: MuJoCo-based Oracle
Student: PhysX-based simulator
```

Questions:

- can a compact effective parameterization reproduce held-out behavior?
- which quantities remain simulator-specific?
- do contact-heavy motions fail earlier than free-space motions?
- does a policy trained in the identified student transfer back to the Oracle?

This should be introduced after the one-engine experiments are stable.

---

## 5. Whole-robot experiments should not jump directly from air to walking

A core principle is to progressively release constraints and add uncertainty classes.

Recommended stages:

| Stage | Base condition | Contact | Typical controller | Main purpose |
|---|---|---|---|---|
| AIR | trunk fixed | none | scripted joint targets | actuator + rigid-body dynamics |
| SUPPORTED CONTACT | base partly constrained by explicit fixture | controlled | scripted / trajectory controller | contact mechanics without balancing |
| STANCE | floating base | feet on ground | balance / posture controller | load transfer + closed-loop contact |
| LOCOMOTION | floating base | dynamic | RL or locomotion controller | task-distribution behavior |

### 5.1 AIR should mean fixed-base free-space motion

For the first whole-robot experiment, the trunk should normally be fixed in the world while the limbs move under gravity.

This is preferable to simply spawning the robot above the floor, which would create free fall, and preferable to an unmodeled spring suspension, which introduces new unknown dynamics.

The fixed-base experiment is intended to expose:

- actuator dynamics;
- gravity loading;
- link inertias;
- multi-joint coupling;
- posture-dependent residuals;
- parameter correlation.

It does not identify every floating-base parameter by itself. It is one controlled layer in the hierarchy.

### 5.2 SUPPORTED CONTACT should avoid the balancing chicken-and-egg problem

Before asking a robot to walk, we can create contact experiments in which the robot does not need an RL balance policy.

Possible fixtures:

- constrain the trunk in translation/rotation while feet touch the ground;
- allow only vertical base motion;
- use a known prismatic guide;
- control a moving ground platform;
- fix one foot and excite another contact;
- apply known external loads.

The fixture dynamics must be explicit and recorded as part of the experiment, not silently ignored.

Useful contact experiments include:

#### Normal loading/unloading

Vary:

- foot load;
- loading speed;
- knee/ankle posture;
- foot orientation.

Observe:

- normal force;
- penetration/compliance proxy;
- transient response;
- damping/rebound behavior.

#### Tangential slip test

At several normal loads, gradually increase tangential demand until slip occurs.

This is more informative about friction than a standing trajectory that never approaches the friction limit.

#### Controlled touchdown

Use known touchdown velocities/heights while restricting other motion.

Observe:

- impact transient;
- bounce;
- settling;
- contact force profile.

### 5.3 STANCE introduces floating-base balance only after supported contact works

Once free-space and supported-contact prediction are acceptable, remove the fixture and study:

- standing;
- small squats;
- center-of-mass shifts;
- arm/head motion while standing;
- push response;
- left/right load transfer.

This stage tests how previously identified components interact under closed-loop support.

### 5.4 LOCOMOTION is the final dynamic whole-robot stage

Only after the preceding layers should we rely heavily on locomotion trajectories.

Useful held-in / held-out motion dimensions include:

- forward and backward speeds;
- lateral velocity;
- turning rate;
- acceleration/deceleration;
- start/stop transitions;
- different step frequencies;
- disturbances;
- different initial postures.

A single nominal forward walk is not sufficient validation.

---

## 6. Command trajectories must pass through the simulated dynamics

For identification, prescribed trajectories should be treated as **controller targets**, not as direct state assignments at every timestep.

Correct concept:

```text
q_des / tau_des / current command
  -> controller / actuator
  -> saturation / delay / friction
  -> robot dynamics
  -> q, dq, contact, observations
```

Incorrect concept for dynamic identification:

```text
q(t) := reference_q(t)
```

Direct state overwrite is acceptable for initialization/reset, but not for producing a trajectory that is later claimed to contain actuator or rigid-body dynamics.

This rule should be explicit across all labs.

---

## 7. Single-actuator experiment design

The single-actuator benchmark should use an actuator model related to the later robot model rather than becoming an unrelated toy.

Possible test fixture:

```text
actuator
  + known rigid arm / inertia disk / pendulum load
```

Recommended excitation families:

- low-speed bidirectional sweep;
- multiple-amplitude sine;
- chirp;
- multisine;
- step and reversal;
- near-saturation commands;
- several external inertial/gravity loads;
- multiple voltage conditions if voltage is modeled.

Questions:

- can viscous and Coulomb friction be separated?
- when does Stribeck behavior become visible?
- how does delay show up in phase?
- can reflected inertia be distinguished from link inertia?
- do one-direction motions hide friction asymmetry?
- how much does a different payload improve identifiability?

The actuator benchmark should produce priors that can later be reused in the leg and whole-robot experiments.

---

## 8. Fixed-base leg experiment design

The leg benchmark is the bridge from component SysID to whole-robot SysID.

The leg should be extracted from the same robot model when practical so that actuator and rigid-body parameters carry forward naturally.

Recommended experiments:

### 8.1 Single-joint excitation at multiple postures

Example:

```text
hold hip/ankle near prescribed targets
excite knee
repeat at multiple hip postures
```

Purpose:

- separate local actuator behavior from posture-dependent gravity/coupling;
- reveal whether a residual changes with the external mechanical load.

### 8.2 Multi-joint multisine

Assign different spectral content to different joints.

Purpose:

- expose dynamic coupling;
- study parameter sensitivity and correlation;
- compare with one-joint-at-a-time identification.

### 8.3 Correct-actuator / wrong-body

Perturb link mass/CoM/inertia while keeping the actuator correct.

Purpose:

- understand how rigid-body errors appear in residuals.

### 8.4 Wrong-actuator / correct-body

Perturb delay, friction, torque scale, saturation, or reflected inertia.

Purpose:

- understand whether actuator error signatures remain stable across posture.

### 8.5 Both wrong

Allow both classes to vary.

Purpose:

- demonstrate compensating solutions;
- test whether lower-level priors reduce ambiguity.

---

## 9. Microduck whole-robot benchmark

Microduck should be the first complete robot on which the full workflow is exercised end-to-end.

Its role is primarily:

> study how actuator-model fidelity and lower-level priors propagate into whole-robot behavior.

The upstream Microduck RL ecosystem already provides useful task families and BAM-style actuator modeling, making it a good platform for controlled Oracle construction.

### 9.1 MD-A — fixed-trunk whole-robot excitation

Fix the trunk and excite all articulated groups through the real command interface.

Suggested sequence:

1. one joint at a time;
2. symmetric left/right leg motion;
3. anti-phase left/right motion;
4. multisine across leg joints;
5. head/neck excitation separately;
6. mixed head + leg motion.

Why include head/neck?

A locomotion policy may keep these joints in a narrow operating region. Dedicated excitation prevents whole-robot identification from being dominated only by the leg motion distribution.

Validation should use different:

- initial poses;
- amplitudes;
- frequencies;
- phase relationships.

### 9.2 MD-B — supported load and contact

Use a fixture or strong support so the robot can load its feet without requiring a robust walking policy.

Motions:

- shallow squat;
- symmetric loading/unloading;
- left/right weight shift;
- small foot slip tests;
- head motion while loaded.

Questions:

- does a free-space actuator fit still predict behavior under load?
- does load-dependent friction become visible?
- does contact error dominate once actuator error is constrained?

### 9.3 MD-C — free-standing locomotion

Use a stable controller/policy to collect natural whole-robot trajectories.

Minimum command coverage:

- stand;
- start walking;
- forward motion at several speeds;
- stop;
- backward motion;
- lateral motion where supported;
- left/right turns;
- combined translation + rotation.

The fit set and validation set should differ in motion family, not only in random seed.

### 9.4 MD-D — cross-task validation

Later validation may use motions such as:

- sit/stand;
- stand-up;
- fall recovery;
- selected episodic tasks.

These are valuable because they move the robot into state/contact distributions different from ordinary velocity tracking.

However, upstream task implementations may use different collision assets. Collision-model changes must be treated explicitly as experiment configuration, otherwise we may incorrectly attribute a mismatch to the identified dynamics.

### 9.5 Component-first vs global-fit comparison

Microduck should directly compare two workflows on the same Oracle dataset.

#### Route A — hierarchical/component-first

```text
actuator benchmark
  -> leg validation
  -> lock/tightly constrain actuator parameters
  -> supported contact
  -> whole-robot residual fit
```

#### Route B — compact global fit

```text
whole-robot dataset
  -> compact simulator parameterization
  -> PACE-style optimization
```

Compare:

- fit error;
- held-out prediction;
- parameter truth error where meaningful;
- parameter stability across datasets;
- optimization budget;
- cross-motion generalization;
- downstream policy transfer.

---

## 10. Microban whole-robot benchmark

Microban remains the designated small humanoid platform.

Its role should differ slightly from Microduck.

Microduck is the first end-to-end benchmark.

Microban should emphasize:

- higher-dimensional parameterization;
- whole-body coupling;
- parameter sharing;
- per-joint variation around common actuator hardware;
- the effect of arm/head motion on balance and load distribution;
- scaling hierarchical SysID to a more complete humanoid morphology.

Microban uses many actuators of the same nominal servo family, so the first parameter-sharing question should not assume several hardware families. Instead compare:

```text
A. fully independent parameters per joint
B. globally shared actuator parameters
C. shared actuator baseline + per-joint residuals
D. grouped parameters by functional/load class if evidence supports it
```

### 10.1 MB-A — fixed-trunk grouped excitation

With the trunk fixed:

- excite one leg at a time;
- excite both legs symmetrically and anti-symmetrically;
- excite arms separately;
- excite head separately;
- combine arm + leg motion;
- run multisine patterns across selected groups.

This should deliberately cover joints that may not be significantly excited by a walking policy.

Questions:

- do nominally identical servos need independent parameters?
- which per-joint residuals are stable across experiments?
- does sharing parameters improve identifiability and robustness?

### 10.2 MB-B — supported whole-body loading

With explicit support/contact constraints:

- small squat;
- left/right load shift;
- both arms forward/backward;
- asymmetric arm poses;
- head motion while standing;
- controlled foot loading.

This helps expose how upper-body mass distribution and motion affect lower-body dynamics without requiring unrestricted balance.

### 10.3 MB-C — free standing and locomotion

Use a stable velocity-control policy/controller and sample:

- standing;
- forward/backward walking;
- lateral commands;
- turning;
- start/stop transitions;
- push disturbances where stable;
- upper-body command changes while locomoting if the controller supports them.

The point is not only to fit locomotion trajectories. It is to evaluate whether parameters obtained lower in the hierarchy remain predictive under whole-body closed-loop dynamics.

### 10.4 MB-D — parameterization benchmark

Compare at least:

```text
Model A:
  every joint fully independent

Model B:
  shared actuator baseline + joint residuals

Model C:
  compact whole-robot effective parameters
```

Measure:

- train/validation loss;
- ground-truth recovery where meaningful;
- variance across repeated datasets/seeds;
- compute budget;
- held-out locomotion performance;
- downstream policy transfer.

The expected lesson is that giving every joint every free parameter is not necessarily the most informative or robust model.

---

## 11. Does ground motion require an RL policy?

Not all ground experiments require RL.

A useful division is:

```text
single actuator             -> scripted excitation
fixed-base leg              -> scripted excitation
whole robot fixed-base      -> scripted excitation
supported contact           -> scripted / trajectory controller
free stance                 -> classical or learned balance controller
locomotion                  -> RL policy is convenient
```

RL becomes most useful once the experiment requires a robust floating-base behavior over a broad state distribution.

The availability of RL should not determine the earlier experimental design.

---

## 12. Avoiding the RL/SysID chicken-and-egg problem

The apparent loop is:

```text
need a good simulator to train a walking policy
but need walking data to identify a good simulator
```

For the synthetic benchmark this loop can be broken cleanly because the benchmark author owns the Oracle.

The key is to separate three protocols.

---

## 13. Protocol A — Oracle policy collects data; Student replays the recorded command

This is the preferred identification protocol for dynamic ground motion.

### 13.1 Step 1 — obtain a collection policy on the Oracle

Because the Oracle is known to the benchmark author, we can:

- use an upstream pretrained policy if it remains stable in the Oracle;
- fine-tune an upstream policy;
- train a new policy directly in the Oracle.

Once suitable, freeze it as a data-generation policy:

```text
pi_collect
```

The SysID algorithm does not receive the Oracle parameters simply because the benchmark author used them to create the policy.

### 13.2 Step 2 — collect Oracle trajectories

For command/context `c_t`:

```text
u_t^O = pi_collect(o_t^O, c_t)

x_(t+1)^O = F_Oracle(x_t^O, u_t^O)
```

Record the command at the selected plant boundary together with realistic observations.

Examples of possible plant-boundary command:

- `q_des`;
- `q_des, dq_des, Kp, Kd, tau_ff`;
- `tau_des`;
- current command.

The boundary must remain consistent between teacher and student.

### 13.3 Step 3 — replay the same external command in the Student

For each candidate Student parameter vector theta:

```text
xhat_(t+1) = F_Student(xhat_t, u_t^O; theta)
```

Then compare Student observations to Oracle observations.

This means the inner optimization loop is:

```text
candidate parameters
  -> rollout recorded command
  -> compare prediction
  -> update parameters
```

It does **not** contain RL training.

### 13.4 Same command does not mean same internal torque

Suppose the command boundary is desired joint position.

Then both teacher and student receive the same `q_des`, but the student controller should compute control effort using its own simulated state:

```text
tau_student = Kp * (q_des - q_student)
            + Kd * (dq_des - dq_student)
            + tau_ff
```

Do not compute Student torque from Oracle state, because that would artificially keep the Student on the Oracle trajectory.

Similarly, do not replay Oracle true internal motor torque if the purpose of the experiment is to identify the actuator mapping between `q_des` and produced torque.

The replay point must match the declared plant boundary.

---

## 14. Long open-loop locomotion replay can diverge; use prediction windows

A Student with poor parameters may quickly deviate from an Oracle locomotion trajectory.

Because contact is hybrid and highly state dependent, long open-loop replay can become uninformative after the first major phase mismatch.

A practical fitting strategy is **multiple shooting / short prediction windows**.

Conceptually:

```text
Oracle trajectory

|---- window 1 ----|
       |---- window 2 ----|
              |---- window 3 ----|
```

For each window:

1. initialize the Student from an estimated state corresponding to the window start;
2. replay the following recorded command sequence;
3. score prediction error over the window;
4. aggregate many windows across the dataset.

Example candidate horizons for a 50 Hz controller might include 5, 10, and 25 control steps (0.1, 0.2, and 0.5 s). These are experiment starting points, not fixed requirements.

The horizon should be selected empirically:

- too short: little dynamic information and possible overemphasis on local fit;
- too long: contact divergence dominates and gradients/objectives become difficult to interpret.

### 14.1 State initialization needs an explicit rule

A synthetic benchmark gives access to all hidden state, but using hidden Oracle state for every window makes the task artificially easy.

We should distinguish:

#### Privileged baseline

Initialize all Student states that have a meaningful correspondence to Oracle states.

Purpose:

- isolate model/parameter error;
- useful as an upper-bound diagnostic.

#### Realistic observation-constrained benchmark

Initialize only from signals/history that would realistically be available.

Possible methods:

- replay a warmup/history segment;
- initialize measured q/dq but not hidden actuator state;
- estimate hidden state;
- carry delay buffers from the replayed history.

These should be reported separately.

---

## 15. Protocol B — same frozen policy runs closed loop in Oracle and Student

Another useful experiment is to deploy exactly the same policy weights in both worlds.

Then:

```text
u_t^O = pi(o_t^O, c_t)

u_t^S = pi(o_t^S, c_t)
```

Because the observations differ, generally:

```text
u_t^O != u_t^S
```

This is not the same as Protocol A.

Protocol B evaluates **closed-loop behavioral equivalence** under a fixed controller.

Metrics may include:

- velocity tracking;
- trunk orientation;
- fall rate;
- foot slip;
- action magnitude;
- joint-limit usage;
- contact timing;
- energy/current proxies.

This is a strong validation test, but not a pure same-input plant-identification test.

A robust policy can hide some plant mismatch by compensating differently in the two environments, so Protocol B should complement rather than replace Protocol A.

---

## 16. Protocol C — train a new policy in the identified Student, then transfer it back to the Oracle

This is the most important downstream test for sim-to-real relevance.

Workflow:

```text
Oracle generates identification data
        ↓
fit Student model
        ↓
train new RL policy in Student
        ↓
freeze policy
        ↓
run policy in Oracle
```

Inside this benchmark, the Oracle now plays the role of the hidden real robot.

Recommended comparison:

| Training simulator | Purpose |
|---|---|
| original nominal Student | sim-to-Oracle baseline |
| actuator-only identified Student | measure value of component ID |
| actuator + rigid-body identified Student | measure added subsystem value |
| actuator + rigid-body + contact/whole-body identified Student | full method |
| Oracle-trained policy | reference achievable behavior in the known Oracle world |

The Oracle-trained policy is a reference, not necessarily a formal optimal upper bound unless training conditions are perfectly controlled.

For policy-training comparisons, keep as much as possible fixed:

- reward function;
- algorithm;
- observation/action interface;
- training budget;
- curriculum;
- random seeds / number of seeds;
- domain-randomization treatment.

The key downstream question is:

> does identification improve the policy trained in the Student when that policy is evaluated in the Oracle?

---

## 17. Collection policies should not use only one narrow gait

A locomotion policy naturally samples the task-relevant state distribution, but it may provide poor excitation for some parameters.

Therefore the dataset should combine three sources.

### 17.1 Designed excitation

Purpose:

- maximize parameter information;
- deliberately visit reversals, high accelerations, different loads, etc.

### 17.2 Controlled contact experiments

Purpose:

- isolate contact from balance;
- visit slip/loading conditions that normal locomotion might avoid.

### 17.3 Natural task policy trajectories

Purpose:

- cover the state/action distribution actually used by downstream control;
- validate whether the model is useful where it matters.

A good benchmark should demonstrate that these sources answer different questions.

---

## 18. Observation ablation should exploit the synthetic Oracle

One of the largest advantages of simulation is that we can record every internal signal while deciding which signals are visible to the Student.

### 18.1 Omniscient analysis log

For debugging/evaluation, record where available:

```text
q
dq
ddq
base pose/twist
command
controller output
true motor torque/current/voltage
friction torque
contact forces
contact states
actuator hidden states
backlash/compliance states
delay buffers
true parameters
```

### 18.2 Realistic Student observation configurations

Use the observation levels defined in the [benchmark contract](07_benchmark_contract.md#7-observation-levels): O0 is privileged, O1 is realistic-rich, and O2 is realistic-minimal. Representative realistic configurations are:

```text
O1: command + encoder + velocity estimate + current/load estimate + IMU + known controller state/gains
O2: command + encoder + IMU
```

Record the exact signal schema for every experiment. Additional ablations, such as command + encoder only or adding external force/torque measurements, should use descriptive names rather than redefining the O-level numbers.

Add controlled:

- sensor noise;
- quantization;
- filtering;
- clock jitter;
- observation delay;
- dropped samples.

This makes telemetry design itself part of the SysID lesson.

---

## 19. Evaluation should separate three notions of success

Every serious experiment should report three categories independently.

### 19.1 Parameter recovery

When teacher and student parameterizations are compatible:

```text
error(theta_hat, theta_true)
```

This answers whether the identification recovered the known construction truth.

### 19.2 Predictive modeling

On held-out commands/conditions:

- q/dq prediction;
- base pose/twist prediction;
- contact timing;
- force/current prediction where relevant;
- frequency-response error;
- rollout-horizon dependence.

This answers whether the model behaves like the Oracle.

### 19.3 Downstream control/RL transfer

Train or evaluate controllers across Student and Oracle:

- task return;
- success rate;
- tracking error;
- stability/fall rate;
- disturbance recovery;
- energy/action metrics.

This answers whether the model is useful for the actual robotics task.

A parameter set can perform well in one category and poorly in another. That difference is itself a key lesson.

---

## 20. Recommended first whole-robot Oracle configurations

To keep early results interpretable, the first Oracle should not make every part of the robot wrong simultaneously.

### Oracle A — actuator mismatch only

Keep:

- rigid-body model correct;
- contact model correct.

Make teacher actuator richer than the student:

```text
teacher:
  delay
  + saturation
  + BAM-style friction
  + optional backlash

student:
  simpler actuator model
```

Purpose:

- validate the actuator-to-whole-robot hierarchy.

### Oracle B — rigid-body mismatch only

Keep actuator and contact models correct, perturb:

- link mass;
- CoM;
- inertia.

Purpose:

- study compensation against torque scale / armature / damping.

### Oracle C — contact mismatch only

Keep free-space dynamics correct, perturb:

- friction;
- contact softness/damping;
- foot geometry/sole model where practical.

Purpose:

- demonstrate why free-space validation should precede contact fitting.

### Oracle D — combined realistic mismatch

Only after A-C are understood, combine:

- actuator mismatch;
- rigid-body mismatch;
- contact mismatch;
- observation effects.

Purpose:

- approximate the ambiguity of real sim-to-real identification.

---

## 21. Suggested project milestone sequence

### Milestone 1 — Oracle contract

Define:

- parameter truth schema;
- observation policy;
- command boundary;
- experiment metadata;
- hidden-state handling;
- fit/validation/test splits;
- reporting format.

### Milestone 2 — actuator Oracle

Deliver:

- rich teacher actuator;
- progressively simpler student models;
- excitation benchmark;
- observation ablation;
- parameter truth comparison.

### Milestone 3 — fixed-base leg

Deliver:

- one robot-derived leg model;
- actuator/body mismatch matrix;
- sensitivity and parameter-correlation analysis;
- hierarchical priors.

### Milestone 4 — whole-robot AIR + supported contact

Deliver:

- fixed-trunk Microduck excitation;
- supported contact fixture;
- no-RL contact datasets;
- validation that lower-level parameters remain predictive.

### Milestone 5 — Microduck locomotion

Deliver:

- Oracle collection policy;
- Protocol A command-replay fitting;
- Protocol B fixed-policy closed-loop validation;
- Protocol C train-in-Student / test-in-Oracle evaluation.

### Milestone 6 — Microban scaling

Deliver:

- full-body grouped excitation;
- shared vs independent actuator parameterizations;
- upper-body/leg coupling experiments;
- free-standing/locomotion validation;
- hierarchical fitting study.

### Milestone 7 — cross-simulator benchmark

Deliver:

- backend/interface normalization;
- one controlled cross-engine task;
- comparison of physical vs effective parameters;
- policy transfer across identified simulator boundary.

---

## 22. Core experimental principles

1. **The Oracle is known to the benchmark author but hidden from the estimator.**
2. **Synthetic ground truth is for evaluation, not privileged fitting unless explicitly labeled.**
3. **Use the same command boundary in teacher and student.**
4. **Do not replay Oracle internal torque when the actuator itself is the identification target.**
5. **Do not directly overwrite states to generate supposedly dynamic data.**
6. **Introduce uncertainty classes progressively: actuator -> body -> contact -> floating base.**
7. **Use supported-contact experiments to avoid requiring RL for every ground test.**
8. **Use an Oracle policy for locomotion data without putting RL training inside the parameter-optimization loop.**
9. **Separate same-input prediction, same-policy closed-loop behavior, and train-in-Student/test-in-Oracle transfer.**
10. **A locomotion policy is not an excitation oracle; combine policy data with designed experiments.**
11. **Report parameter recovery, prediction quality, and downstream transfer separately.**
12. **Do not interpret CPU/Warp differences as independent physics without evidence.**
13. **Introduce genuinely different physics engines only after one-engine model-mismatch experiments are stable.**
14. **Microduck should prove the complete workflow; Microban should stress scaling, whole-body coupling, and parameter sharing.**
15. **The eventual hardware workflow should reuse the same experiment and validation contracts developed here.**

---

## 23. Resulting project narrative

The intended story of the repository becomes:

```text
1. Build a rich synthetic Oracle.
2. Know every hidden truth, but expose only realistic observations.
3. Design motions that make selected dynamics observable.
4. Fit progressively richer Student models.
5. Use residuals and held-out conditions to diagnose missing physics.
6. Move from actuator to leg to supported contact.
7. Run the complete whole-robot pipeline on Microduck.
8. Scale parameter sharing and whole-body coupling studies to Microban.
9. Introduce cross-simulator mismatch only after the controlled hierarchy works.
10. Evaluate whether identified models actually improve controller/RL transfer back into the Oracle.
11. Later repeat the same methodology on hardware, where the true parameters are no longer available.
```

This preserves the strongest advantage of simulation: complete ground truth and experimental control, while still forcing the identification pipeline to operate under realistic observation and model limitations.
