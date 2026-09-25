# K8 · Use identification for control and transfer

A model that predicts motion better may help a controller, but prediction and control are different claims. This lesson gives a fair protocol for testing the connection and explains where RL and domain randomization belong.

The core comparison redesigns controller settings from two models using one declared method, then evaluates both on the same hidden Oracle.

## Better prediction is not automatically better control {#failure}

Suppose an identified model has lower held-out trajectory error. If the controller running on the real system is unchanged, that offline improvement does not change the closed-loop behavior. If a new controller is designed from the identified model, its behavior can change, but the design method and evaluation must be controlled.

Before seeing results, predict a case where tracking improves while control effort or constraint violations worsen.

## Separate the three evaluation protocols {#boundary}

Use clear names:

| Protocol | What changes | What it tests |
|---|---|---|
| Same-input prediction | Model only | Open-loop or replay prediction |
| Same-controller closed loop | Physical system and controller stay fixed | Whether model accuracy alone changes no controller outcome |
| Model-based redesign | Initial/identified model each produces settings with one design method | Whether identification supports a downstream controller design |

The core lesson uses the third protocol. Freeze the task, controller design rule, budget, constraints, initial conditions, disturbances, and hidden Oracle. Do not tune the controller repeatedly against final Oracle scores.

## Freeze data before designing controllers {#comparison}

The workflow is

```text
collect and split data → identify models → freeze model-selection rule →
apply one controller-design method to each model → evaluate both in one Oracle
```

The identification final evaluation cannot also be used to choose the controller or claim its final performance. If the design method changes after seeing Oracle results, declare a new development cycle and reserve a new evaluation.

RL training and broad or targeted domain randomization are extensions. They introduce policy optimization and training-distribution choices that must be evaluated under their own protocol.

## Read downstream evidence {#evidence}

Report prediction metrics separately from tracking error, control effort, and constraint violations. Pair initial conditions and disturbances where possible. A controller that tracks better but uses more effort may be preferable or unacceptable depending on the declared task cost.

The evidence should show both model-to-controller paths and the same Oracle evaluation conditions. Do not use a single final score to hide a change in safety margin or operating range.

## Think it through {#exercise}

A report says: “The identified model improves control because its prediction error is lower.” The controller configuration was unchanged. What is missing, and what fair comparison would you request?

<details markdown="1">
<summary>Read a suggested answer</summary>

The claim confuses prediction with downstream control. With an unchanged controller and physical system, changing an offline model cannot by itself change the closed-loop result. Request two controller configurations generated from the initial and identified models using the same design method, then evaluate them on the same hidden Oracle with paired conditions and declared tracking, effort, and constraint metrics.
</details>

## What this protocol cannot prove {#limits}

A positive control comparison does not prove hardware transfer, universal robustness, or policy improvement. It is one task under one controller-design method and one Oracle. RL retraining, randomization, and deployment require separate data lineage and evaluation.

L4 applies this bounded protocol after comparing whole-robot fitting routes. Continue to [L4 · Compare whole-robot fitting routes and control outcomes](../l4/index.md).
