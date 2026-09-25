# L4 · Compare whole-robot fitting routes and control outcomes

A whole robot makes two questions meet: when do component measurements help a global fit, and does a better model support a downstream control task? This lesson compares the workflows before making the control claim.

The first whole-robot case uses supported or fixed-base Microduck motions. Full locomotion and RL training are extensions, not the first completion gate.

## A good component fit can fail at whole-robot scale {#failure}

A component-first route may provide useful constraints, but its assumptions and data costs travel into the whole-robot fit. A global fit may use more freedom and produce a lower training loss while leaving parameters ambiguous.

Predict a case where component constraints improve held-out prediction and a case where they bias the model because the component boundary does not match the whole robot.

## Declare the Microduck boundary {#boundary}

Use one primary backend, one Microduck Oracle, a compact Student parameterization, and declared command, joint, and base observations:

```text
commands → actuator/body/contact boundary → Microduck → joint/base observations
```

The fitting route is part of the experiment:

- Route A: fit components, validate them, then constrain a whole-robot fit;
- Route B: fit a compact whole-robot model directly.

The Oracle truth, internal forces, and hidden states remain unavailable to the Student. Extra component data and computation in Route A are part of its cost.

## Compare routes, then redesign controllers {#comparison}

Share whole-robot fitting motions, held-out motion families, model-selection rules, and declared budgets. Start with supported/fixed-base actions, then add stance or locomotion only after the contract is stable.

For the bounded downstream case:

1. freeze the initial and identified model-selection rule;
2. generate controller settings from each model using the same design method;
3. evaluate both settings in the same Oracle with paired initial conditions and disturbances;
4. report tracking, control effort, and constraint violations separately.

Do not train RL inside the identification loop. Policy training and randomization belong to a later extension with separate data lineage.

## Read whole-robot evidence {#evidence}

Show route cost, data lineage, joint and base errors, prediction horizon, and parameter interpretation. Then show the two model-to-controller paths and the matched Oracle evaluation. A route with a lower fitting loss may still have worse held-out motion or less interpretable parameters.

Count the number of component runs, fitting time, and constraints. Otherwise the comparison can accidentally report an unequal-data advantage as an optimizer advantage.

## Think it through {#exercise}

Route A uses extra actuator data and has a slightly higher whole-robot fitting loss. It predicts held-out base motion better, while its controller uses less effort but tracks one joint less accurately. Which route is better?

<details markdown="1">
<summary>Read a suggested answer</summary>

There is no single answer without a declared task cost and data budget. Report the extra data/compute, held-out joint/base metrics, and controller metrics separately. Choose A only if the intended task values its improved base prediction and effort within the declared constraints; otherwise the global route may be preferable. Do not reduce the decision to fitting loss.
</details>

## What the whole-robot case cannot prove {#limits}

A supported Microduck case does not establish free locomotion, hardware transfer, or RL policy improvement. Parameter recovery is meaningful only for shared, identifiable quantities. The same Oracle evaluation does not make an unchanged controller comparison informative.

L5 studies how parameter sharing scales to Microban. L6 returns to a small plant to study structural and cross-engine mismatch. Continue to [L5 · Share parameters across Microban joints](../l5/index.md).
