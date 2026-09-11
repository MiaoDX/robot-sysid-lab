# Generic Robot / Actuator SysID Framework

The framework should not be tied to BAM, PACE, CMA-ES, hobby servos, or a single simulator. The reusable unit is an identification experiment with explicit boundaries.

## Core abstractions

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

### Plant

A real robot subsystem or a synthetic teacher. It exposes commands, measurements, timing, and reset behavior, but does not need to reveal internal parameters.

### Model

A candidate hypothesis class. Examples:

- ideal position/torque actuator
- rigid actuator with scale and delay
- Coulomb/viscous friction
- Stribeck or load-dependent friction
- motor + transmission + reflected inertia
- two-mass compliant transmission
- actuator with backlash/hysteresis

### ParameterSchema

Defines the free parameters, units, bounds, priors, sharing rules, and whether a quantity is:

- global,
- actuator-family level,
- per-joint,
- body/link level,
- contact level.

This is important for humanoids: identical actuator modules should usually share strong priors rather than giving every joint an unconstrained copy of every parameter.

### Excitation

Should include at least:

- sine / chirp
- multisine
- PRBS-like inputs where appropriate
- step / reversal / lift-drop tests
- fixed trajectories
- active or information-maximizing experiment design

### SimulatorBackend

Initial priority:

1. MJLab / MuJoCo Warp for large parallel batches.
2. CPU MuJoCo for high-quality small-parameter baselines.
3. Optional differentiable/JAX backends later.

Do not assume that parameters with the same name have identical semantics across MuJoCo, PhysX, Bullet, or custom actuator code.

### Optimizer

Keep the optimizer replaceable:

- linear / weighted least squares
- nonlinear least squares / Gauss-Newton
- CMA-ES
- random / massive parallel sampling
- Bayesian optimization
- gradient-based / differentiable methods

PACE is one useful solver strategy, not the framework itself.

## Actuator boundary

Choose the model boundary at the interface actually exposed to the upper-level controller.

| Hardware/control interface | Natural model input |
|---|---|
| integrated position servo | `q_des` / gain parameters |
| current-controlled drive | `i_q_des` |
| torque-controlled joint | `tau_des` |
| Unitree-style joint API | `q_des, dq_des, Kp, Kd, tau_ff` |
| low-level PMSM drive | voltage/current/FOC variables |
| series elastic actuator | motor-side and joint-side states |

Do not model PWM/FOC detail unless the omitted dynamics are actually relevant at the chosen boundary and operating bandwidth.

## Suggested actuator model ladder

Use the smallest model that passes held-out validation.

- **H0**: ideal actuator
- **H1**: gain/torque scale + delay
- **H2**: + saturation / velocity-dependent limits
- **H3**: + Coulomb and viscous friction
- **H4**: + Stribeck, asymmetry, or load-dependent friction
- **H5**: + reflected inertia / motor-side dynamics
- **H6**: + compliance or backlash
- **H7**: + voltage, thermal, wear, or hysteresis effects if evidence requires them

Promotion from one level to the next should be justified by residual structure, frequency-response mismatch, or cross-condition validation failure.

## Validation rules

Every experiment should report more than fit loss:

- held-out trajectory error
- parameter stability across datasets
- sensitivity / practical identifiability
- residual correlation with state, load, voltage, temperature, direction, and time
- frequency-response mismatch where applicable
- whether fitted parameters are physical or effective simulator parameters

The intended outcome is a predictive model with the minimum useful complexity, not a maximally detailed model.
