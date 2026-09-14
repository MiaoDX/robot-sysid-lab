# L0 inertia and damping identification

Configuration: `l0-inertia-damping-v1`<br>
Plant boundary: known applied torque `u` in N m -> observed `q`, `qd`<br>
Fit excitation: chirp<br>
Validation excitation: held-out multisine

![Oracle, nominal, and identified trajectories](report.png)

| quantity | Oracle | Nominal | Identified |
|---|---:|---:|---:|
| inertia `J` (kg m^2) | 0.06500000 | 0.09500000 | 0.06500000 |
| damping `b` (N m s/rad) | 0.05500000 | 0.01800000 | 0.05500000 |

| split/model | q MAE (rad) | qd MAE (rad/s) |
|---|---:|---:|
| fit / nominal | 4.3107227 | 1.4136074 |
| fit / identified | 1.5607874e-14 | 1.2252942e-14 |
| validation / nominal | 2.7396426 | 0.87716149 |
| validation / identified | 1.8251542e-14 | 2.0286828e-14 |

The estimator saw only fitting `t`, `u`, `q`, and `qd`, plus public bounds and
the non-truth nominal initialization. Oracle parameters are shown only in this
evaluation report. This matched, ideal-observation example demonstrates
recovery and held-out prediction; it does not establish model-mismatch or
real-robot transfer.
