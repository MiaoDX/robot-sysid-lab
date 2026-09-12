# Happy Path, Identification Boundary, and Identifiability

This document defines the first implementation path for `robot-sysid-lab` and clarifies which ideas are mandatory for the first usable benchmark versus which should remain later research directions.

The project intentionally does **not** try to solve every possible SysID problem before implementation starts. The goal is to establish one clear, end-to-end happy path that is scientifically sound enough to teach from, easy enough to debug, and extensible enough to support later experiments.

The first implementation should therefore optimize for clarity and observability rather than completeness.

> **Scope rule:** Sections 2 and 17 define the first L0 delivery. The larger model ladders, diagnostic catalogs, and visualization suites in the roadmap are references for later lessons, not additional prerequisites for L0. Work status, sequencing, and completion evidence live in [STATUS.md](../STATUS.md); keep the README focused on the project and navigation.

## 1. The happy path

The initial end-to-end path should be:

```text
choose a simple Oracle
  -> define one explicit identification boundary
  -> expose a declared observation set (ideal measurements in L0)
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

## 2. First happy-path benchmark: one default experiment

The first lesson asks one question:

> Can input and motion data recover unknown inertia and viscous damping, and then predict a different motion?

Start with success in a deliberately well-posed problem. Model mismatch is the next lesson, not a requirement to finish the first one.

### Fixed scope

| Decision | L0 default |
|---|---|
| Oracle | `J*qdd + b*qd = u`, with positive inertia `J` and viscous damping `b` |
| Input boundary | Known, actually applied joint torque `u` in N m; unit torque scale is fixed |
| Outputs | Joint position `q` and velocity `qd`, with units and sample times |
| Initial state | Known `q(0)` and `qd(0)`; use the same declared reset for Oracle and Student |
| Unknowns | Only `J` and `b`; all other effects are absent rather than silently fitted |
| Student | Same model structure; deliberately incorrect nominal values for `J` and `b` |
| Observations | Ideal, noise-free `t, u, q, qd`; explicitly label these as an ideal-observation baseline |
| Fitting data | One predetermined chirp containing transient and velocity variation |
| Validation data | One separately generated multisine; no parameter refitting on this trajectory |
| Backend | A small CPU analytical/Python reference; no GPU, RL, or whole-robot dependency |
| Estimator | One bounded nonlinear least-squares fit of simulated motion to fitting observations |
| Result | One generated lesson/report comparing Oracle, nominal Student, and identified Student |

There is no gravity term in this teaching system. It is a rotational inertia with viscous drag, not a vertical pendulum with unmodeled gravity. Coulomb friction, delay, saturation, backlash, and contact are explicitly out of L0 scope.

Known applied torque is an idealized measurement assumption, not a claim that a servo command is a calibrated torque measurement. The L1 actuator lesson will move the boundary upward and model the command-to-torque chain explicitly.

### Data and truth separation

The estimator receives only fitting observations, the public model definition, bounds, and the declared initial state. It must not receive Oracle parameters or internal acceleration. The evaluation/report stage may reveal `J*` and `b*` after fitting to explain the result.

A shared forward-simulation implementation is acceptable for this matched-model baseline. Label it as a self-consistency/recovery exercise, not evidence of robustness to model mismatch or sim-to-real. Keep data generation, fitting, and evaluation interfaces separate even when they reuse numerical code.

### Numerical and estimation choices

Treat sampled torque as zero-order held and document the sample period and integration convention. Use an analytical constant-input solution as a numerical reference, or demonstrate convergence against that reference; sharing code alone must not count as a correctness test. Check zero-input dissipation and finite, physically valid outputs.

Fit bounded `J > 0` and `b > 0` from a non-truth initialization. If both position and velocity contribute to the objective, declare fixed scaling for their different units using fitting data only. Freeze that scaling for validation. Do not feed true acceleration to an easier regression while presenting the result as position/velocity-only identification.

Keep the numerical values for truth, nominal error, bounds, excitation amplitude/frequencies, duration, timestep, and acceptance tolerances together in one versioned example configuration. Establish them during implementation checks, then freeze the released example. Do not keep retuning them against held-out error merely to make the lesson look successful.

### Minimal evidence, not a benchmark matrix

The delivered default run must include:

- fitting and held-out `q`/`qd` overlays for Oracle, nominal, and identified models, with the applied torque shown alongside rather than on a misleading shared-unit axis;
- residual versus time and separate fit/validation error values;
- nominal, fitted, and Oracle `J`/`b` values with declared units and meaningful recovery errors;
- one lightweight sensitivity check for `J` and `b` on the fitting data, interpreted as a local diagnostic rather than a proof of structural identifiability;
- a configuration/metadata record tying the plots and numbers to the same run.

A full FRF suite, 2-D loss landscape, multiple optimizers, extensive seed sweeps, a 3-D viewer, and an interactive website are not L0 acceptance requirements. A few numerical regression starts may be used to check that the estimator did not merely get lucky; they do not turn L0 into an optimizer comparison.

### The next lesson adds one question

After this delivery is accepted, introduce one omitted effect, preferably command delay, and compare a Student without that effect against one that contains it. Update the input boundary, prehistory, and delay resolution before collecting those data. Friction and the richer actuator ladder follow separately.

The first lesson demonstrates that SysID works under clear assumptions. The next lesson demonstrates why those assumptions matter.

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

The catalog below supports later lessons; L0 requires only the lightweight fitting-data sensitivity check in Section 2.

Useful checks include:

### Repeated fits

Run several estimator initializations or nearby datasets.

If prediction remains similar while fitted parameters move substantially, investigate parameter ambiguity, model mismatch, and incomplete optimization separately. Variation between optimizer starts alone is not a parameter-confidence estimate.

### One-parameter sensitivity

Perturb one parameter around the fitted value and measure fitting loss. A separately labeled validation slice may be used for diagnosis, but must not become a hidden model-selection loop over the held-out result.

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

These diagnostics can explain the early teaching labs; running every diagnostic is not a condition for delivering L0.

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
known applied-torque mechanical boundary
one J + b Oracle configuration
ideal t, u, q, qd observations with separate evaluation truth
one fit chirp + one held-out multisine
one matched Student structure, shown before and after fitting
one bounded nonlinear least-squares estimator
numerical reference and repeatability checks
fit / validation separation
J / b comparison and local sensitivity evidence
minimal generated plots + a readable lesson
independent colleague reproduction and explanation
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

## 17. Deliver the first lesson end to end

The next implementation change should deliver the L0 experiment in Section 2, not a framework skeleton. Its result must be useful both to an engineer inspecting the numerics and to a colleague learning SysID.

### Two entrances to the same experiment

**See the result.** Provide a checked-in or durably linked example report generated by the implementation. Lead with Oracle / nominal / identified motion curves, then explain parameter recovery and the held-out result. A reader should not need a simulator or GPU installation merely to understand the lesson. Do not publish illustrative curves as measured benchmark results.

**Reproduce and change it.** Document minimal CPU setup and one real command that regenerates data, fits the Student, evaluates held-out motion, and writes the report. Add that command only when it actually exists. Let a learner change one nominal parameter or excitation setting and rerun the same pipeline.

The recorded report and reproduction route must use the same configuration and computation. Do not maintain a separate animation that merely resembles the actual experiment. Interactive sliders and the documentation website can be added later without blocking this delivery.

### Engineering acceptance

The implementation PR should provide evidence that:

- a clean CPU environment can reproduce the documented default without private assets, robot hardware, a GPU, or an RL checkpoint;
- the integrator agrees with the declared reference, zero-input motion dissipates energy, and invalid parameters fail explicitly;
- fitting cannot read hidden truth or held-out observations, while evaluation can reveal truth only after fitting;
- the default matched model recovers `J` and `b` within documented, numerically justified tolerances and improves held-out prediction over the nominal model;
- config, units, timing, initialization, versions, plots, and metrics agree and are retained with the run;
- a failing fit remains visible as a failure rather than being replaced by a hand-selected or truth-initialized success.

There is no universal numerical threshold set by this design document. Set and justify the first release's tolerances using numerical reference checks; do not adjust them opportunistically after seeing a held-out failure. If the released validation case later influences tuning, keep it as a known regression case and add a fresh held-out case for new generalization claims.

### Learning acceptance

Ask a colleague who did not implement the lab to:

1. identify a mismatch in the nominal model from the plots;
2. reproduce the default experiment and explain what fitting changed;
3. distinguish fitting data from the unseen validation motion;
4. change one exposed setting and explain the resulting behavior;
5. state why an ideal, matched, two-parameter example does not establish real-robot transfer.

Record the feedback and improve the lesson if it depends on the author's verbal explanation. This small walkthrough is enough; a formal learning analytics system is not required.

### Progression after acceptance

Use [STATUS.md](../STATUS.md) for the live checklist and links to implementation evidence. Once L0 works and is understandable, add one model-mismatch lesson, then build L1 synthetic actuator. Extract shared abstractions only after repeated experiments demonstrate a concrete need. The fixed-base leg, contact, Microduck, and Microban remain the subsequent ladder, not prerequisites for the first lesson.

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
