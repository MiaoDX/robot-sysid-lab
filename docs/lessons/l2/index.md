# L2 · Separate actuator and body errors in a fixed-base leg

A coupled leg can fit one posture while hiding whether the error belongs to an actuator or a link model. Start by making that decision explicit: predict which change in posture or acceleration should separate the two explanations. This lesson introduces multijoint coupling without contact or floating-base uncertainty.

The first goal is not to recover every inertial property. It is to learn which parameter combinations the motions can distinguish and how component evidence changes that ambiguity.

Here **Student** means the fitted leg model and **Oracle** means the hidden system that generates the reference motion. Applied torque, true link parameters, and internal forces are **diagnostic signals** unless the experiment contract makes them observations.

## One posture can hide two wrong subsystems {#failure}

Start with a two-joint fixed-base leg. You first choose the condition that should separate the hypotheses. A Student with an incorrect link inertia may improve its trajectory by changing an actuator scale or damping term. On one posture, both changes can compensate. On another posture or frequency, they can diverge.

Predict which new condition would expose a body-model error and which would expose a timing or actuator error. State what you would keep fixed before fitting.

## Declare the coupled-leg boundary {#boundary}

The primary boundary is

```text
joint commands → fixed actuator/controller boundary → two-joint fixed-base leg → encoder observations
```

The general dynamics include coupling and gravity:

$$
M(q)\ddot q + C(q,\dot q)\dot q + g(q) + \tau_f = \tau.
$$

The Student initially fits one declared link-inertia group. Later comparisons allow a limited actuator group. Applied torque, true body parameters, and internal forces remain evaluator or Oracle diagnostics. Contact and floating-base motion are outside this lesson.

## Run isolated and coupled cases {#comparison}

The four cases below are a **planned experiment contract**. They specify what we will compare; they are not measured results until a runner produces the traces and report. Use the same public fitting motions, controller, parameter scales, and budget across four cases:

| Case | Hidden mismatch | Teaching purpose |
|---|---|---|
| A | Rigid-body group only | See whether coupling evidence recovers a body-side effect |
| B | Actuator group only | See how actuator errors appear across posture/frequency |
| C | Both groups | Expose compensating solutions |
| D | Both, with component constraints | Test whether lower-level evidence reduces ambiguity |

Hold out a posture or frequency family. Choose parameter groups through sensitivity evidence and metadata, not by inspecting final evaluation.

## Read leg evidence {#evidence}

When the runner is available, show synchronized joint traces, per-joint residuals, parameter correlations or loss slices, and held-out errors before and after component constraints. These are planned evidence views for this page. Count the extra actuator or component data used by Case D.

A constraint can reduce an ambiguity without proving that every remaining parameter is physical. If a lower-level fit is wrong, carrying it into the whole leg can make the global fit look more certain than it is.

## Think it through {#exercise}

Cases B and C have similar fitting errors. In C, the actuator scale and link inertia move in opposite directions across starts, and the held-out posture is poor. Which next motion would you choose, and which parameter group would you constrain first?

<details markdown="1">
<summary>Read a suggested answer</summary>

Choose a motion that changes posture and acceleration separately, such as repeating the same joint-1 excitation at two joint-2 postures and adding a joint-2 excitation. Constrain the group with independent component evidence and the weaker sensitivity support, rather than choosing from the final score. Recheck the held-out posture after the constraint.
</details>

The common wrong turn is to select the group with the best final score, or to treat a lower fit loss as proof of physical correctness. If you cannot choose, inspect which group has independent component evidence and which condition changes its sensitivity; then rerun the held-out posture. Continue when you can name the evidence that would reverse your choice.

## What this leg cannot prove {#limits}

A fixed-base leg does not establish contact behavior, floating-base dynamics, or separate recovery of all mass, center-of-mass, and inertia terms. An effective parameter can still predict well within the tested posture/frequency envelope.

L3 adds one new uncertainty class: compliant normal contact. It must preserve the free-space evidence from this lesson. Continue to [L3 · Add contact after validating free space](../l3/index.md).
