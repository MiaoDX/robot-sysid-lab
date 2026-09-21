# robot-sysid-lab

**Learn robot system identification by seeing it work.**

A simulation-first learning and research lab for robotics engineers working on RL, whole-body control, simulation, and planning.

**Knowledge** builds intuition through explanations, visual examples, and experiments. **Synthetic labs** use a configurable Oracle as ground truth to study what Student models can recover and predict.

## Architecture

![Knowledge guides experiments; an Oracle generates declared observations, an Initial model is fitted on training data, and held-out validation produces visual explanations. Privileged truth goes only to evaluation. The same method scales from 1-DoF to Microduck and Microban.](docs/assets/architecture.svg)

The Oracle knows its full state and parameters; the estimator receives only the declared observations. Parameter recovery, held-out prediction, and control/RL transfer are distinct questions—not a single score.

## Start the course

Open the [course homepage](docs/course/index.html), then follow
[K0: why identification matters](docs/lessons/k0/index.html) →
[K1: the fundamentals](docs/lessons/k1/index.html) →
[L0: inertia and damping](docs/lessons/l0/index.html).
Each lesson is a continuous reading page with examples and exercises.
[L1: command delay](docs/lessons/l1/index.html) continues the experimental path.
Future lessons appear in the course directory with their availability marked.

The website is available in [English](docs/course/index.html) and
[中文](docs/course/index.zh-CN.html). Use the language switch at the top right
to keep reading the same page in the other language. Lesson notes, report
explanations, and the curriculum design are rendered as bilingual web pages;
teaching clips include both subtitle languages. See the [website authoring guide](docs/site/README.md)
for rebuilding the pages after an edit.

To review the HTML and interactive lesson over a LAN, run these commands from
the repository root in separate terminals:

```bash
python -m pip install -r requirements-interactive.txt
python -m http.server 2720 --bind 0.0.0.0
python -m marimo run apps/l0_inertia_damping.py --host 0.0.0.0 --port 2718
python -m marimo run apps/l1_servo_loaded_pendulum.py --host 0.0.0.0 --port 2719
```

## Explore the source

| Start here | Go deeper |
|---|---|
| [Course overview](docs/course/index.html) | [Project overview](docs/00_overview.md) |
| [Learn the fundamentals](docs/01_sysid_101.md) | [Learning and lab roadmap](docs/03_synthetic_lab_roadmap.md) |
| [Design Oracle experiments](docs/04_oracle_sim_experiment_design.md) | [Benchmark contract](docs/07_benchmark_contract.md) |
| [Understand the visual reports](docs/05_visualization_and_reporting.md) | [Lesson / Experiment Pipeline](docs/lesson_pipeline.md) |

The first guided course is the [interactive L0 Marimo app](apps/l0_inertia_damping.py),
a continuous lesson from motivation through experiment evidence and limits,
introduced by the [L0 lesson set](docs/lessons/l0/README.md). The
next guided lab is the [interactive L1 servo-loaded-pendulum app](apps/l1_servo_loaded_pendulum.py),
introduced by the [L1 lesson set](docs/lessons/l1/README.md). The static lesson
pages and teaching videos are the primary learning path; Marimo is the bounded
interactive adapter, and longer or heavier experiments should use the local
CPU/GPU commands documented with each lesson. See the [lesson delivery policy](docs/lesson_delivery_policy.md)
for the split used by future levels. The
[Jupyter notebook](notebooks/l0_inertia_damping.ipynb) remains available for
cell-by-cell inspection.
Its headless equivalent is `python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping`.
The generated [L0 report](reports/l0_inertia_damping/report.md) is available without running a notebook.

[Project status and next steps](STATUS.md)

## License

[MIT](LICENSE).
