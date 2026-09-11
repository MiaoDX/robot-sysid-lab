# BAM, Microduck, and Articulated-Limb Experiments

This track turns SysID concepts into concrete robot experiments. The intended progression is:

```text
single servo bench
  -> fixed-base multi-joint limb
  -> limb + contact
  -> whole Microduck
  -> small humanoid / Microban
```

The point is not to reproduce every upstream implementation detail. The point is to use a small, open robot stack to teach the complete loop:

```text
experiment design
  -> data collection
  -> model selection
  -> parameter fitting
  -> held-out validation
  -> simulator integration
  -> RL / control evaluation
```

## 1. BAM servo bench

Primary upstream reference:

- BAM (Better Actuator Models): https://github.com/rhoban/bam

Recommended first experiments:

1. **Single pendulum identification**
   - one servo, arm, known mass, known length
   - record commanded position and measured position
   - reproduce a BAM-style fit

2. **Model-class comparison**
   - start with simple Coulomb/viscous friction
   - compare against richer BAM friction models
   - report both fit error and held-out error

3. **Excitation comparison**
   - slow sine
   - chirp
   - multisine
   - lift-and-drop / passive backdrive
   - direction reversals

4. **Condition shift**
   - different payload
   - different command gain / Kp
   - different supply voltage
   - forward versus backward motion

5. **Deliberate model mismatch**
   - add backlash or a compliant coupler to the physical or synthetic plant
   - attempt to fit it with a rigid model
   - show parameter compensation and validation failure

## 2. What to measure

At minimum:

- command timestamp
- measured joint position
- measured or estimated velocity
- command target
- available current / load / torque estimate
- supply voltage
- control mode / gain

If available, add:

- motor temperature
- driver temperature
- bus latency / loop timing
- external load-cell torque

The goal is to make timing and operating conditions explicit rather than hiding them inside a single trajectory file.

## 3. Microduck whole-robot experiments

Microduck is useful because it connects realistic actuator modeling to a complete MJLab/MuJoCo RL stack.

Suggested experiment matrix:

| Model | Added effects | Question |
|---|---|---|
| A | ideal PD | how far can a simple actuator model go? |
| B | simple friction | how much does friction matter? |
| C | BAM-style rich actuator | does component fidelity improve prediction? |
| D | + delay | is timing part of the gap? |
| E | + battery / voltage effects | how much does supply variation matter? |
| F | + backlash | does model structure matter more than more fitting? |

For each model, compare:

- trajectory prediction on fixed motions
- held-out motion prediction
- RL policy behavior in simulation
- if hardware is available, sim-to-real task performance

## 4. BAM versus PACE inside the same example

A useful teaching comparison is:

- **BAM-style route**: identify the local actuator with an explicit model family.
- **PACE-style route**: optimize a smaller set of simulator parameters so whole-robot trajectories match.

Both can reduce real-sim error, but the fitted parameter meanings can differ. The same Microduck dataset can be used to demonstrate this distinction.

## 5. Small humanoid extension

After Microduck, repeat the same methodology on a small open humanoid such as Microban or another MJLab-compatible platform:

- identify actuator-family parameters first
- reuse them across joints of the same hardware family
- fit only small per-joint residuals where needed
- move from fixed-base motions to whole-body motions
- keep a separate validation task set

This provides a much cleaner bridge to a full humanoid than jumping directly from one servo to a 20–30 DoF robot.
