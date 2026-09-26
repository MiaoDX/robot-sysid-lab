# 1. Meet the machine and the question

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

The physical teaching setup has a fixed base, one rotary servo axis, a rigid
arm of known length, a known point payload at its end, and gravity. The arm
angle `q` is measured from the downward vertical in radians; positive velocity
`qd` follows the positive rotation direction shown in the machine schematic.
The geometry and trajectory playback use the same recorded state array, so a
frame at timeline index `i` uses exactly `q[i]` and `qd[i]` from the selected
run.

The plant is intentionally analytical. Its gravity term is

$$
I\ddot q = \tau - g\ell\left(\frac{m_a}{2}+m_p\right)\sin q,
\qquad I = \frac{m_a\ell^2}{3}+m_p\ell^2,
$$

where `m_a` is the uniform arm mass, `m_p` is the point payload mass, and `ell`
is the arm length. The arm contributes distributed inertia and a gravity load
at its midpoint; the payload contributes at the tip. These values and the PD
law are fixed and known. Only the effective delay is hidden from the Student.

| Role | What it means in the experiment |
| --- | --- |
| Oracle | Uses the configured non-zero command delay to generate observations. |
| Initial model | Uses the visible zero-delay assumption before identification. |
| Identified Student | Fits delay from public fit observations within stated bounds. |

The Oracle's true torque and delayed-command state may appear in diagnostics,
but they are privileged signals. The fitting API receives `t`, `q_des`, `q`,
and `qd` only.

## Checkpoint

Before opening the report, predict where the zero-delay Initial curve should
first depart from the Oracle: immediately at a command transition, or only
after the delayed phase accumulates. Then inspect the machine frame and the fit
plot. The answer is a timing-dependent phase difference, with its visible size
depending on the excitation frequency; it is not evidence of a changed arm
mass.
