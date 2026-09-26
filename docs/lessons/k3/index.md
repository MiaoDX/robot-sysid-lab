# K3 · Trace commands to joint torque

A command is not automatically a torque measurement. Controllers, timing, friction, and output limits can all change what the joint receives. This lesson gives you a boundary for reasoning about those effects one at a time.

The key question is not “which actuator model is richest?” It is “which hidden effect does the current evidence require us to add?”

## A correct command can produce a wrong motion {#failure}

Suppose the desired position follows a clean sweep, but the joint lags at high frequency and leaves a directional error near reversals. Increasing a rigid-body inertia may reduce one plot's error while hiding the command-to-torque problem.

Predict how three isolated effects would look: a fixed command delay, a resisting torque that changes with speed direction, and a symmetric torque limit. Their signatures overlap in closed-loop motion, so the experiment must change the condition that each effect responds to.

## Define the command-to-torque boundary {#boundary}

A simple controller can be written as

$$
\tau_\text{cmd} = K_p(q_\text{des}-q) + K_d(\dot q_\text{des}-\dot q).
$$

The plant boundary may then include a delay, saturation, and resistance before the mechanical dynamics:

```text
q_des → fixed controller → command delay → saturation/friction → joint dynamics → q, q̇
```

The lesson must declare which signal enters the Student. A command-only Student cannot use the Oracle's actual applied torque to explain its own result. If applied torque is measured and part of the intended boundary, say so explicitly.

## See the boundary move {#media}

The static boundary diagram names the signals; this clip shows the recorded command and delayed input on a shared time axis.

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l1-boundary.png" preload="metadata"><source src="../../../demos/manim/rendered/l1-boundary.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l1-boundary.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l1-boundary.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Where does the delay hide?</figcaption><details><summary>Read the video explanation</summary><p>The delay follows the fixed PD law; the orange input is the yellow command shifted by 0.080 s.</p><p>Readback is an Oracle diagnostic for this lesson's boundary, not an extra Student observation.</p></details></figure>

For the frequency clue, watch the fixed delay occupy more of each shorter cycle. The phase formula is a local intuition for a pure delay; closed-loop position also depends on mechanics and control.

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l1-phase.png" preload="metadata"><source src="../../../demos/manim/rendered/l1-phase.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l1-phase.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l1-phase.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Why does a chirp reveal the delay?</figcaption><details><summary>Read the video explanation</summary><p>The delay remains 0.080 s while frequency increases.</p><p>The phase share grows; this is not a direct measurement of motor time constant.</p></details></figure>

## Isolate one actuator effect at a time {#comparison}

Use the same controller and mechanical parameters while changing one hidden effect:

| Isolated effect | Condition that exposes it | First comparison |
|---|---|---|
| Delay | frequency and command timing | sweep versus reversal, with command history reset |
| Friction | speed direction and reversal rate | low/high speed, forward/reverse |
| Saturation | command amplitude | below and above the limit |

Do not add delay, friction, and saturation to one Student before the single-effect cases are understood. A richer model can reduce fitting error by absorbing a different missing effect.

## Compare the friction clue {#friction-media}

The friction extension uses a different declared boundary: known applied torque drives a rotary load, with known inertia and no delay, gravity, or saturation. Both Students fit the same t, u, q, qd observations, then freeze parameters for a new input. The resistance curve is evaluator-only; the held-out position residual evaluates prediction.

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l1-friction.png" preload="metadata"><source src="../../../demos/manim/rendered/l1-friction.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l1-friction.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l1-friction.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Can viscous damping explain friction?</figcaption><details><summary>Read the video explanation</summary><p>Viscous-only residuals remain around reversals; the richer friction Student follows the Oracle.</p><p>The pattern is evidence to investigate, not proof that friction is the only cause.</p></details></figure>

## Read actuator evidence {#evidence}

The table above is a conceptual contract; the linked L1 clips and reports are measured synthetic evidence. Any applied-torque or internal-state trace is an Oracle diagnostic unless the page explicitly declares it as an observation.

Use a boundary diagram, a signal timeline, and condition-specific residuals together. A phase shift is a clue for delay, not a direct measurement of motor electromagnetic time. A reversal-localized residual is a clue for resistance, not proof that friction is the only missing effect. A flat response at large commands suggests saturation only if the command actually crosses the limit.

Mark Oracle-only signals such as actual applied torque and internal delay state. They can explain why a trace looks the way it does, but they must not leak into a command-only fit.

## Think it through {#exercise}

Compare the two clips: why may the friction Student see applied torque u while the delay Student may not see the orange actuator-input trace?

<details><summary>Check the boundary</summary><p>The friction experiment explicitly starts at known applied torque. The delay experiment starts at a position command and estimates the hidden command-to-torque timing. Adding actual torque to that fit would change the problem.</p></details>

A command sweep has a phase-like error at high frequency. A low-speed reversal has a sign-dependent error. A large-amplitude command produces a clipped applied torque in the Oracle diagnostic plot. Which isolated experiment would you use for each hypothesis, and which signal must remain hidden from the fitter?

<details markdown="1">
<summary>Read a suggested answer</summary>

Use a frequency comparison with a declared command history for delay, bidirectional low/high-speed motions for friction, and below/above-threshold amplitudes for saturation. Keep actual applied torque and internal actuator states hidden when the Student is meant to infer effects from commands and motion. Those signals can appear in an explanation or evaluator-only plot.
</details>

The common wrong turn is to use the Oracle's applied torque to explain a command-only fit. If you cannot choose an experiment, hold the controller fixed and change only frequency, direction, or amplitude. Continue when each hypothesis has one condition that could make it disagree with the others.

## What the command boundary cannot prove {#limits}

An effective command delay depends on where the boundary is drawn; it is not automatically an electromagnetic motor constant. A smooth resistance term is not a full friction law, and a fitted limit may be only a lower bound when the data never cross it.

K7 will explain why these fitted values can be physical, effective, nuisance, or uncertain. L1 applies the isolated delay and friction cases; L1-O adds observation quality, while L1-S is an elective saturation case.

Continue to [L1 · Actuator delay and friction](../l1/index.md).
