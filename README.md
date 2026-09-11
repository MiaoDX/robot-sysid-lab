# robot-sysid-lab

A practical robot system-identification learning and research lab for algorithm engineers working on RL, WBC, simulation, planning, and control.

The project has two first-class tracks:

1. **Knowledge track** — build a shared SysID vocabulary and engineering methodology for the robotics team.
2. **Synthetic lab track** — construct increasingly realistic simulated teacher systems with known ground truth, hide that truth from the identification pipeline, and study what can and cannot be recovered from observations and experiments.

The synthetic track is not only a warm-up for hardware. It is a long-term benchmark environment where we can inspect every latent quantity, generate arbitrary motions and operating conditions, deliberately introduce model mismatch, and compare identification strategies under controlled ground truth.

## Core methodology

```text
Build synthetic truth
  -> hide the truth
  -> design experiments
  -> collect observations
  -> choose a student model
  -> estimate parameters
  -> diagnose residuals
  -> validate on held-out conditions
  -> increase model/system complexity
```

System identification is not just parameter optimization. A low training error does not prove that the recovered parameters are physically correct, identifiable, or predictive outside the fitting trajectory.

The repository therefore emphasizes:

- experiment design and excitation,
- model structure before optimizer choice,
- practical identifiability and parameter compensation,
- held-out validation and residual analysis,
- physical versus effective simulator parameters,
- and hierarchical scaling from components to whole robots.

## Synthetic learning ladder

```text
1-DoF analytical system
  -> synthetic actuator
  -> fixed-base articulated leg
  -> leg + contact
  -> whole Microduck
  -> Microban small humanoid
  -> sim-to-sim mismatch
  -> later: real hardware validation
```

For each level, the teacher can be deliberately richer than the student. This avoids the inverse crime and lets the lab expose model mismatch, unobservable parameters, insufficient excitation, optimizer failure, and compensating parameter solutions.

## Knowledge topics

The accompanying team-learning material covers:

- SysID fundamentals and vocabulary,
- robot dynamics for identification,
- actuator and friction modeling,
- experiment design and identifiability,
- estimation and optimizer behavior,
- validation and residual diagnostics,
- physical versus effective parameters,
- and the connection from identified models to sim-to-real and domain randomization.

## Planned lab families

- **1-DoF concepts** — inertia, damping, friction, delay, saturation, excitation, and observability.
- **Actuator lab** — BAM-style model families, rich friction, delay, saturation, backlash/compliance, and sensor availability.
- **Fixed-base leg** — coupling, gravity, actuator/body compensation, and rigid-body parameter identifiability.
- **Contact leg** — contact friction, compliance, geometry, and diagnostic separation from actuator errors.
- **Microduck** — component-first identification versus PACE-style whole-robot residual matching.
- **Microban** — small-humanoid scaling, actuator-family parameter sharing, hierarchy, and high-dimensional identifiability.
- **Cross-simulator studies** — teacher and student using different model structures or numerical implementations.

## Supporting abstractions

Reusable software abstractions are still useful, but they support the labs rather than define the project:

```text
Plant
Dataset
Model
ParameterSchema
Excitation
SimulatorBackend
Loss
Estimator
Validation
Report
```

BAM, PACE, MuJoCo, MJLab, CMA-ES, least squares, and differentiable methods are examples of models, backends, workflows, or estimators that can plug into this structure; none of them is the framework itself.

Start with [docs/00_overview.md](docs/00_overview.md) and the [synthetic lab roadmap](docs/03_synthetic_lab_roadmap.md).

## License

MIT. See [LICENSE](LICENSE).
