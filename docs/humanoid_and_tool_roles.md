# From BAM and PACE to a Humanoid SysID Pipeline

BAM, PACE, MuJoCo SysID, and SPI-Active are related but operate at different boundaries.

## Role separation

| Tool / method | Best viewed as | Typical boundary | Main strength |
|---|---|---|---|
| BAM | component-level actuator modeling | one actuator / actuator family | explicit model structure and friction/motor fidelity |
| PACE | whole-simulator trajectory matching | robot joint dynamics | global behavior matching with a compact parameterization |
| MuJoCo SysID | generic simulator parameter optimization | arbitrary MuJoCo model | reusable nonlinear least-squares infrastructure |
| SPI-Active | active experiment design + SysID | robot / controller interaction | choose informative commands instead of relying only on hand-designed excitation |

The tools are not strict substitutes.

## When BAM may be enough

A BAM-style workflow can be sufficient when:

- actuator dynamics dominate the real-sim gap;
- rigid-body geometry and inertias are already accurate enough from CAD;
- the robot is small and mechanically stiff;
- held-out whole-robot trajectories validate well;
- RL performance transfers with only narrow domain randomization.

This is a plausible outcome for small servo-driven robots such as Microduck-class systems.

## When PACE-style whole-robot matching still helps

Use a PACE-style residual/global fit when:

- whole-robot behavior still differs after component ID;
- there are per-joint residuals, global delay, effective armature, or damping mismatch;
- rigid-body or contact parameters are uncertain;
- simulator-native parameters need tuning for the downstream training environment;
- the objective is behavioral prediction rather than recovery of every physical parameter.

A useful hierarchy is:

```text
BAM-style component ID
  -> lock or tightly bound actuator-family parameters
  -> per-joint calibration/residuals
  -> limb-level validation
  -> PACE/MuJoCo whole-robot residual matching
  -> narrow domain randomization
```

This reduces parameter compensation because the global optimizer no longer has complete freedom to use one wrong parameter to hide another missing effect.

## Humanoid actuator boundaries

A humanoid joint is often not an integrated hobby servo. The boundary may be:

### Position/impedance interface

Input:

```text
q_des, dq_des, Kp, Kd, tau_ff
```

Model the controller, delay, saturation, torque scale, reducer friction, and any relevant compliance above the hidden FOC/current loop.

### Torque interface

Input:

```text
tau_des
```

A practical hierarchy is:

```text
ideal torque
  -> torque scale / bias
  -> delay
  -> current/torque saturation
  -> velocity-dependent torque limits
  -> friction
  -> reflected inertia
  -> compliance / resonance / backlash
  -> thermal and voltage effects if needed
```

### Current interface

Input:

```text
i_q_des
```

Now torque constant, current-loop bandwidth, voltage limits, back-EMF, and thermal/current clipping may become part of the plant boundary.

The rule is to model only the lower-level dynamics that materially affect the bandwidth and behavior seen at the selected interface.

## Recommended humanoid staging

### Stage 0 — calibration

Before dynamic ID, verify:

- joint zero and direction
- encoder scale
- gear ratio
- torque/current sign
- torque scale sanity
- timestamping and loop timing

### Stage 1 — actuator-family bench ID

For each hardware family, characterize:

- torque/current mapping
- delay
- saturation
- friction versus velocity/load
- bandwidth / frequency response
- temperature and voltage sensitivity if relevant

### Stage 2 — fixed-base articulated subsystem

Use one leg or arm to separate actuator effects from rigid-body mass/CoM/inertia mismatch. Prefer free-space tests before contact.

### Stage 3 — contact subsystem

Add foot-ground interaction only after free-space prediction is acceptable.

### Stage 4 — whole-robot residual matching

Run PACE-style or MuJoCo-native optimization with lower-level parameters fixed or strongly regularized.

### Stage 5 — robust training

Use the identified model as the center of the training distribution and randomize only the uncertainty that remains supported by measurement or manufacturing variation.

## Frequency-domain validation

Trajectory matching should be paired with actuator frequency-response characterization.

A time-domain optimizer can sometimes trade inertia, damping, and delay against each other. A Bode/FRF view can expose:

- missing delay through phase slope;
- flexible modes through resonance/anti-resonance;
- insufficient model order;
- bandwidth mismatch that a single trajectory hides.

If validation repeatedly shows a frequency-localized residual, the next step is often a richer model structure, not a larger CMA-ES budget.

## Physical versus effective parameters

Always label fitted values according to their interpretation:

- **physical**: independently measurable and tied to a real quantity;
- **effective**: simulator parameter that improves prediction but may absorb omitted physics.

For humanoid engineering, both are useful, but they should never be confused.
