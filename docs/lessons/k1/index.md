# K1 · System identification fundamentals

The previous lesson explained why experimental data helps us improve a model. Now we can make the question precise: what input enters the system, what can we measure, and what do we want to estimate?

We will keep using a rotating joint. By the end, you should be able to sketch its input and observations, distinguish states from parameters, and explain why choosing a model differs from adjusting its parameters.

## Choose the system we want to study {#boundary}

Apply torque to a joint, then record its position and velocity:

<div class="signal-flow" role="img" aria-label="Known torque enters a rotating joint and produces observed position and velocity"><span>Known torque</span><span aria-hidden="true">→</span><strong>Rotating joint</strong><span aria-hidden="true">→</span><span>Position and velocity</span></div>

The **input** enters the system we are studying. **Observations** are the quantities we record. The physical processes included between them determine which model we need. Choosing those processes defines the system boundary.

Here we assume the applied torque is known. If we have only a target position command, we also need to describe how the controller turns it into torque. L1 will study that path. In L0, applied torque is already a known input.

## States, observations, and parameters {#quantities}

The joint's angle and speed change over time. They describe its current condition and are called **states**. Data provided by sensors or a recorder are **observations**. They may cover only some states and may contain noise.

**Parameters** describe relatively fixed properties of a model. In the first experiment, inertia and damping stay constant during a run. We will estimate them from the input and motion data.

| Quantity | Rotating-joint example | Role in the experiment |
|---|---|---|
| Input | Applied torque $u$ | Drives the motion |
| State | Angle $q$ and angular velocity $\dot q$ | Describes the current motion |
| Observation | Recorded position and velocity | Lets us compare predictions with the experiment |
| Parameter | Inertia $J$ and viscous damping $b$ | Determines the response to an input |

L0 observes position and velocity perfectly, so the state and observation values agree. On hardware, measured position may be noisy and velocity may need to be calculated from position changes.

## Connect the quantities with an equation {#equation}

L0 uses this model:

$$
J\ddot q+b\dot q=u
$$

$\ddot q$ is angular acceleration: how quickly angular velocity changes. $J\ddot q$ describes the torque needed to accelerate; $b\dot q$ describes viscous resistance during motion. Given the input $u$ and an initial state, the model predicts how the joint will move.

Greater inertia means less acceleration for the same net torque. Greater viscous damping means more resistance at the same speed. Identification estimates $J$ and $b$ from the relationships these quantities reveal during an experiment.

## Choose a model, then estimate its parameters {#structure}

Writing that equation already makes a choice: the model includes inertia and viscous damping. Deciding which effects to include is **model structure selection**. Finding suitable values of $J$ and $b$ within that structure is **parameter estimation**.

If the actual system also has appreciable delay, changing only inertia and damping may improve some motions while leaving others inaccurate. We need to inspect the experiment and its errors to decide whether the model should include delay. More optimization effort cannot guarantee a remedy for a missing effect.

In the first experiment, the system generating the data and the model being fitted use the same equation. This lets us understand parameter estimation before studying incomplete models.

## Read the three model curves {#models}

The **true system** produces the observations we want to explain. In a synthetic experiment, a simulator with known parameters plays this role. Videos and reports label it *True system* or *Oracle*.

The **initial model** uses our parameter guesses before identification. The **identified model** uses values estimated from the experimental data. Comparing their predictions shows what identification changed.

True parameters let us check the result. The fitting program receives inputs and observations, together with the model and parameter bounds chosen beforehand.

## Think it through {#exercise}

You have recorded applied torque, joint position, and velocity, but do not yet know inertia or damping. Identify the input, observations, and unknown parameters. Would a position measurement at just one instant determine both parameters?

<details markdown="1">
<summary>Read a suggested answer</summary>

Torque is the input. The position and velocity time series are the observations. Inertia and damping are the unknown parameters.

A single position usually cannot determine them. Different parameter values and motion histories can pass through the same position. We need a motion with suitable acceleration and deceleration to reveal how the parameters affect the response.

</details>

The common wrong turn is to call a single position a dataset. If you are stuck, write the time-varying input and observation columns first, then mark which quantities are unknown. Continue when you can draw the boundary without using the true parameters.

## Start the first experiment {#next}

Continue to [L0 · Estimate joint inertia and damping](../l0/index.md). We will start with an inaccurate model, fit its parameters, and check its predictions on a new motion.

The [system identification reference notes](../../01_sysid_101.md) collect additional terminology. Later lessons will introduce these ideas through specific experiments.
