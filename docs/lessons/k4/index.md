# K4 · Decide whether an experiment separates parameters

A fitting program can report a tiny error while the parameters remain poorly constrained. This lesson asks why that happens and how to design an input that reveals the effects we want to estimate.

You should finish this lesson able to read a sensitivity comparison, recognize a long loss valley, and propose a better experiment without treating “more samples” as the answer.

## A small error can hide a large question {#failure}

L0 estimates inertia $J$ and viscous damping $b$ from a rotating joint. Suppose the fitting curve almost overlaps the observed curve. Does that mean both values are known?

Not necessarily. If the recorded motion changes speed only a little, the terms $J\ddot q$ and $b\dot q$ may contribute in nearly the same proportion throughout the run. Several pairs of values can then make similar predictions. The optimizer has found a good region of behavior, but the experiment has not told us which direction inside that region is correct.

Before reading the comparison, predict what should happen when the input produces mostly slow motion and what should happen when it produces clear accelerations and reversals.

## What can the estimator see? {#boundary}

The plant boundary is the same as L0:

<div class="signal-flow" role="img" aria-label="Known applied torque enters a rotating joint and produces observed position and velocity"><span>Applied torque $u$</span><span aria-hidden="true">→</span><strong>Rotating joint</strong><span aria-hidden="true">→</span><span>Observed $q$, $\dot q$</span></div>

The Student model is

$$
J\ddot q + b\dot q = u.
$$

The fitter receives only the fitting input and observations, plus parameter bounds and the declared objective. Oracle parameters and the final held-out motion are evaluation-only. In this noiseless teaching case, weak information means weak separation of parameter effects, not sensor noise.

A useful local question is: if we change $J$ slightly, how does the predicted curve move? The corresponding change is a **sensitivity**. Put the sensitivity to $J$ and the sensitivity to $b$ side by side. If their columns point in nearly the same direction over the recorded samples, the data struggle to distinguish the parameters.

## Compare the input, not just the sample count {#comparison}

Hold the system, amplitude budget, duration budget, model, bounds, estimator, and final evaluation motion fixed. Change only the fitting input:

| Fitting input | What it exposes | Risk |
|---|---|---|
| Slow, narrow-band motion | A limited range of velocity and acceleration | Inertia may have little independent effect |
| Wider-band sweep with reversals | More distinct velocity and acceleration patterns | Larger motion may leave the intended operating range |

The fair comparison is not “which run has more rows?” Record the actual position, velocity, and acceleration coverage. Equal duration and amplitude do not guarantee equal information.

The final evaluation motion must be declared before looking at its score. It tests whether the input choice produced a model that predicts a new condition.

## Read sensitivity and loss-valley evidence {#evidence}

The sensitivity and loss views here are conceptual until a corresponding run is replayed. They explain what evidence to request; they do not report a new measured result.

Three views answer different questions:

1. **Coverage:** Do the two fitting inputs actually produce different ranges of $\dot q$ and $\ddot q$?
2. **Sensitivity:** Are the output changes caused by $J$ and $b$ distinguishable over those samples?
3. **Loss surface:** If we evaluate many $(J,b)$ pairs, is the low-loss region compact or an elongated valley?

An elongated valley means a family of parameter pairs behaves similarly for this experiment. It does not by itself prove that the parameters are structurally impossible to identify. A new input, a new posture, an independent measurement, or a different model boundary may cut across the valley.

A multi-start fit is useful evidence about this run's optimization behavior. Several starts landing in one valley does not prove that every experiment would recover the same physical values.

## Think it through {#exercise}

You have two fitting datasets with the same duration and maximum command. Dataset A keeps the joint near one speed. Dataset B contains repeated accelerations and reversals. The fitted losses are similar, but Dataset A produces a long diagonal valley in $(J,b)$ while Dataset B produces a compact region.

Which dataset should you use if the next task changes the frequency content? What additional plot would you request before claiming that Dataset B identifies both parameters?

<details markdown="1">
<summary>Read a suggested answer</summary>

Prefer Dataset B because its input separates velocity and acceleration effects more clearly. Request the actual state coverage and the sensitivity directions, then check the final held-out motion that was declared before fitting. A compact loss region supports local separation under this setup; it does not establish global uniqueness or guarantee transfer to every load and frequency.

If the held-out result is used to choose a frequency band or retune the objective, it becomes development data. Reserve a fresh final evaluation for the resulting claim.
</details>

Do not repair a long loss valley by adding more nearby samples. If you cannot choose, inspect scaled sensitivity columns and state which new condition would rotate one of them. Continue when the proposed input changes information rather than only sample count.

## What this experiment cannot tell us {#limits}

This comparison studies practical information in a matched, noiseless single-joint model. It does not prove a globally unique solution, quantify hardware sensor uncertainty, or decide whether a missing physical effect is present. A structured residual after a better input can still have several explanations.

The next lesson explains how an optimizer uses a declared objective and why its stopping status is evidence about the fitting process, not proof that the model is correct.

Continue to [K5 · Understand what fitting actually solved](../k5/index.md).
