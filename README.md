# robot-sysid-lab

A practical, layered introduction to robot system identification: from synthetic 1-DoF plants and real actuator benches to articulated limbs, whole robots, and humanoid sim-to-real.

The project has two goals:

1. **Teach SysID clearly to robot algorithm engineers** working on RL, WBC, simulation, planning, or control.
2. **Build reusable engineering patterns** for actuator characterization, model selection, simulator matching, validation, and humanoid migration.

## Core idea

System identification is not just parameter optimization. A useful workflow separates:

```text
Plant -> Experiment -> Model Class -> Parameter Estimation -> Validation
```

A low training error does not prove that the recovered parameters are physically correct, or even that the chosen model structure is adequate. This repository therefore emphasizes model structure, excitation, identifiability, held-out validation, residual analysis, and the distinction between physical parameters and effective simulator parameters.

## Learning ladder

```text
1-DoF analytical plant
  -> single actuator
  -> multi-joint fixed-base limb
  -> limb + contact
  -> whole synthetic Microduck
  -> small humanoid / Microban
  -> real servo bench
  -> real small robot
  -> full humanoid
```

## Planned tracks

- **SysID 101**: concepts, vocabulary, and short references.
- **Synthetic sandbox**: teacher/student plants with known hidden ground truth.
- **BAM / Microduck labs**: real actuator identification and sim-to-real examples.
- **Generic actuator framework**: abstractions that extend from smart servos to torque-controlled PMSM humanoid joints.
- **Whole-robot matching**: PACE-style and MuJoCo-native system identification.

Start with [docs/00_overview.md](docs/00_overview.md).

## License

MIT. See [LICENSE](LICENSE).
