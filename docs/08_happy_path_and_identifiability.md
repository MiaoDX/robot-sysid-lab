# Happy Path, Identification Boundary, and Identifiability

This document defines the first implementation path for `robot-sysid-lab` and clarifies which ideas are mandatory for the first usable benchmark versus which should remain later research directions.

The project intentionally does **not** try to solve every possible SysID problem before implementation starts. The goal is to establish one clear, end-to-end happy path that is scientifically sound enough to teach from, easy enough to debug, and extensible enough to support later experiments.

The first implementation should therefore optimize for clarity and observability rather than completeness.

## 1. The happy path

The initial end-to-end path should be:

```text
choose a simple Oracle
  -> define one explicit identification boundary
  -> expose a realistic but sufficient observation set
  -> design one informative excitation
  -> fit one Student model family
  -> validate on held-out conditions
  -> compare against hidden truth where the parameters are identifiable
  -> visualize the result
```

The recommended first sequence is:

```text
L0: 1-DoF analytical system
  ->
L1: synthetic actuator
```

Only after those work well should the same contracts be applied to:

```text
fixed-base leg
  -> contact
  -> Microduck
  -> Microban
```

The first implementation should prefer one good example over a large matrix of incomplete variants.

## 2. First happy-path benchmark

A useful first benchmark can be intentionally constrained.

### Oracle

Use a simple actuator/plant model with a small number of known effects, for example:

```text
inertia
+ viscous friction
+ Coulomb friction
+ command delay
```

The Oracle may expose additional privileged internal signals for debugging and visualization, but those signals should not automatically be available to the Student estimator.

### Identification boundary

Choose one command interface and keep it explicit.

For the first lab, a good boundary is:

```text
Input:
applied or commanded joint torque

Plant includes:
mechanical inertia
friction
command delay if placed inside the boundary

Output:
joint position and velocity
```

A later actuator lab can move the boundary upward to position/impedance commands and include the lower-level controller and actuator physics.

### Observation set

Start with a realistic but convenient set:

```text
command
joint position
joint velocity
timestamps
```

Do not begin by simultaneously modeling sensor quantization, packet loss, unknown filters, and timestamp jitter.

Those are valuable later experiments, but they should not obscure the first end-to-end pipeline.

### Excitation

Use one or two clearly informative signals, such as:

```text
chirp for fitting
multisine or different chirp for validation
```

The goal is to establish the complete workflow before comparing every excitation family.

### Student models

Use a short model ladder rather than many competing implementations:

```text
H0: inertia only
H1: inertia + viscous friction
H2: + Coulomb friction
H3: + delay
```

The first benchmark should demonstrate both successful parameter recovery in a matched-model case and predictable residual structure in a deliberately simpler Student model.

### Estimation

Use one estimator that is robust enough for the first problem.

The first benchmark does not need to compare CMA-ES, Gauss-Newton, random search, Bayesian optimization, and gradients all at once.

Optimizer comparison should come only after the model/data contract itself is trusted.

### Validation

At minimum:

```text
fit condition
held-out input trajectory
parameter comparison where meaningful
residual plots
prediction error over time
```

This is enough to establish the benchmark language used by later labs.

## 3. Identification boundary must be explicit

A SysID result only has meaning relative to the system boundary being identified.

Robots contain several nested systems:

```text
policy
  -> high-level command
     -> controller / firmware
        -> actuator
           -> transmission
              -> rigid-body dynamics
                 -> contact
                    -> sensors
                       -> policy
```

Different experiments may intentionally identify different boundaries.

### Boundary A — mechanical plant

Example:

```text
Input:
physical joint torque

Included:
rigid-body dynamics
friction
compliance if modeled

Output:
q, qd
```

This is appropriate for teaching rigid-body and mechanical parameter identification.

### Boundary B — actuated joint

Example:

```text
Input:
q_des, qd_des, Kp, Kd, tau_ff

Included:
firmware/controller
command delay
saturation
actuator
transmission
mechanical joint/load

Output:
encoder q, qd
```

This is often closer to what an upper-level robot controller actually sees.

BAM-style actuator characterization naturally fits near this boundary when the lower-level actuator behavior is explicitly modeled.

### Boundary C — closed-loop whole robot

Example:

```text
Input:
velocity or task command

Included:
policy/controller
actuator
robot
contact

Output:
whole-robot behavior
```

This boundary can be useful for behavioral matching, but the resulting parameters are usually more effective and less physically interpretable.

Whole-robot validation can use this boundary even if the earlier identification stages use a lower one.

### Required benchmark header

Every serious benchmark should eventually state something equivalent to:

