# 1. Orientation: what is being identified?

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

The experiment uses an Oracle to generate observations. The Oracle knows the
truth, but the estimator does not receive it. The estimator sees only `t`,
`u`, `q`, `qd`, public parameter bounds, and a starting model.

Three names appear in every plot:

| Name | Role |
|---|---|
| Oracle | hidden teacher system that generated the observations |
| Nominal | pre-identification Student model; intentionally wrong baseline |
| Identified | Student model after fitting `J` and `b` |

Nominal is not a second truth. It answers the practical question: what happens
if we use a plausible model before calibration or SysID? Identified answers
whether the experiment gave enough information to improve it.

## Checkpoint

Before opening the plot, predict which model should be closest to the Oracle
after fitting. Then open the [report](../../../reports/l0_inertia_damping/report.md)
and check whether the parameter table agrees with your prediction.

**Answer:** the identified model should be closest because it is fitted on the
Oracle-generated observations. That expectation is a hypothesis to test on
held-out data, not proof by itself.
