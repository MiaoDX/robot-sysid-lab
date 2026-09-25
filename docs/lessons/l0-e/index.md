# L0-E · When input hides a parameter's effect

L0 shows that a matched model can recover inertia and damping from informative motion. This companion experiment asks the harder question: can a large dataset still leave a parameter weakly constrained when the input does not reveal its effect?

The numerical runner and fixed report are still to be implemented. This page freezes the learner-facing contract and exercises without claiming measured sensitivity, fitted values, or a runtime.

## More rows do not guarantee more information {#failure}

Imagine collecting a long, slow motion near one speed. The fitting loss may be small because the model predicts that narrow behavior well. Yet inertia appears through acceleration, while viscous damping appears through velocity. If acceleration barely changes, many parameter combinations can remain plausible.

Predict what a wider-band input with reversals should change. It may separate the effects, but it can also leave the intended operating range. Information and safety are both experiment-design constraints.

## Keep the L0 boundary fixed {#boundary}

Reuse the matched L0 plant:

$$
J\ddot q + b\dot q = u.
$$

The fitting input and ideal $q,\dot q$ observations are public. The Student, estimator, bounds, objective scaling, initial state, and final held-out multisine are fixed across the comparison. Only the fitting excitation changes. Oracle parameters remain evaluation-only.

This isolation matters. Adding noise, changing the estimator, or widening the model at the same time would make an observed difference ambiguous.

## Compare slow and broadband excitation {#comparison}

Use the same declared amplitude and duration budget:

| Fitting excitation | Expected information | What to record |
|---|---|---|
| Slow/narrow-band input | Small acceleration variation | velocity and acceleration coverage |
| Wider-band sweep with reversals | More independent velocity/acceleration patterns | frequency, state coverage, and command range |

Score both fits on the same final held-out multisine, chosen before seeing either result. Report the actual state coverage rather than assuming equal command budgets are equivalent.

A browser control, if later justified by a runtime measurement, may choose among bounded input presets. It must not expose an unbounded optimizer or silently change the final evaluation.

## Read the planned evidence {#evidence}

The fixed evidence package will include input and state coverage, scaled sensitivity directions, a two-parameter loss surface, multiple starts, parameter estimates, and held-out error. Read these views together:

- weak sensitivity suggests a data limitation, not an automatic optimizer failure;
- a long loss valley shows parameter combinations with similar behavior;
- held-out error tests whether the selected excitation supports prediction;
- a change after a new input is evidence about the experiment, not proof of a universal design rule.

If a final result is used to choose the input preset or objective, it becomes development data and needs a new final evaluation.

## Think it through {#exercise}

A slow input gives a lower fitting loss than a broadband input. Its loss surface is elongated, while the broadband fit has a higher fitting loss but a better held-out prediction. Which result should guide the next experiment?

<details markdown="1">
<summary>Read a suggested answer</summary>

Use the declared prediction goal and held-out evidence, not fitting loss alone. The broadband input may expose more useful behavior even if its optimization is harder. Inspect scaling, convergence, and state coverage before concluding that its higher loss is a problem. If the next choice is made from the held-out result, reserve another final run.
</details>

## What this experiment cannot prove {#limits}

This comparison isolates excitation under ideal observations and a matched two-parameter model. Weak sensitivity does not prove structural non-identifiability, and a successful broadband fit does not guarantee hardware identifiability. Noise and preprocessing belong to L1-O; multibody excitation returns in L2.

Continue to [K2 · Locate dynamics terms from motion errors](../k2/index.md) and [K3 · Trace commands to joint torque](../k3/index.md).
