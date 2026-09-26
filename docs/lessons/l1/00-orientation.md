# L1 · Meet the machine and the question

System identification asks whether a model learned from one controlled
experiment can predict observations from another. L1 uses a small machine so
the boundary stays visible:

```text
position command q_des
        -> fixed PD controller
        -> command delay
        -> actuator torque
        -> loaded pendulum under gravity
        -> encoder position q and derived velocity qd
```

The simulated setup has a fixed base, one rotary servo axis, a rigid arm of
known length, a known point payload, and gravity. Angle `q` is measured from
the downward vertical in radians. Positive velocity follows increasing angle.

The plant is intentionally analytical. Its gravity term is

$$
I\ddot q = \tau - g\ell\left(\frac{m_a}{2}+m_p\right)\sin q,
\qquad I = \frac{m_a\ell^2}{3}+m_p\ell^2,
$$

where `m_a` is the uniform arm mass, `m_p` is the point payload mass, and `ell`
is the arm length. The arm contributes distributed inertia and a gravity load
at its midpoint; the payload contributes at the tip. These values and the PD
law are fixed and known. Only the effective delay needs to be estimated.

| Role | What it means in the experiment |
| --- | --- |
| Oracle | Uses the configured non-zero command delay to generate observations. |
| Initial model | Uses the visible zero-delay assumption before identification. |
| Identified Student | Estimates delay from the fitting observations within the chosen bounds. |

Torque and delayed-command traces help explain the motion in diagnostic
figures. Fitting uses time, target position, recorded position, and derived
velocity, named `t`, `q_des`, `q`, and `qd` in code.

## Checkpoint

Before opening the report, predict where the zero-delay Initial curve should
first depart from the Oracle: immediately at a command transition, or only
after the delayed phase accumulates. Then inspect the machine frame and the fit
plot. The answer is a timing-dependent phase difference, with its visible size
depending on the excitation frequency; it is not evidence of a changed arm
mass.
