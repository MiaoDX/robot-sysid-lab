# L1-S · Make torque saturation visible

A gentle experiment cannot reveal an output limit it never reaches. This elective lesson uses that simple fact to distinguish “the fit did not need a limit” from “the limit was measured.”

This page defines a bounded experiment contract. The numerical runner and report are not implemented yet, so the examples below are reasoning exercises rather than measured results.

## A successful fit can leave the limit unknown {#failure}

Suppose a command stays below the true torque limit. A Student with no saturation and a Student with a very large saturation threshold can produce the same motion. More optimization time cannot choose among equivalent thresholds.

Predict what changes when the command crosses the limit. The applied torque should stop following the command while the command itself continues to grow.

## Declare the saturation boundary {#boundary}

The isolated boundary is

```text
torque command → symmetric saturation → known rotational dynamics → motion
```

Mechanical parameters and torque scale remain fixed. The Student sees the command and declared motion observations. Actual applied torque is an Oracle diagnostic, not a fitting input. Delay and extra friction are excluded so that the new effect is output saturation.

The parameter `tau_max` is recoverable only to the extent that the data cross and identify the threshold. Otherwise the honest result may be a lower bound.

## Compare below-threshold and threshold-crossing data {#comparison}

Use two fitting conditions with the same duration and declared noise:

| Dataset | What it can support |
|---|---|
| Commands never reach the limit | Behavior below the limit; no unique upper threshold |
| Commands cross the limit | Threshold-related behavior, if the crossing is observable |

Compare unlimited and limited Students on both datasets, then use a predeclared held-out amplitude family. Keep the model choice and amplitude range fixed before reading the final score.

## Read saturation evidence {#evidence}

The planned figures are command and applied-torque traces, saturation fraction, loss versus `tau_max`, prediction error by amplitude, and residuals around the clipped region. A flat loss above a range of large thresholds is evidence that the current data only constrain a lower bound.

Do not report the Oracle applied torque as if it were a signal available to the fitter. It explains the diagnostic plot and verifies the generator, while the Student must infer the effect from its declared observations.

## Think it through {#exercise}

Dataset A uses small commands and gives identical predictions for every threshold above 2 Nm. Dataset B crosses an apparent clip near 1 Nm and predicts a held-out large command differently under unlimited and limited models. Which dataset supports a saturation claim, and what must still be checked?

<details markdown="1">
<summary>Read a suggested answer</summary>

Dataset B supports a saturation hypothesis because it contains behavior that separates the candidate models. Check that the apparent clip is not a controller or numerical artifact, that the held-out amplitude was declared before selection, and that the fitted threshold remains supported across seeds and relevant motion conditions. Dataset A supports only a statement that the limit was not reached.
</details>

The common wrong turn is to report a unique threshold without a crossing. If you cannot decide, inspect the command range and the loss plateau, then design a declared amplitude family that crosses the candidate limit. Continue when the result can be stated as a threshold or a lower bound.

## What this experiment cannot prove {#limits}

A constant symmetric limit is a teaching boundary, not a complete actuator model. Speed-, voltage-, temperature-, direction-, and load-dependent limits remain separate questions. If no command reaches the limit, report a range or lower bound rather than a unique parameter.

Return to [L1-O observation quality](../l1-o/index.md) or continue to [K7 · Interpret fitted parameter values](../course-design.md#k7). L1-S is elective and is not required before L2.
