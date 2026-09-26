# 4. Exercise, limits, and the bridge to L2

Before fitting, make one prediction. In the guided app, change the Initial
delay slider away from zero , observe the pending setup, and write down what you expect to change:

1. Moving the Initial delay toward the Oracle's effective delay should bring
   the orange response closer; moving it farther away should generally enlarge
   the mismatch. The response is a delayed feedback loop, so large delays can
   also change damping and stability.
2. A higher-frequency command should make the same time delay occupy more of a
   cycle, making phase mismatch easier to see.
3. The blue Identified result should remain the previous completed fit until
   **Run identification** is pressed.

Run the fit only after making the prediction. Then compare the new fit and
validation metrics. Presentation controls such as timeline position or signal
selection are replay controls and should not launch fitting.

## What this lesson leaves out

L1 deliberately introduces one hidden actuator effect. It omits torque scale or
bias, saturation and velocity limits, Coulomb/Stribeck/asymmetric friction,
compliance and backlash, reflected motor inertia, voltage and temperature,
sensor noise/filtering/quantization, contact, payload shifts, and whole-robot
dynamics. It also does not use CAD assets, MuJoCo/MJLab, hardware collection,
or a motor-electromagnetic model. A fitted delay therefore does not establish
hardware transfer; it predicts this declared synthetic boundary.

The next actuator bridge adds friction and saturation only when their residual
signatures are useful. The following structural lesson is a fixed-base leg,
where gravity and joint coupling become the new questions. Keeping one new
effect per lesson makes it possible to tell whether a failure came from
excitation, identifiability, estimator convergence, or model structure.

## Final checkpoint

State the L1 conclusion in one sentence:

> For this fixed-base, gravity-loaded pendulum and declared `q_des -> PD ->
> delay -> torque` boundary, public position and derived-velocity observations
> can recover an effective command delay and improve held-out prediction; that
> conclusion is bounded by the synthetic ideal assumptions and does not claim
> motor or hardware identification.
