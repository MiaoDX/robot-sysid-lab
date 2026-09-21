# L0 · From physics to data: why inertia and damping matter

The equation has two competing effects:

- Larger `J` resists changes in velocity. The same torque produces less
  acceleration.
- Larger `b` removes more energy when the joint is moving. Velocity decays
  faster when the applied torque is small or zero.

The fit input is a chirp: its frequency changes over time. This gives the
experiment both slower and faster motion, which helps separate an acceleration
effect (`J`) from a velocity-dependent effect (`b`). The validation input is a
different multisine, so it tests the fitted model under a motion it did not see
during fitting.

Open the [static figure](../../../reports/l0_inertia_damping/report.png) or run
the [notebook](../../../notebooks/l0_inertia_damping.ipynb). Read the four
trajectory panels from left to right:

1. fit position and validation position;
2. fit velocity and validation velocity.

The black True-system curve is the observation target. The orange Initial-model
curve is the uncalibrated baseline. The blue Identified-model curve is the
fitted result.
Look for acceleration differences in the velocity panels and accumulated
position differences in the position panels. A small residual means the
identified model reproduces that observed quantity for that experiment.

## Try one change

In the Marimo lesson, change Initial-model damping while leaving the truth and
input unchanged. The orange curve changes immediately; the blue result stays
fixed and is marked stale. Press **Run identification** to fit again from the
new starting values. A successful fit should still converge to the same Oracle
values.

Compare the new starting prediction with the completed fit, then check
validation. This shows both how the starting guess changes the initial error
and whether fitting still reaches a useful result.

## Checkpoint

Which observation would be most directly affected by increasing inertia: the
instantaneous acceleration or the sign of the applied torque? The answer is
acceleration. A parameter is useful only when the experiment makes its effect
observable in the data.
