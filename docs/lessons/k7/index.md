# K7 · Interpret fitted parameter values

A fitted number can improve a prediction without representing the physical quantity you hoped to measure. This lesson gives names to that distinction and shows how to test whether a parameter meaning survives a change in condition.

The result to report is sometimes a range, a parameter combination, or an effective value. That is a valid identification result when the evidence supports it.

## Two parameter sets can fit the same motion {#failure}

Suppose a Student omits a small delay. Increasing damping and changing a torque scale may compensate for part of that omission on the fitting motion. Both parameter sets can look plausible, but they answer different physical questions.

Before comparing values, predict what a compensating fit should do on a new frequency, posture, direction, or load. If its meaning is physical, the same quantity should remain interpretable when the condition changes. If it is effective, its value may move because the omitted effect moved.

## Name the parameter boundary {#boundary}

Use four labels:

| Label | Meaning | Claim it can support |
|---|---|---|
| Physical | An independently meaningful property under the declared boundary | Recovery against an independent reference, if identifiable |
| Effective | A value that improves prediction while absorbing omitted effects | Prediction within a declared operating envelope |
| Nuisance | A value needed to explain observations but not a downstream target | A better fit or correction, not a physical interpretation |
| Uncertain | A quantity whose supported range matters more than one point | Robust decisions across that range |

The label belongs to the parameter **and its boundary**. A delay estimated at the output of a fixed controller is not automatically a motor electromagnetic constant. A damping value in a model without friction may absorb resistance near the tested speeds.

## Test meanings across conditions {#comparison}

Keep the public fitting data fixed and compare a matched Student with an incomplete Student. Then evaluate both on a condition chosen before fitting:

1. fit both structures under the same objective and bounds;
2. record which parameters move together and which hit bounds;
3. evaluate a new condition where the omitted effect should matter;
4. report whether the parameter interpretation and prediction remain stable.

Independent component constraints can narrow a compensation valley, but they also change the boundary and data cost. Count that evidence as part of the route, not as free knowledge.

## Read parameter evidence {#evidence}

The parameter comparisons are conceptual until the stated conditions produce a checked record. Treat a stable label as a claim with a boundary, not as a measured fact by itself.

Use a parameter-pair loss view, fitted values across conditions, and predictions together. A stable parameter value with poor held-out behavior is not a success. A changing effective value with stable prediction may be useful, provided its range and boundary are stated.

Only parameters with shared semantics and enough information support a recovery-error claim. For unmatched Oracle/Student effects, report behavior, residuals, and operating range instead. Local optimizer curvature is not a complete uncertainty description under model mismatch.

Here is a completed L1 friction comparison, distinct from the conceptual delay example above. Both Students use the same known torque, ideal observations, fixed inertia, and fitting record. One fits viscous damping alone; the other fits damping and smooth Coulomb-like resistance.

| Model | Fitted $b$ (N m s/rad) | Fitted $\tau_c$ (N m) | Interpretation |
|---|---:|---:|---|
| Viscous-only | 0.097292 | Fixed at 0 | $b$ absorbs omitted resistance: an effective value for this boundary |
| With friction | 0.055000 | 0.060000 | Recovers the reference values in this matched, noise-free synthetic case |

![Parameter compensation and held-out residuals in L1 friction](../../../reports/l1_friction/report.png)

Read resistance versus velocity first, then the held-out residual: changing the viscous slope cannot reproduce the curved resistance relation. The values and figure come from the [frozen report](../../../reports/l1_friction/report.md). They support compensation for omitted friction. This run did not refit at each speed, so it does not measure a law for how fitted $b$ changes with speed.

## Think it through {#exercise}

A friction-free Student fits a low-speed run by increasing damping. On a higher-speed reversal, its residual becomes directional and the fitted damping changes. How should the original damping value be reported, and what experiment would reduce the ambiguity?

<details markdown="1">
<summary>Read a suggested answer</summary>

Report the damping as an effective value for the low-speed, friction-free boundary, not as an independently recovered physical damping coefficient. Add bidirectional speeds that expose the missing resistance, or measure an independent torque/resistance signal if that belongs to the intended boundary. If the richer model is selected using the same evaluation run, reserve another final run.
</details>

The common wrong turn is to attach a physical name to a value before checking its boundary. If you cannot classify it, compare the value and the prediction across a new condition, then report a combination or range. Continue when the label states the evidence and the limit.

## What parameter labels cannot prove {#limits}

Calling a value “physical” does not make it identifiable. Calling it “effective” does not make it useless. The claim must name the boundary, data, conditions, and independent evidence behind the label.

L2 applies these ideas to actuator and rigid-body compensation in a coupled leg. Continue to [L2 · Separate actuator and body errors in a fixed-base leg](../l2/index.md).
