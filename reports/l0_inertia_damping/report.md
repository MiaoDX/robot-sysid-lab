# L0 inertia and damping identification

This is the result of the first lesson in the [L0 lesson](../../docs/lessons/l0/index.md).
The lesson asks a small question: can we use observed motion to estimate the
inertia and viscous damping of a one-degree-of-freedom plant?

## How to read this report

The plant follows `J*qdd + b*qd = u`. `u` is the applied torque, `q` is
position, and `qd` is velocity. **True system (Oracle)** is the hidden teacher
that generated the observations. **Initial model** is the plausible but
deliberately wrong model available before identification. **Identified model**
is the result after fitting `J` and `b` on the fit trajectory. The Initial
model is a baseline for seeing why identification is needed; it is not another
ground-truth system. The machine-readable configuration retains the key
`nominal` for compatibility.

The fit trajectory is used by the estimator. The validation trajectory uses a
different multisine input and is kept untouched until after fitting. Improvement
on validation is the useful evidence that the fitted model learned dynamics
rather than only matching one motion.

A **chirp** is one sinusoid whose frequency sweeps from low to high. A
**multisine** adds several fixed-frequency sinusoids. **Held-out** means that
the multisine observations are not used to estimate `J` or `b`; they are used
only after fitting to test prediction on a different motion.

Configuration: `l0-inertia-damping-v1`<br>
Plant boundary: known applied torque `u` in N m -> observed `q`, `qd`<br>
Fit excitation: chirp<br>
Validation excitation: held-out multisine

![True-system, Initial-model, and Identified-model trajectories](report.png)

**Curve key:** True system (Oracle) is the solid dark line. Identified model is
the blue dashed line with open markers. When they overlap, the markers still
show that both curves are present; the overlap is evidence of a successful
match. Initial model is orange.

| quantity | True system | Initial model | Identified model |
|---|---:|---:|---:|
| inertia `J` (kg m^2) | 0.06500000 | 0.09500000 | 0.06500000 |
| damping `b` (N m s/rad) | 0.05500000 | 0.01800000 | 0.05500000 |

| split/model | q MAE (rad) | qd MAE (rad/s) |
|---|---:|---:|
| fit / Initial model | 4.3107227 | 1.4136074 |
| fit / Identified model | 1.5607874e-14 | 1.2252942e-14 |
| validation / Initial model | 2.7396426 | 0.87716149 |
| validation / Identified model | 1.8251542e-14 | 2.0286828e-14 |

## What this result does and does not show

The identified parameters recover this matched analytical teacher and predict
the held-out excitation. This is a controlled first success, not a claim that
a real servo can be represented by these two terms. The experiment omits
torque calibration and controller dynamics, delay, saturation, friction beyond
viscous damping, compliance, contact, and sensor noise. The [lesson notes](../../docs/lessons/l0/03-assumptions-and-next-step.md)
explain how those omissions shape the next experiment.

## Try it

Read the [L0 lessons](../../docs/lessons/l0/index.md), then change one Initial-
model value in the [interactive Marimo lesson](../../apps/l0_inertia_damping.py).
The orange preview changes immediately; press **Run identification** to refresh
the blue result. A successful fit should still recover the Oracle parameters.
Regenerate this report headlessly with:

```bash
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
```

The estimator saw only fitting `t`, `u`, `q`, and `qd`, plus public bounds and
the non-truth nominal initialization. Oracle parameters are shown only in this
evaluation report. This matched, ideal-observation example demonstrates
recovery and held-out prediction; it does not establish model-mismatch or
real-robot transfer.
