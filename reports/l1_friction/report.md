# L1 friction extension: viscous damping versus smooth Coulomb-like resistance

This frozen CPU run compares a viscous-only Student with a Student that can
represent smooth Coulomb-like resistance. The known-inertia plant is
`J*qdd + b*qd + tau_c*tanh(qd/v_eps) = u`; delay, gravity, saturation and
measurement noise are absent by design.

![Fit, validation, resistance and reversal residuals](report.png)

## Boundary and observations

The Oracle uses `b=0.055` and `tau_c=0.06` with
fixed `J=0.065` and `v_eps=0.04`. The estimator sees
only `t`, applied torque `u`, position `q`, and velocity `qd`. Oracle parameters,
the resistance decomposition, and held-out observations stay outside the fit API.

## Results

The viscous-only fit returned `b=0.097292`. The friction fit returned
`b=0.055000`, `tau_c=0.060000`.
Held-out q RMSE ratio (friction / viscous) is `1.177e-18` and qd RMSE ratio is
`2.673e-17`. The held-out reversal-window q RMSE ratio is `1.217e-19`.
The local fit sensitivity condition number is `15.24`.

## Interpretation and limits

The omitted friction term produces structured residuals around changes of
velocity. A velocity-correlated residual is evidence for a missing effect, not
proof that the effect is friction: delay, filtering, or an incorrect torque
boundary can create similar patterns. This lesson uses smooth `tanh` friction;
it does not establish static sticking, Stribeck behavior, backlash, asymmetric
friction, sensor noise, or hardware transfer.

Thresholds were frozen after the pilot: both validation error ratios must be
at most `0.25`, reversal ratio at most
`0.4`, and parameter recovery is reported within
`0.002` only when sensitivity supports it.
