# Learning Path and References

This project is not intended to turn every robot algorithm engineer into a SysID specialist. The goal is a short common language plus hands-on experiments.

## Suggested internal learning sequence

### Part A — Dynamics and feedback intuition

Learn enough to reason about second-order systems, damping, resonance, bandwidth, delay, and frequency response.

Recommended:

- Åström & Murray, **Feedback Systems** — https://fbsbook.org/
- MIT OpenCourseWare, **Engineering Dynamics** — https://ocw.mit.edu/

Focus on:

- mass-spring-damper dynamics,
- transfer functions,
- Bode/frequency response,
- poles and damping,
- feedback stability and bandwidth.

### Part B — System identification concepts

Recommended:

- MIT 2.160, **Identification, Estimation and Learning** — search via MIT OpenCourseWare.
- Ljung, **System Identification: Theory for the User** as an optional deeper reference.

Focus on:

- experiment design,
- persistent excitation,
- model structure,
- least squares and prediction-error thinking,
- identifiability,
- validation and residuals.

### Part C — Robot-specific hands-on material

Primary project references:

- BAM (Better Actuator Models): https://github.com/rhoban/bam
- PACE sim-to-real: https://github.com/leggedrobotics/pace-sim2real
- Microduck RL: search the Pollen Robotics / Hugging Face Microduck repositories
- mjlab: https://github.com/mujocolab/mjlab
- MuJoCo: https://github.com/google-deepmind/mujoco

Advanced references:

- SPI-Active for active excitation / information-driven SysID
- Pinocchio for rigid-body dynamics regressors
- FIGAROH for robot dynamics identification and calibration workflows

## What people should know after SysID 101

Participants should be able to answer:

1. What is the plant boundary?
2. What is the model class?
3. Which quantities are parameters and which are hidden states?
4. Why is this excitation informative?
5. Can two parameter sets explain the same data?
6. Is the fitted parameter physically meaningful or merely an effective simulator value?
7. Does the model predict held-out trajectories?
8. What pattern remains in the residual?
9. Is the next step more optimization or a richer model structure?
10. How does the identified reference model connect to domain randomization and RL?

## Course tracks

The [rendered course map](course/index.html) is the canonical overview. Its
prefixes separate three kinds of progression:

| Track | Range | Purpose |
|---|---|---|
| Knowledge | `K0-K8` | concepts from motivation through sim-to-real |
| Synthetic labs | `L0-L6` | controlled experiments from one joint through cross-simulator mismatch |
| Hardware transfer | `H0-H2` | actuator bench, small robot, then full humanoid |

`L0` therefore means **Lab 0**, not the first item in one mixed nine-step
ladder. The progression inside each track is intentional: each stage introduces
only one or two new classes of uncertainty. Knowledge and labs can advance
together; hardware stages begin when their prerequisite experiment and safety
contracts are ready.
