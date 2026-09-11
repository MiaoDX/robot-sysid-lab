# Articulated-Limb SysID: the Missing Middle Layer

A single actuator is too simple to teach multibody coupling, while a whole humanoid introduces too many simultaneous failure modes. A fixed-base leg is the useful middle layer.

## Stage A — fixed-base leg in free space

Extract one leg from the robot model and rigidly fix the pelvis/base. Keep the same link inertias, joint limits, and actuator models used by the whole robot.

The subsystem dynamics become

\[
M(q)\ddot q + C(q,\dot q)\dot q + g(q) + \tau_f = \tau.
\]

There is no floating-base state and no contact force. This is the cleanest place to introduce:

- dynamic coupling between joints;
- posture-dependent gravity loading;
- separation of actuator parameters from rigid-body parameters;
- multi-joint excitation;
- parameter correlation and practical identifiability.

## Recommended experiments

### A1. One joint at a time

Hold hip and ankle fixed and excite the knee with a chirp. Repeat at several hip postures.

If the residual changes strongly with posture, the problem may be in mass/CoM/gravity modeling rather than only in the knee actuator model.

### A2. Simultaneous multisine excitation

Excite hip, knee, and ankle at different frequencies. Compare parameter sensitivity with the single-joint experiment.

This demonstrates that identifiability depends on the experiment, not only on the estimator.

### A3. Actuator-correct / body-wrong

Use the true actuator model but perturb thigh/shank mass or CoM in the student model. Fit only rigid-body residual parameters.

### A4. Body-correct / actuator-wrong

Keep CAD parameters correct and perturb torque scale, friction, inertia, or delay.

### A5. Both wrong

Perturb both classes and inspect parameter compensation. For example, increased link mass may be partly compensated by increased torque scale over a narrow trajectory family.

## Stage B — add contact

Once free-space prediction is validated, place the foot on the ground:

\[
M(q)\ddot q + h(q,\dot q) = \tau + J_c^T\lambda.
\]

Now introduce only one new uncertainty class: contact.

Candidate effects:

- coefficient of friction;
- normal compliance/damping;
- foot geometry;
- sole compliance;
- slip/stick transition.

The lesson is diagnostic ordering:

```text
actuator OK?
  -> articulated rigid-body model OK?
  -> contact model OK?
  -> floating-base / whole-body model OK?
```

## Hierarchical identification

A scalable workflow can carry priors upward:

```text
actuator-family ID
  -> per-joint residual calibration
  -> limb-level rigid-body ID
  -> contact ID
  -> whole-robot residual matching
```

Parameters identified at a lower level should be fixed or tightly bounded at higher levels unless validation provides evidence that they need to move. This reduces compensating solutions and makes whole-robot optimization easier to interpret.