```text
Identification boundary

Input:
...

Included dynamics:
...

Excluded dynamics:
...

Student-visible observations:
...

Privileged evaluation-only signals:
...
```

This should become a normal part of experiment reports.

## 4. Ground truth does not imply parameter identifiability

Synthetic simulation provides complete ground truth, but knowing the true parameters does not mean the observations uniquely determine those parameters.

This distinction is central.

Consider a simplified actuator model:

```text
J qdd + b qd + Fc sign(qd) = kt u
```

Under some experiment and observation choices, multiple parameter combinations can produce nearly indistinguishable motion.

A fitted parameter set can therefore differ from the Oracle truth while still reproducing the observable behavior.

The benchmark must distinguish:

```text
parameter recovery failure
from
parameter non-identifiability
```

## 5. Practical identifiability vocabulary

The project should use a simple qualitative vocabulary first.

### Structurally identifiable

Under ideal noise-free data and the chosen model structure, the parameter can in principle be uniquely determined.

### Practically identifiable

The parameter is sufficiently excited and constrained by the actual experiment to be estimated with useful precision.

### Weakly identifiable

The data contains some information about the parameter, but strong correlation or low sensitivity makes the estimate unstable.

### Unidentifiable

The experiment and observations do not uniquely constrain the parameter.

The first implementation does not need a complete symbolic-identifiability engine.

It does need enough diagnostics to avoid misleading conclusions.

## 6. How the happy path should handle identifiability

The first benchmark should follow a conservative rule.

For parameters expected to be practically identifiable:

```text
report parameter recovery error
```

For parameters that are weakly identifiable or intentionally ambiguous:

```text
report predictive behavior
report parameter sensitivity / instability
avoid claiming physical recovery
```

This keeps the ground-truth advantage without turning every unknown parameter into a mandatory recovery target.

## 7. Simple diagnostics before advanced theory

The first implementation can use practical evidence rather than sophisticated theory.

Useful checks include:

### Repeated fits

Run several estimator initializations or nearby datasets.

If prediction remains similar while fitted parameters move substantially, parameter ambiguity is likely.

### One-parameter sensitivity

Perturb one parameter around the fitted value and measure validation loss.

A nearly flat curve indicates weak practical sensitivity.

### Two-parameter loss slices

For selected pairs, visualize:

```text
loss(theta_i, theta_j)
```

A narrow isolated basin suggests better localization.

A long valley suggests parameter correlation or compensation.

### Cross-excitation stability

Fit with one excitation and repeat with another.

A physically meaningful parameter should not move dramatically without a reason tied to model mismatch or operating-condition dependence.

These diagnostics are sufficient for the first teaching labs.

Later work can add sensitivity matrices, singular values, Fisher-information-like metrics, profile likelihoods, posterior approximations, or symbolic analysis.

## 8. Successful behavior can matter more than exact parameter recovery

The project should preserve two distinct questions:

```text
Did we recover the physical truth?
```

and

```text
Did we build a predictive model for the intended operating region?
```

For a matched, identifiable synthetic problem, both should be possible.

For model-mismatch or high-dimensional whole-robot problems, exact parameter recovery may be neither possible nor necessary.

This is where the existing distinction between physical and effective parameters becomes important.

A useful result can therefore be:

```text
physical parameter recovery: uncertain
behavior prediction: strong
interpretation: effective simulator parameter
```

as long as the report says so explicitly.

## 9. Do not turn identifiability into a blocker for the first implementation

The first lab should deliberately choose a problem where the key parameters are reasonably identifiable under the selected excitation.

That gives the project a clean happy path.

Then add explicit failure cases later:

```text
slow excitation hides inertia
one-direction motion hides asymmetric friction
limited operating range makes multiple parameter sets equivalent
unknown torque scale correlates with mechanical parameters
```

This sequencing is important.

The project should first show:

> SysID can work when the problem is well posed.

Then show:

> Here is how and why it fails when the problem is poorly posed.

## 10. Happy path for the synthetic actuator

After the 1-DoF concept lab, the first serious reusable benchmark should be a synthetic actuator.

A reasonable initial path is:

```text
Oracle actuator
  -> realistic command interface
  -> rich-enough but controlled friction/delay model
  -> chirp/reversal data
  -> Student model ladder
  -> parameter fitting
  -> held-out trajectory validation
  -> residual and FRF visualization
```

Do not initially combine all of the following:

```text
backlash
compliance
thermal dependence
voltage sag
sensor timing jitter
load-dependent friction
cross-simulator mismatch
active excitation
```

Instead, add one new uncertainty class at a time after the baseline works.

## 11. Happy path for Microduck and Microban

The whole-robot stages should follow the same principle.

### Microduck

First whole-robot path:

