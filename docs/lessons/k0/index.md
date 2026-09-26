# K0 · Why system identification matters

A robot moves smoothly in simulation, then lags behind its commands or keeps oscillating on hardware. When this happens, we need to understand which parts of the model are inaccurate and what evidence would help us improve them.

System identification uses experimental data to build and improve models. We will start with one rotating joint, see why a plausible model can make poor predictions, and learn how to check whether a change has helped.

## One input, two different motions {#mismatch}

Imagine applying a time-varying torque to a joint while a model predicts its position and velocity. If the model has inaccurate inertia or damping, its predicted motion will drift away from the observations.

The clip below shows this happening. White represents the system being studied; orange represents our initial model. Both receive the same torque, and the velocity bars use the same scale.

<figure class="clip"><video controls="" playsinline="" poster="../../../demos/manim/rendered/l0-mismatch.png" preload="metadata"><source src="../../../demos/manim/rendered/l0-mismatch.mp4" type="video/mp4"/><track default="" kind="subtitles" label="English" src="../../site/subtitles/l0-mismatch.en.vtt" srclang="en"/><track kind="subtitles" label="中文" src="../../site/subtitles/l0-mismatch.zh-CN.vtt" srclang="zh-CN"/></video><figcaption>What does the mismatch look like?</figcaption><details><summary>Read the video explanation</summary><p>One equation: J qdd + b qd = u. Compare the True system and Initial model.</p><p>The same applied torque drives both systems. White is truth; orange is the Initial model.</p><p>The velocity meters share a scale. Incorrect damping produces a visibly different response.</p></details></figure>

For this experiment, the system being studied is simulated too. We know its true parameters and can check the answer after identification. The estimator gets only the experimental data. Later lessons will extend the method to hardware.

## What a drawing can tell us {#model}

Drawings and CAD models describe geometry, dimensions, and estimated mass distribution. Joint motion also depends on friction, control, command delay, and changing loads. Some of these properties require measurements; some vary with operating conditions.

A plausible model can therefore make inaccurate predictions. System identification tests the model against recorded inputs and motion, then estimates uncertain quantities. In our joint example, those quantities are inertia and damping.

## Learning from an experiment {#experiment}

Start with a question, such as how strongly the joint resists acceleration and how much energy it loses while moving. Apply a known torque and record its motion.

Then adjust the model parameters so that its predictions under the same input approach the recorded observations. This is **fitting**. The experiment matters too: slow motion at constant speed tells us little about how inertia affects acceleration.

After fitting, test the model on a motion that was withheld from tuning. This is **validation**. It checks whether the model learned behavior that helps it predict a new motion.

## Accurate parameters, predictions, and hardware behavior {#evidence}

These outcomes are related, but each needs its own evidence.

**Parameter accuracy** needs a reliable reference. In a synthetic experiment we know the true values. On hardware, independent measurements may be needed to establish whether a fitted value represents a particular physical quantity.

**Prediction accuracy** needs new experimental data. A model may predict well over a limited range even when individual parameters are difficult to determine. It may also match one trajectory and fail on another.

**Better control or policy behavior on hardware** needs a separate hardware evaluation. Better model predictions provide a stronger starting point for that evaluation.

In L0, we will check parameters and motion predictions within a small experiment whose assumptions we can inspect.

## Think it through {#exercise}

Someone adjusts a model until it almost perfectly reproduces the motion used for fitting, then says, “The model can now predict the joint's motion.” What result would you ask to see next?

<details markdown="1">
<summary>Read a suggested answer</summary>

Ask for a motion withheld from fitting. Choose input changes that test the properties of interest, such as a different set of frequencies or amplitudes. Compare prediction errors before and after identification, and describe the conditions under which the model works.

If the validation result is then used to tune the model, that data becomes part of development. A fresh independent check needs another reserved dataset.

</details>

## Continue to the next lesson {#next}

Our goal is to predict a system's motion from its input. [K1 · System identification fundamentals](../k1/index.md) introduces inputs, states, observations, and parameters so that we can describe the first experiment precisely.
