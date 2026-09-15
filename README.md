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
| [Start the L0 lesson set](docs/lessons/l0/README.md) | [Project overview](docs/00_overview.md) |
| [Learn the fundamentals](docs/01_sysid_101.md) | [Learning and lab roadmap](docs/03_synthetic_lab_roadmap.md) |
| [Design Oracle experiments](docs/04_oracle_sim_experiment_design.md) | [Benchmark contract](docs/07_benchmark_contract.md) |
| [Understand the visual reports](docs/05_visualization_and_reporting.md) | [Lesson / Experiment Pipeline](docs/lesson_pipeline.md) |

The first guided course is the [interactive L0 Marimo app](apps/l0_inertia_damping.py),
a continuous lesson from motivation through experiment evidence and limits,
introduced by the [L0 lesson set](docs/lessons/l0/README.md). The
[Jupyter notebook](notebooks/l0_inertia_damping.ipynb) remains available for
cell-by-cell inspection.
Its headless equivalent is `python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping`.
The generated [L0 report](reports/l0_inertia_damping/report.md) is available without running a notebook.

[Project status and next steps](STATUS.md)

## License

[MIT](LICENSE).
