# L5 · Share parameters across Microban joints

A larger robot makes parameter freedom expensive. This lesson asks whether every joint should have its own values, whether actuator families can share them, and how to detect a joint-specific exception without using final evaluation to choose the grouping.

The lesson studies scale and parameterization. It does not add a catalog of new friction, compliance, or thermal effects.

## More parameters can predict worse {#failure}

An independent fit can reduce training loss by following noise or motion-specific ambiguity. A shared fit can improve stability but hide a real joint difference. Neither parameter count is automatically correct.

Predict what should happen when one joint in an otherwise similar actuator family has a controlled deviation.

## Declare the Microban parameter boundary {#boundary}

Use a fixed Microban Oracle, the primary backend from the preceding whole-robot work, and one observation protocol:

```text
whole-body commands → actuator/body Student → joint and body observations
```

Compare three parameterizations:

1. independent parameters for every joint;
2. actuator-family shared parameters plus bounded joint residuals;
3. a compact whole-robot effective parameterization.

The Oracle's controlled joint-specific deviation is used for scoring and explanation only. Family labels, residual bounds, and penalties must be chosen from metadata, fitting data, or an explicit development split.

## Compare freedom and sharing {#comparison}

Use the same public fitting data, final whole-body motions, and declared compute budget for all three schemes. Include two cases:

- a family-similar baseline where sharing should reduce variance;
- a controlled joint-specific deviation where sharing may bias the fit.

Repeat enough runs to inspect parameter stability. If a grouping is changed after seeing final evaluation, it is a development decision and needs a new final split.

## Read scale evidence {#evidence}

This is a planned parameter-sharing comparison. The exception and stability views describe the required evidence package; they do not reveal hidden values to the fitter.

Show joint/body error heatmaps, parameter counts, estimate distributions, residuals around the hidden exception, cross-motion predictions, and runtime. Separate:

- lower variance from sharing;
- biased underfitting from excessive sharing;
- instability from an optimizer or data problem.

Only semantically shared, identifiable quantities support a recovery claim. Whole-body prediction can be useful even when individual effective values are not physical.

## Think it through {#exercise}

The shared model has slightly worse training error, better held-out body motion, and a residual concentrated at one joint. The independent model removes that residual but changes dramatically across starts. Which model would you choose for a controller model, and what extra evidence would you request?

<details markdown="1">
<summary>Read a suggested answer</summary>

The shared model may be preferable if body prediction and stability are the declared goals, but the joint residual is a signal to inspect rather than erase. Request repeated runs, joint-level held-out metrics, and an independent component or excitation test for that joint. Choose using the predeclared task and parameter-use requirements, not the best final score.
</details>

The common wrong turn is to select sharing after seeing the final exception score. If you cannot choose, freeze the grouping from metadata or development data and request a joint-specific held-out motion. Continue when variance, bias, and task metrics are reported separately.

## What sharing cannot prove {#limits}

Sharing does not prove actuators are physically identical, and independent parameters do not prove real per-joint differences. A larger model is not automatically more informative. L5 does not add new contact or actuator physics and is not required before L6.

L6 returns to a small plant to make model mismatch explicit. Continue to [L6 · From structural mismatch to a true cross-engine test](../l6/index.md).
