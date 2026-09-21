# L0 · Assumptions and the next step

L0 uses known applied torque and ideal position and velocity observations. The system generating the data and the fitted model share the same equation, so we can directly check the estimated inertia and damping.

Under these conditions, the model estimates parameters from a chirp and predicts motion under a separate multisine input. This establishes a working experiment to compare with later ones.

Real joints may also have command delay, torque limits, other friction, compliance, and sensor noise. When those effects matter, changing inertia and damping alone may be insufficient. Fitted values can compensate for missing effects: a larger inertia parameter might improve one trajectory while failing to predict another.

## What to study next

[L1](../l1/index.md) uses a known arm, payload, and position controller, then adds one unknown command delay. We will see how it changes motion and test whether a delay estimated from one motion predicts another.

The question changes, but we still need to understand inputs and observations, fit parameters, and check data withheld from adjustment. This distinguishes a closer match to the original data from better prediction on a new motion.

## Explain the result in one sentence

Include both the experiment conditions and its validation result. For example:

> With known torque, ideal observations, and a correct model structure, we estimated inertia and damping from a chirp and predicted a multisine motion withheld from fitting.

Before applying this result to hardware, check which conditions still hold and decide what additional models or measurements are needed.
