# L1 · Actuator delay and friction

L0 started with known torque and estimated a joint's inertia and damping. This lesson uses position control: we specify a target angle, a controller calculates torque, and that torque drives a loaded arm.

What changes if the torque command takes a little time to reach the arm? Can we estimate that delay from recorded motion, then use it to predict a different motion?

## Meet the machine {#machine}

The setup has a fixed base, one rotary axis, a rigid arm, and a payload at the tip. Arm length, arm mass, payload mass, and gravity are known. Angle $q$ is measured from the downward vertical.

A position controller compares the target angle with the current angle and calculates a torque command. We insert a delay before that command is applied. The initial model assumes immediate application; our task is to check and improve that assumption using data.

## Locate the delay {#boundary}

Follow the command path: the target position enters a fixed PD controller, which computes torque. The torque command is delayed before reaching the arm and producing motion.

```text
Target position
    → PD controller
    → torque-command delay
    → loaded arm
    → position and velocity
```

The delay applies to the complete torque command calculated by the controller. Delayed position measurements would define a different problem, so first identify where the delay occurs.

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l1-boundary.png" preload="metadata"><source src="../../../demos/manim/rendered/l1-boundary.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l1-boundary.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l1-boundary.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Where does the delay hide?</figcaption><details><summary>Read the video explanation</summary><p>A fixed base, rigid arm, and payload. A drawing does not reveal command delay.</p><p>q_des enters the fixed PD controller. The buffer stores the full torque command c.</p><p>Delay is after PD; the delayed torque drives the gravity-loaded pendulum.</p><p>This is an effective command delay at this boundary, not an electromagnetic motor time constant.</p></details></figure>

<details markdown="1">
<summary>Expand the model equations</summary>

The PD controller uses position error and current velocity to calculate torque:

$$
c_k=k_p(q^{des}_k-q_k)-k_d\dot q_k,\qquad \tau_k=\operatorname{delay}(c)_k
$$

$k_p$ and $k_d$ are fixed gains. A buffer stores already computed torque commands $c$; the delay selects and interpolates command history. History before the first recorded command is zero.

Torque drives the known loaded pendulum:

$$
I\ddot q=\tau-g\ell\left(\frac{m_a}{2}+m_p\right)\sin q,\qquad I=\frac{m_a\ell^2}{3}+m_p\ell^2
$$

$m_a$ is the uniform arm mass, $m_p$ is the point payload mass, and $\ell$ is arm length. The arm mass is distributed along its length while the payload is at the tip, so they contribute differently to inertia and gravitational torque.

</details>

Fitting receives time, target position, recorded position, and velocity calculated by finite differences of position. Internal torque records and true delay are available only for explanation and evaluation. Mechanical parameters, controller gains, and integration settings stay fixed; delay is the only estimated parameter.

## Why faster motion reveals timing error {#phase}

The fitting input is a position chirp with increasing frequency. At low frequency, a fixed delay occupies only a small part of a cycle. As the period shortens, the same delay occupies a larger share.

The delay stays at 0.080 s throughout this clip. Watch why its phase effect becomes more visible as frequency rises.

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l1-phase.png" preload="metadata"><source src="../../../demos/manim/rendered/l1-phase.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l1-phase.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l1-phase.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Why does a chirp reveal it?</figcaption><details><summary>Read the video explanation</summary><p>During the chirp, frequency increases while delay stays at 0.080 s.</p><p>The same time delay occupies more of each shorter cycle, revealing a phase difference.</p><p>The local phase clue is about 360 × frequency × delay; closed-loop response also depends on plant and controller.</p></details></figure>

For a sinusoid at frequency $f$, a pure time delay $\Delta t$ gives a phase-lag magnitude of $360f\Delta t$ degrees. Our arm runs under feedback control, so its angle response also depends on the mechanics and controller. This relation builds intuition; position phase difference alone is not a direct delay measurement.

## Estimate delay from the observations {#fit}

The fitting program tries delay values, predicts position and velocity, and compares them with the chirp observations. Candidate delays stay within bounds chosen before fitting.

This run compares against a zero-delay initial model and produces the result below. All other model parameters stay fixed. The true delay is revealed for checking the completed fit.

| Role | Effective delay | Mechanical parameters |
|---|---:|---|
| Oracle (evaluation only) | 0.08000 s | fixed known arm and payload |
| Initial model | 0.00000 s | same known values |
| Identified Student | 0.08000 s | same known values |

The estimate approaches 0.080 s, showing that this model can explain the timing mismatch in the chirp. Next, freeze the result and test another motion.

## Test another motion {#validation}

Validation uses a separately prepared reversal waveform with a different frequency and phase composition. Both runs start at zero angle and zero internal velocity. The validation data does not select the delay.

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l1-heldout.png" preload="metadata"><source src="../../../demos/manim/rendered/l1-heldout.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l1-heldout.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l1-heldout.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>Did the fit predict the held-out motion?</figcaption><details><summary>Read the video explanation</summary><p>Fit delay on a chirp; these reversal motions are withheld from fitting.</p><p>Compare Initial and Identified position RMSE. The blue trace nearly overlaps truth.</p><p>Better held-out prediction supports this model under known mechanics, fixed PD, and ideal observations.</p></details></figure>

These are the root mean square errors (RMSE) for position `q` and velocity `qd` from that run. RMSE squares the errors, averages them, then takes the square root, so larger deviations have a stronger effect on the result.

