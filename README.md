# robot-sysid-lab

**Learn robot system identification by seeing it work.**

A simulation-first learning and research lab for robotics engineers working on RL, whole-body control, simulation, and planning.

**Knowledge** builds intuition through explanations, visual examples, and experiments. **Synthetic labs** use a configurable Oracle as ground truth to study what Student models can recover and predict.

## Architecture

![Two connected tracks: knowledge guides experiments; an Oracle generates declared observations, a Student is fitted on training data, and held-out validation produces visual explanations. Privileged truth goes only to evaluation. The same method scales from 1-DoF to Microduck and Microban.](docs/assets/architecture.svg)

The Oracle knows its full state and parameters; the estimator receives only the declared observations. Parameter recovery, held-out prediction, and control/RL transfer are distinct questions—not a single score.

## Explore

| Start here | Go deeper |
|---|---|
| [Learn the fundamentals](docs/01_sysid_101.md) | [Project overview](docs/00_overview.md) |
| [Follow the first lab](docs/08_happy_path_and_identifiability.md) | [Learning and lab roadmap](docs/03_synthetic_lab_roadmap.md) |
| [Design Oracle experiments](docs/04_oracle_sim_experiment_design.md) | [Benchmark contract](docs/07_benchmark_contract.md) |
| [Understand the visual reports](docs/05_visualization_and_reporting.md) | [Learning experience](docs/06_learning_experience.md) |

[Project status and next steps](STATUS.md)

## License

[MIT](LICENSE).
