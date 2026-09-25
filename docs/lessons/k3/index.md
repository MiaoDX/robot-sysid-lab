# K3 · Trace commands to joint torque

A command is not automatically a torque measurement. Controllers, timing, friction, and output limits can all change what the joint receives. This lesson gives you a boundary for reasoning about those effects one at a time.

The key question is not “which actuator model is richest?” It is “which hidden effect does the current evidence require us to add?”

## A correct command can produce a wrong motion {#failure}

Suppose the desired position follows a clean sweep, but the joint lags at high frequency and leaves a directional error near reversals. Increasing a rigid-body inertia may reduce one plot's error while hiding the command-to-torque problem.

Predict how three isolated effects would look: a fixed command delay, a resisting torque that changes with speed direction, and a symmetric torque limit. Their signatures overlap in closed-loop motion, so the experiment must change the condition that each effect responds to.

## Define the command-to-torque boundary {#boundary}

A simple controller can be written as

$$
\tau_\text{cmd} = K_p(q_\text{des}-q) + K_d(\dot q_\text{des}-\dot q).
$$

The plant boundary may then include a delay, saturation, and resistance before the mechanical dynamics:

```text
q_des → fixed controller → command delay → saturation/friction → joint dynamics → q, q̇
```

The lesson must declare which signal enters the Student. A command-only Student cannot use the Oracle's actual applied torque to explain its own result. If applied torque is measured and part of the intended boundary, say so explicitly.

## Isolate one actuator effect at a time {#comparison}

Use the same controller and mechanical parameters while changing one hidden effect:

| Isolated effect | Condition that exposes it | First comparison |
|---|---|---|
| Delay | frequency and command timing | sweep versus reversal, with command history reset |
| Friction | speed direction and reversal rate | low/high speed, forward/reverse |
| Saturation | command amplitude | below and above the limit |

Do not add delay, friction, and saturation to one Student before the single-effect cases are understood. A richer model can reduce fitting error by absorbing a different missing effect.

## Read actuator evidence {#evidence}

The comparison below is a conceptual contract. Any applied-torque or internal-state trace is an Oracle diagnostic unless the page explicitly declares it as an observation.

Use a boundary diagram, a signal timeline, and condition-specific residuals together. A phase shift is a clue for delay, not a direct measurement of motor electromagnetic time. A reversal-localized residual is a clue for resistance, not proof that friction is the only missing effect. A flat response at large commands suggests saturation only if the command actually crosses the limit.

Mark Oracle-only signals such as actual applied torque and internal delay state. They can explain why a trace looks the way it does, but they must not leak into a command-only fit.

## Think it through {#exercise}

A command sweep has a phase-like error at high frequency. A low-speed reversal has a sign-dependent error. A large-amplitude command produces a clipped applied torque in the Oracle diagnostic plot. Which isolated experiment would you use for each hypothesis, and which signal must remain hidden from the fitter?

<details markdown="1">
<summary>Read a suggested answer</summary>

Use a frequency comparison with a declared command history for delay, bidirectional low/high-speed motions for friction, and below/above-threshold amplitudes for saturation. Keep actual applied torque and internal actuator states hidden when the Student is meant to infer effects from commands and motion. Those signals can appear in an explanation or evaluator-only plot.
</details>

The common wrong turn is to use the Oracle's applied torque to explain a command-only fit. If you cannot choose an experiment, hold the controller fixed and change only frequency, direction, or amplitude. Continue when each hypothesis has one condition that could make it disagree with the others.

## What the command boundary cannot prove {#limits}

An effective command delay depends on where the boundary is drawn; it is not automatically an electromagnetic motor constant. A smooth resistance term is not a full friction law, and a fitted limit may be only a lower bound when the data never cross it.

K7 will explain why these fitted values can be physical, effective, nuisance, or uncertain. L1 applies the isolated delay and friction cases; L1-O adds observation quality, while L1-S is an elective saturation case.

Continue to [L1 · Actuator delay and friction](../l1/index.md).