| Split | Initial q RMSE (rad) | Identified q RMSE | Initial qd RMSE (rad/s) | Identified qd RMSE |
|---|---:|---:|---:|---:|
| Fit chirp | 0.00442141 | 9.4514e-18 | 0.0177397 | 1.85405e-16 |
| Held-out reversals | 0.0308547 | 6.00653e-17 | 0.490069 | 1.10139e-15 |

The identified model also reduces error on validation, showing that the estimated delay improves prediction for these new commands. Errors near numerical precision reflect the matching equations, known mechanics, and ideal observations in this example.

## Look for clues in the residuals {#residuals}

[![L1 machine, fit and validation curves, residuals, and local loss](../../../reports/l1_servo_loaded_pendulum/report.png)](../../../reports/l1_servo_loaded_pendulum/report.png)

Black represents the true system, orange the initial model, and blue dashed lines with hollow markers the identified model. Residuals are model predictions minus observations. Click the image to inspect it at full size.

Start with the orange residuals near reversals. A response that arrives early or late produces a pattern of positive and negative deviations. For small time shifts, position error is often related to velocity, so a residual-versus-velocity plot can reveal a clue.

Velocity correlation alone cannot establish friction as the cause: delay can produce a similar pattern. Use the system boundary to guide experiments that distinguish possible causes. Torque traces in this figure help explain the motion; the fitting program did not receive those hidden signals.

## Extension: friction versus viscous damping {#friction}

The delay experiment raises a second question: when a residual follows velocity, is the missing effect timing or resistance? We isolate that question in a known-torque rotary load before combining effects in a richer model.

The friction extension uses:

$$
J\\ddot q + b\\dot q + \\tau_c\\tanh(\\dot q/v_{eps}) = u
$$

`J` and `v_eps` are fixed and known. The Oracle has viscous damping `b` and a smooth Coulomb-like term `tau_c`; delay, gravity, saturation, sensor noise, and backlash are absent. The estimator receives only `t`, applied torque `u`, `q`, and `qd`.

We compare two Students:

- **Viscous-only:** fit `b` with `tau_c = 0`;
- **Friction:** fit both `b` and `tau_c`.

The fit motion is bidirectional and includes low and moderate speeds. A different amplitude, frequency, and harmonic composition is held out. In the frozen run, the viscous-only fit returns `b=0.097292`; the friction Student recovers `b=0.055000` and `tau_c=0.060000`. The held-out q and qd RMSE ratios (friction / viscous) are approximately `1.18e-18` and `2.67e-17`; the reversal-window ratio is `1.22e-19`.

![L1 friction extension: resistance and reversal residuals](../../../reports/l1_friction/report.png)

These results show why the experiments are separated: L1 first isolates timing in the closed-loop command path, then this extension isolates a resisting-torque hypothesis. A velocity-correlated residual alone does not prove friction; delay, filtering, or an incorrect torque boundary can produce similar patterns.

This extension uses smooth `tanh` friction. It does not cover static sticking, Stribeck behavior, asymmetric friction, backlash, sensor noise, or hardware transfer. See the [friction experiment report](../../../reports/l1_friction/report.md) and [Notebook](../../../notebooks/l1_friction.ipynb) for the reproducible local run.

## Think it through {#exercise}

1. Why could predictions be inaccurate even with correct arm length and masses?
2. Why does the same 0.080 s delay produce a larger phase shift at higher frequency?
3. If residuals correlate with velocity, what evidence would you need before attributing the error to friction?

<details markdown="1">
<summary>Read suggested answers</summary>

The drawing does not describe the timing of the full command path. Late commands can change the closed-loop response even when mechanical parameters are correct.

Higher frequency means a shorter period, so the same delay occupies a larger fraction of a cycle. The closed-loop angle response still depends on the controller and mechanics.

Design experiments that separate timing shifts from resisting torque. For example, vary command frequency under known control and mechanical conditions to test the timing explanation, then use motions spanning different directions and speeds to investigate friction. A correlation plot alone does not determine the cause.

</details>

If delay and friction still look interchangeable, keep the boundary fixed and add a bidirectional speed comparison before widening the Student. Continue when the proposed run changes one declared condition and preserves the frozen evaluation split.

## Understand what the delay represents {#limits}

This is an effective delay between the PD torque command and the arm input in this experiment. Moving the delay or changing the sampling setup can change the parameter's meaning. It should not be interpreted as the motor's electromagnetic time constant.

The experiment still omits other friction, saturation, compliance, measurement noise, and contact. Its result supports timing estimation and new-motion prediction for these known mechanics. A real actuator needs measurements to check those assumptions.

L1 now contains two isolated actuator experiments: command delay in the closed-loop loaded arm, followed by friction versus viscous damping under known torque. Later lessons will study output limits and observation errors before moving to coupled joints.

## Optional: run the experiment yourself {#local-experiment}

Run these commands from the repository root to generate a report and open the local CPU experiment:

```bash
python -m pip install -r requirements-interactive.txt
python -m synthetic.l1_servo_loaded_pendulum --output-dir reports/l1_servo_loaded_pendulum
python -m marimo run apps/l1_servo_loaded_pendulum.py --host 0.0.0.0 --port 2719
```

Change **Initial delay**, then write down your prediction. The app marks the settings as pending while the curves still show the previous result. Press **Run identification**, then compare the new initial model, identified model, and validation errors.

For further detail, read the [full experiment report](../../../reports/l1_servo_loaded_pendulum/report.md), open the [supplementary notes and code links](README.md), or download the [notebook](../../../notebooks/l1_servo_loaded_pendulum.ipynb).
