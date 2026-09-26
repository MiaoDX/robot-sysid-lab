# L1 Development Plan: Servo-Driven Loaded Pendulum

**Status:** implemented; engineering gates verified; independent learner acceptance pending
**Track:** synthetic lab
**Predecessor:** L0 inertia and damping
**Plan rule:** implementation authorized by the user; preserve the four-wave scope below.

## Current evidence

The numerical module, frozen v2 config, report, notebook, four-page lesson and
Marimo app are implemented. [Verification](../../reports/l1_servo_loaded_pendulum/verification.md)
records 30 passing tests, clean CPU reproduction, executed notebook, and real
browser submit/stale/replay checks at 320/768/1440 px (plus 375/414 px).
Default delay is recovered at 0.080 s; held-out q and qd RMSE improve by at least
90%. The measured default run is 0.176 s, so Job mode is unnecessary.

Acceptance gates 1–6 and 8 pass. **Gate 7 remains open:** no independent
reader feedback has been received. The [learner walkthrough](../lessons/l1/README.md#learner-acceptance-walkthrough)
is ready; do not mark this full plan complete until actual results are recorded.
Scope and parked alternatives below are unchanged; hardware validation remains
out of scope, not an outstanding L1 engineering gate.

## Goal

Make the first machine-shaped SysID lesson. A learner should be able to connect a
position command to actuator behavior and then to the motion of a loaded rigid
pendulum. The lesson should make one model-mismatch effect visible and explain
why held-out behavior matters.

The lesson question is:

> When a servo receives a position command, how does an actuator delay change the
> motion of a loaded mechanical body, and can that effect be identified from
> realistic joint observations?

## Scope

The L1 plant is a fixed base, one rotary actuator, one rigid arm, gravity, and a
known point payload. The first implementation uses an analytical deterministic
CPU model so the machine view and numerical trajectories come from the same
state arrays.

The declared boundary is:

```text
q_des + q -> fixed PD controller -> command delay -> actuator torque -> pendulum
       -> encoder position q and derived velocity qd
```

The delay is defined on the controller's torque command, after the fixed PD law
and before the pendulum plant. Controller gains, filtering, rate limits, and
sampling are fixed constants. Changing the delay location would define a
different experiment.

The public estimator receives `t`, `q_des`, `q`, and `qd`. Oracle-only signals
such as true torque and hidden delayed command state may be used for evaluation
and diagnostics, but never for fitting. The public and privileged observation
namespaces must be recorded in run metadata so an Oracle torque trace cannot be
mistaken for an estimator input.

### Effect budget

L1 introduces exactly one new hidden actuator effect: command delay. The Oracle
has a non-zero delay; the Initial Student assumes zero delay; the Identified
Student estimates delay within documented bounds. Pendulum mass, arm length,
gravity, controller gains, integration step, and sensor definition are fixed and
known for this lesson.

The following are explicitly outside this milestone: torque scale or bias,
saturation, velocity limits, Coulomb/Stribeck/asymmetric friction,
compliance, backlash, reflected motor inertia, voltage, temperature, sensor
noise, contact, payload shifts, Microduck assets, MuJoCo/MJLab backends,
hardware collection, and whole-robot fitting. These become separate effects or
later labs only when a concrete failure requires them.

Do not use `H0-H7` to name this actuator ladder; the course already uses `H` for
hardware stages. Use descriptive names or `A0/A1` in future documentation.

## Learner experience

The L1 lesson is a vertically readable course page with a guided interactive
surface. It should introduce the machine before showing metrics:

1. Why a CAD or controller model can still predict the wrong motion.
2. The physical setup: fixed base, servo axis, arm, payload, gravity, and angle.
3. The command-to-torque boundary and the delayed command path.
4. Fit data versus held-out validation data.
5. A machine playback synchronized with the selected trajectory.
6. Residual evidence that reveals the omitted delay in the Initial model.
7. A short exercise: change the initial delay assumption or excitation and
   predict what should change before running identification.
8. Limits and the bridge to friction/saturation and then a fixed-base leg.

The static lesson explains concepts and how to read evidence. The generated
report records one fixed run. The interactive app lets the learner change only
safe settings and explicitly starts fitting with a **Run identification** action.

## Data and model contract

### Oracle

The Oracle configuration contains:

- rigid-body geometry and known point payload;
- gravity and initial state;
- fixed position-servo gains;
- command delay and hidden delayed-command state;
- fit and validation excitation definitions;
- numerical timing and integration settings.

### Student roles

| Role | Delay | Mechanical parameters | Purpose |
|---|---|---|---|
| Initial model | fixed at zero | fixed to known setup | visible pre-identification baseline |
| Identified Student | fitted in public bounds | fixed to known setup | test delay recovery and prediction |
| Oracle | hidden non-zero value | true configured setup | evaluation reference |

There is no claim that the delay is a physical motor constant. It is an
effective parameter for the chosen command boundary and sampling conditions.
The report must label it accordingly.

The learner-visible Initial model is separate from the optimizer's initial
guess. The default may use the same zero-delay value, but the fitting API must
accept an independent optimizer start so later lessons can teach convergence
without changing the baseline comparison.

### Splits and conditions

- **Fit:** a position-command chirp with a fixed reset state.
- **Validation:** a separate held-out multisine or reversal trajectory with a
  different frequency/phase composition and a fixed reset state.
- The estimator sees fit observations only; validation observations and Oracle
  parameters remain outside the fitting API.
- The configuration records the seed, timestamps, command generation, reset
  state, and units.

## Visual evidence

The completed run must provide these synchronized views:

- 2D machine schematic or animation showing fixed base, servo body, joint axis,
  arm, payload, gravity arrow, current angle, and angular velocity;
- timeline scrubber that replays recorded states without re-simulating or
  refitting;
- fit and validation views side by side;
- target angle, Oracle angle, Initial angle, and Identified angle;
- angular velocity and actuator torque/command views where the signal is
  available, with Oracle-only torque clearly labeled;
- residual versus time and at least one residual-versus-command or
  residual-versus-velocity view;
- parameter-role view for shared values and the Oracle-only hidden delay;
- visible line/marker conventions that keep Oracle and Identified distinct even
  when their trajectories coincide.

Presentation controls such as split selection, camera, timeline, and signal
selection read the completed run. They must not submit a new fit.

## Implementation phases

### Wave 1: contract and numerical model

Create the frozen L1 config and an importable module under `synthetic/`.
Implement the pendulum dynamics, position-servo controller, delayed command
buffer, dataset generation, Student fitting, scoring, residual diagnostics, and
provenance. Keep the API analogous to L0 where that is genuinely useful, but do
not introduce framework base classes yet.

Deliverables:

- `synthetic/l1_servo_loaded_pendulum.py`
- `synthetic/l1_config.json`
- `notebooks/l1_servo_loaded_pendulum.ipynb`
- focused numerical and leakage tests

### Wave 2: reports and lesson

Generate the default run from the module and write the explained report and
machine-readable metrics. Add the learner-facing lesson using the existing L0
lesson structure and link it from the lesson index and course map.

Deliverables:

- `docs/lessons/l1/README.md` and ordered lesson pages;
- `notebooks/l1_servo_loaded_pendulum.ipynb` for cell-level inspection;
- `reports/l1_servo_loaded_pendulum/report.md`;
- `reports/l1_servo_loaded_pendulum/report.png`;
- `reports/l1_servo_loaded_pendulum/metrics.json`.

The report must explain the physical setup, `q_des` boundary, delay meaning,
fit/validation split, residual interpretation, and omitted effects. It is not a
replacement for the lesson narrative. It must also include a machine schematic
or representative playback frame in addition to time-series plots.

### Wave 3: guided machine surface

Add the guided interactive app using the same module and configuration. Expose
only controls that support the lesson, such as Initial delay and excitation
selection. Changing a control updates a preview or marks the run stale;
**Run identification** performs the fit and replaces the completed run.

The playback timeline and view selectors reuse the completed run. If a measured
default run takes longer than about five seconds, retain the same UI contract
and switch this lesson to Job mode with an explicit job state rather than
silently recalculating on every interaction.

Deliverables:

- `apps/l1_servo_loaded_pendulum.py`;
- browser smoke checks at narrow and desktop widths;
- no kernel-not-found or console errors on the supported path.

### Wave 4: verification and closeout

Run the numerical suite, reproduce the report in a clean CPU environment,
execute the guided app, and perform the learner acceptance walkthrough. Update
`STATUS.md` with links, commands, metrics, and any feedback. Commit the lesson
and generated artifacts only after the evidence is reproducible.

## Acceptance gates

L1 is complete only when all of these hold:

1. **Machine/state agreement:** the 2D playback geometry agrees with the
   recorded Oracle/Student angle and velocity arrays at sampled timeline points.
2. **Numerical behavior:** the delayed Oracle produces a visible phase/tracking
   mismatch for the zero-delay Initial Student; the Identified Student improves
   held-out validation by a documented threshold.
3. **Delay evidence:** the fitted delay is within a documented tolerance of the
   Oracle delay for the matched benchmark, while the report labels it effective
   and boundary-dependent.
4. **No leakage:** fitting cannot access Oracle parameters, hidden delayed state,
   validation observations, or validation metrics.
5. **Interaction semantics:** changing a fit-affecting control does not claim a
   fresh result until Run identification is pressed; timeline/camera/view
   changes do not rerun fitting.
6. **Reproduction:** a clean CPU command regenerates the report and metrics from
   the checked-in config, with deterministic outputs or documented tolerances.
7. **Learning:** an independent reader can identify the machine parts, explain
   delay, distinguish fit from validation, interpret one residual pattern,
   change one setting, and name at least three omitted real effects.
8. **Scope:** the lesson explicitly states that it is not a motor-electromagnetic
   or whole-robot simulation and does not establish hardware transfer.

## Verification commands

The implementation should provide commands in the same style as L0. The exact
module flags can be chosen during Wave 1, but the plan requires these checks:

```bash
python -m pytest -q
python -m synthetic.l1_servo_loaded_pendulum \
  --output-dir reports/l1_servo_loaded_pendulum
python -m json.tool notebooks/l1_servo_loaded_pendulum.ipynb >/dev/null
```

The guided app must be launched from the repository root with the documented
interactive requirements. Browser checks should cover 320px, 768px, and
1440px widths, one slider change, one explicit fit, timeline scrubbing, and
console cleanliness.

## Risks and mitigations

**Delay identifiability can be weak under slow excitation.** Use a fit chirp
that spans the documented servo bandwidth, retain the held-out trajectory, and
report sensitivity or a local loss slice around delay.

**Gravity and controller dynamics can obscure the actuator lesson.** Keep arm
geometry, payload, gravity, and gains known and fixed; introduce friction or
load changes in later lessons.

**A visually attractive machine view can imply unearned physical realism.** Use
an explicit “synthetic, ideal observation” label and show the model boundary and
omitted effects next to the animation.

**Interactive fitting may become slow as models grow.** Measure the default run;
keep presentation controls replay-only; promote to a cached dataset plus Job
mode when the interactive budget is exceeded.

**Shared abstractions may be premature.** Compare L0 and L1 after delivery and
extract only structures proven repeated, such as an `ExperimentRun` artifact
layout. Do not build a queue service, generic renderer, or simulator registry in
this milestone.

## Parked alternatives

- Torque scale as the first mismatch: useful, but less directly connected to
  L0's deferred delay lesson; revisit as the next actuator effect or if delay
  proves unidentifiable.
- MuJoCo or MJLab/MuJoCo Warp: revisit at L2 when multibody/contact workload or
  asset fidelity justifies it.
- 3D rendering: revisit when a 2D view cannot answer a specific learning
  question.
- Payload/load-condition matrix, friction, saturation, compliance/backlash,
  voltage/thermal effects, Microduck, hardware, and full-robot fitting: later
  lessons in the documented synthetic/hardware ladders.
- Generic framework classes, queue API, automatic model selection, and active
  experiment design: derive from repeated concrete labs rather than this plan.

## Plan decision

The user authorized the full four-wave plan above. Engineering implementation
and maintainer verification are delivered; the independent learner gate remains.
The first implementation checkpoint is Wave 1, but later waves remain part of
the same L1 scope and should not be silently dropped. The only material product
choice that may need revisiting during implementation is whether delay remains
identifiable under the frozen excitation; if not, preserve the contract and
record the evidence before selecting a replacement effect.
