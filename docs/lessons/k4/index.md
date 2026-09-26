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

This clip asks why greater speed does not necessarily separate parameters better. Compare the two inputs at the same peak torque, then the velocity coverage and sensitivity values. The lesson’s contours provide the loss geometry behind the clip’s conclusion.

<figure class="clip"><video controls playsinline poster="../../../demos/manim/rendered/l0-excitation.png" preload="metadata"><source src="../../../demos/manim/rendered/l0-excitation.mp4" type="video/mp4"/><track default kind="subtitles" label="English" src="../../site/subtitles/l0-excitation.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l0-excitation.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Which input separates the effects?</figcaption><details><summary>Read the video explanation</summary><p>The same peak torque, duration, model, scales, and held-out motion are used. Only the fitting excitation changes.</p><p>The slow input has a longer loss valley; the broad input has clearer acceleration reversals and a better-conditioned local Jacobian.</p><p>Both noiseless fits recover and pass held-out prediction. Weak sensitivity is evidence to improve the experiment, not proof of optimizer failure.</p></details></figure>

The L0-E run now provides the corresponding simulation comparison. Both inputs recover the noiseless teacher, but the broad input separates local parameter effects more clearly. This is not a claim that the slow fit fails.

![L0-E simulation coverage and sensitivity](../../../reports/l0_excitation/slow_narrow_vs_broad.png)

The slow record has velocity 0…11.763 rad/s, acceleration RMS 1.609 rad/s², smallest scaled sensitivity singular value 0.494, and condition number 11.81. The broad record has velocity −0.953…6.324 rad/s, acceleration RMS 8.470 rad/s², smallest singular value 1.218, and condition number 1.90. Both use the same 8 s, 0.8 N m peak budget. Output scales are fixed at 1 rad and 1 rad/s; parameter scales use the public initial model, 0.095 and 0.018. Singular values divide the Jacobian by √(2N). Purple denotes J and green b; solid lines show position derivatives and dashed lines velocity derivatives, on shared axes. Read the broad input as better local separation under this contract, while noting its different state coverage.

![L0-E simulation loss contours](../../../reports/l0_excitation/excitation_loss_contours.png)

The long slow valley and compact broad contours are the exact scaled residual objective. Eighteen declared starts recover J = 0.065 and b = 0.055, so the weak valley is not presented as an invented optimizer failure. The shared held-out multisine gives about 2.4 × 10⁻¹⁴ rad position RMSE for both fits. See the [reproducible report](../../../reports/l0_excitation/report.md) and run `python -m synthetic.l0_excitation --output-dir reports/l0_excitation`.

Three views answer different questions:

1. **Coverage:** Do the two fitting inputs actually produce different ranges of $\dot q$ and $\ddot q$?
2. **Sensitivity:** Are the output changes caused by $J$ and $b$ distinguishable over those samples?
3. **Loss surface:** If we evaluate many $(J,b)$ pairs, is the low-loss region compact or an elongated valley?

An elongated valley means a family of parameter pairs behaves similarly for this experiment. It does not by itself prove that the parameters are structurally impossible to identify. A new input, a new posture, an independent measurement, or a different model boundary may cut across the valley.

A multi-start fit is useful evidence about this run's optimization behavior. Several starts landing in one valley does not prove that every experiment would recover the same physical values.

## Think it through {#exercise}

Use the simulation figures above: which column crosses positive and negative acceleration? At the same 0.2 contour level, which valley is longer? Match that observation to condition numbers 11.81 and 1.90.

Then inspect the report’s 18 starts and shared held-out prediction: can you claim the slow input is unidentifiable, or that the broad input predicts significantly better? What would you change first to gain margin against perturbations in a next experiment?

<details markdown="1">
<summary>Read a suggested answer</summary>

The broad input on the right crosses positive and negative acceleration. The slow input on the left has a longer 0.2 contour, matching its larger condition number of 11.81. Prefer excitation that introduces independent acceleration changes, while checking actual state constraints. Both inputs recover and achieve about 2.4 × 10⁻¹⁴ rad held-out RMSE, so this cannot establish slow-input non-identifiability or rank prediction from floating-point differences. Compact contours support local separation; they do not measure noise robustness, prove global uniqueness, or guarantee hardware transfer.

If the held-out result is used to choose a frequency band or retune the objective, it becomes development data. Reserve a fresh final evaluation for the resulting claim.
</details>

Do not repair a long loss valley by adding more nearby samples. If you cannot choose, inspect scaled sensitivity columns and state which new condition would rotate one of them. Continue when the proposed input changes information rather than only sample count.

## What this experiment cannot tell us {#limits}

This comparison studies practical information in a matched, noiseless single-joint model. It does not prove a globally unique solution, quantify hardware sensor uncertainty, or decide whether a missing physical effect is present. A structured residual after a better input can still have several explanations.

The next lesson explains how an optimizer uses a declared objective and why its stopping status is evidence about the fitting process, not proof that the model is correct.

Continue to [K5 · Understand what fitting actually solved](../k5/index.md).
