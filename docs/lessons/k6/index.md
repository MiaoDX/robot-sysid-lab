# K6 · Challenge predictions with new experiments

A model can overlap the trajectories used for fitting and still fail on a motion that matters. This lesson turns validation into a design decision: choose what to withhold, keep model selection separate from final evaluation, and use residual structure to decide what to investigate next.

You should finish able to reject a misleading “high accuracy” claim and write a bounded evidence statement.

## Replay is the easiest test to pass {#failure}

If the model is adjusted against a trajectory, plotting that same trajectory again mostly checks whether the fitting loop worked. It does not test whether the model predicts a changed frequency, direction, posture, load, or controller condition.

A random split of neighboring time samples can be equally misleading. Samples on both sides of the split share the same run history, inputs, and hidden state. For a dynamical system, that is not an independent future experiment.

Before looking at the split, predict which held-out condition would challenge a model whose residual grows with frequency and which would challenge one whose residual changes with direction.

## Separate fitting, development, and final evaluation {#split}

Use three roles when a model or fitting rule may be adjusted:

| Role | May influence fitting or choices? | Purpose |
|---|---|---|
| Fitting | Yes, for parameter estimation | Estimate the declared Student parameters |
| Development | Yes, for choosing structure, bounds, scales, or controls | Compare candidate decisions |
| Final evaluation | No, until the decisions are frozen | Report the final prediction claim |

The split should reflect the intended use. A new frequency tests frequency behavior; a new posture tests configuration dependence; a new load tests scaling; a new direction tests asymmetry. Withhold complete runs or conditions with their initial state and timing declared.

The fitter receives only fitting observations. The final evaluation observations stay unavailable during model and hyperparameter selection. If a validation run changes a decision, rename it development and reserve another run.

This clip reuses the completed L0 run: the chirp fits $J,b$, and the multisine evaluates the frozen model. Both the model and the split are fixed before evaluation. Predict first: if the multisine result helped choose parameter bounds, could it still count as final evaluation?

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l0-heldout.png" preload="metadata"><source src="../../../demos/manim/rendered/l0-heldout.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l0-heldout.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l0-heldout.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Can a frozen fit predict a new motion?</figcaption><details><summary>Read the video explanation</summary><p>The chirp estimates J and b; the reserved multisine is evaluated only after fitting.</p><p>On held-out position, orange is the initial model and blue the identified model.</p><p>The identified trace overlaps the Oracle. This supports prediction for the declared boundary and ideal observations.</p></details></figure>

The [fixed report](../../../reports/l0_inertia_damping/report.md) separates fitting and held-out metrics. The clip shows held-out position, while the report's two fourth-row residual panels both use fitting data. Appearing on the same page does not turn fitting residuals into held-out evidence. The tiny errors here come from matched equations and ideal observations and support prediction only under the declared conditions.

## Read residuals as clues, not verdicts {#evidence}

The split and residual examples are a reading contract. A final claim must use a completed, untouched run and its measured metrics.

A residual is the declared difference between model and observation, with a unit and sign convention. Its structure can suggest a hypothesis:

- growth with frequency may point toward timing, unmodeled dynamics, or numerical effects;
- a reversal-localized pattern may point toward friction or hysteresis;
- a posture-dependent pattern may point toward gravity, geometry, or coupling;
- a condition-specific offset may point toward bias, calibration, or an omitted input.

None of these patterns identifies a unique cause. Pair the residual with a sensitivity comparison, a boundary check, or a new experiment. Report both the error magnitude and the conditions over which it was measured.

## Compare predictions on the intended envelope {#comparison}

Use the same baseline and identified models on fitting data and on declared held-out runs. Show trajectories, per-channel metrics, and residuals on a common scale. Summarize errors by the condition that changed, rather than averaging away the failure.

A useful report says: “Under these motions, the identified model reduced position error from A to B; the remaining residual increased with frequency; this supports improved prediction in the tested range, but does not establish performance at higher frequencies.” Replace the placeholders with measured values only after the experiment runs.

For a knowledge lesson, the exact numbers may come from the existing L0/L1 reports. Do not copy a number from one condition into a claim about another.

## Think it through {#exercise}

A team fits a delay model, checks one held-out reversal, sees a low error, and then uses that reversal to choose the delay bound. They report the result as final validation. What is wrong with the claim, and what should happen next?

<details markdown="1">
<summary>Read a suggested answer</summary>

The reversal became development data when it changed the bound. It can no longer support an untouched final claim. Freeze the model, bound, scale, and fitting rule, then evaluate a new complete run chosen for the intended operating change. State whether the new run changes frequency, direction, posture, load, or another condition, and report the range covered.
</details>

The common wrong turn is to tune on the only held-out run and still call it final evaluation. If you cannot classify the split, record which decision changed after viewing it and reserve a fresh complete run. Continue when the final claim names the changed condition and its range.

## What validation cannot prove {#limits}

A successful held-out run supports a bounded prediction claim. It does not establish physical parameter truth, universal generalization, or improved control. A residual pattern is a hypothesis generator, not a diagnosis by itself.

Use K6 throughout L1 and the later labs. [L0-E](../l0-e/index.md) applies these ideas to excitation; L2 applies them to posture and coupling. Continue to [K2 · Locate dynamics terms from motion errors](../k2/index.md) when you need the dynamics vocabulary for the actuator and leg lessons.
