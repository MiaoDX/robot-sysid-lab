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
10. How does the identified nominal model connect to domain randomization and RL?

## Practical ladder

| Level | System | Main lesson |
|---|---|---|
| 0 | analytical 1-DoF | dynamics, parameter sensitivity |
| 1 | synthetic actuator | friction, delay, saturation, model mismatch |
| 2 | fixed-base articulated leg | coupling, gravity, rigid-body vs actuator parameters |
| 3 | leg + contact | contact model and environment uncertainty |
| 4 | synthetic Microduck | whole-robot trajectory matching |
| 5 | synthetic small humanoid | high-dimensional identifiability and hierarchy |
| 6 | real actuator bench | unknown unknowns and measurement reality |
| 7 | real Microduck/Microban | complete sim-to-real loop |
| 8 | full humanoid | scalable engineering pipeline |

The progression is intentional: each level introduces only one or two new classes of uncertainty.
