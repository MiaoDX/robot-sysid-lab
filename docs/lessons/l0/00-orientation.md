# L0 · Orientation: what is being identified?

System identification (SysID) means learning a useful model of a system from
experiments. In this lesson the system is one rotational degree of freedom.
The model boundary is intentionally explicit:

```text
known applied torque u  ->  rotational plant  ->  observed q and qd
```

The plant follows

$$
J\ddot{q} + b\dot{q} = u
$$

Here $q$ is position in radians, $\dot{q}$ is velocity in radians per second,
$\ddot{q}$ is acceleration, $u$ is applied torque in N m, $J$ is inertia in
kg m^2, and $b$ is viscous damping in N m s/rad. The unknowns are only $J$
and $b$. In code these signals are named `q`, `qd`, and `qdd`.

A simulator with known parameters generates the observations. The estimator
receives time, torque, position, and velocity, together with parameter bounds
and an initial guess chosen beforehand. The true parameters are used later
to check the result.

Three names appear in every plot:

| Name | Role |
|---|---|
| True system (Oracle) | system that generated the observations |
| Initial model | plausible but intentionally wrong model available before identification |
| Identified model | model after fitting `J` and `b` |

Comparing the initial and identified models shows how fitting changes the
prediction. We then test a motion withheld from fitting to see whether the
improvement carries over to new data.

## Checkpoint

Before opening the plot, predict which model should be closest to the Oracle
after fitting. Then open the [report](../../../reports/l0_inertia_damping/report.md)
and check whether the parameter table agrees with your prediction.

**Answer:** the identified model should be closest because it is fitted on the
Oracle-generated observations. That expectation is a hypothesis to test on
held-out data, not proof by itself.