```text
known Oracle configuration
  -> fixed-base joint excitation
  -> supported stance/load-shift data
  -> frozen Oracle-policy locomotion data
  -> fit a compact Student parameter set
  -> validate on held-out motion commands
  -> compare nominal vs identified rollout
```

The first version should keep rigid-body/contact truth mostly fixed while changing a controlled subset of actuator parameters.

Later versions can add body/contact mismatch.

### Microban

First Microban path:

```text
reuse the validated Microduck methodology
  -> group joints by common actuator assumptions
  -> fit shared base parameters + small per-joint residuals
  -> validate whole-body coupling and locomotion
```

Do not make the first Microban benchmark simultaneously test every possible per-joint parameter, contact parameter, sensor effect, and optimizer.

Its first purpose is to test whether the hierarchical methodology scales to a more complete humanoid.

## 12. Counterfactual validation is valuable, but not a first-version requirement

Synthetic Oracle models give the project a powerful later capability: interventions can be applied consistently to both Oracle and Student.

Examples:

```text
increase payload
change controller gain
reduce supply voltage
change contact friction
modify one link mass
```

This asks a stronger question than held-out trajectory validation:

> Does the identified model predict what happens when the system itself is changed?

This is particularly useful for separating physically meaningful models from trajectory-specific effective fits.

However, counterfactual validation should remain a later benchmark family.

The first happy path only needs held-out motions and operating conditions.

## 13. SysID-informed domain randomization is a later closed-loop research direction

The eventual RL pipeline should investigate:

```text
SysID
  -> nominal model
  -> remaining uncertainty
  -> targeted domain randomization
  -> policy training
  -> Oracle evaluation
```

Interesting future comparisons include:

```text
arbitrary wide DR
identified nominal only
SysID-informed independent DR
SysID-informed correlated DR
```

This can test whether better uncertainty characterization leads to better transfer, less conservative policies, or improved sample efficiency.

The first implementation does not need to derive DR distributions from SysID results.

The initial RL goal is simpler:

```text
train in nominal Student
vs
train in identified Student
then evaluate both in Oracle
```

That is enough to test whether improved model prediction helps policy transfer.

## 14. Active SysID also stays off the first happy path

Active experiment design remains an important advanced direction.

Later, the system may choose new excitation based on current uncertainty:

```text
current fit
  -> identify poorly constrained parameters
  -> propose informative motion
  -> collect more data
  -> refit
```

This may eventually connect to SPI-Active-style ideas.

For the first implementation, use manually designed excitation with clear educational intent.

## 15. What is mandatory now versus later

### P0 — first implementation

Required:

```text
one explicit identification boundary
one Oracle configuration
one realistic observation set
one clear excitation protocol
one Student model ladder
one estimator
fit / validation separation
parameter truth comparison where identifiable
basic practical-identifiability diagnostics
standard visualization/report output
```

### P1 — after the happy path works

Add selectively:

```text
noise and timing effects
observation ablation
stronger model mismatch
multiple excitation families
optimizer comparison
parameter sharing
whole-robot residual fitting
sim-to-sim implementation differences
```

### P2 — advanced research

Later:

```text
Oracle distributions at scale
counterfactual interventions
SysID-informed uncertainty / domain randomization
active SysID
cross-engine studies
hardware validation
```

This ordering should prevent the project from becoming blocked by unresolved advanced questions.

## 16. Architecture freeze criterion

The design work is sufficient to begin implementation once the project has agreement on:

```text
1. what the first Oracle is;
2. what the first identification boundary is;
3. what the Student can observe;
4. which parameters the first experiment intends to identify;
5. what held-out validation means;
6. what plots/reports constitute a complete result.
```

Everything else can evolve from implementation experience.

The repository should not require agreement on every future simulator, optimizer, storage backend, interactive UI technology, active-learning method, or domain-randomization strategy before the first lab is built.

## 17. Recommended immediate next step

After this architecture PR is merged, the next implementation work should be intentionally narrow:

```text
Step 1
rebuild L0 1-DoF as a clean benchmark

Step 2
verify the experiment/result/report contract

Step 3
build the L1 synthetic actuator benchmark

Step 4
only then extract reusable abstractions from repeated code
```

The first implementation PR should aim to produce one convincing experiment with complete visualization rather than a generic framework skeleton.

## 18. Core principle

The project should be ambitious in the questions it eventually explores, but conservative in how many uncertainties it introduces at once.

The preferred progression is:

```text
make one simple SysID problem work
  -> make its failure modes visible
  -> introduce one new uncertainty class
  -> validate again
  -> scale the same reasoning to larger robots
```

The purpose of the architecture is to support that progression, not to predict every future requirement before code exists.
