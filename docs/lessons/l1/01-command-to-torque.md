# L1 · From command to delayed torque

A position command specifies where the joint should go. To make it move,
the controller calculates torque from the current position error and velocity.
Here we use a fixed PD controller:

$$
c_k = k_p\left(q^{des}_k-q_k\right)-k_d\,\dot q_k,
\qquad \tau_k = \operatorname{delay}(c)_k.
$$

The command delay is inserted **after the controller calculates torque and before
that torque reaches the arm**. The command buffer stores
the already-computed torque command `c`, not the position target. The delay
selects/interpolates that buffer at `delay_s`; before the first recorded command
the history is zero. Oracle and Student share fixed controller gains and
integration settings.
Moving the delay to the encoder, to the position command before the controller,
or to a torque sensor would define a different lesson.

Why can a CAD or controller model still predict the wrong motion? A CAD model
can have the right arm mass and gravity while assuming an instantaneous command
path. A controller model can have the right gains while omitting transport
delay introduced by firmware, communication, scheduling, or a sampled command
interface. At low frequency the mismatch may be subtle. As frequency rises,
the same delay shifts the torque and therefore the angle in phase.

L1 keeps the body and controller parameters known so that residual evidence has
one intended explanation. The delay should be described as an **effective,
boundary-dependent timing parameter**. It should not be reported as a physical
motor constant or used to claim electromagnetic identification.

## Fit and validation inputs

The fit uses a chirp whose frequency increases over time. The held-out
validation input uses a separately defined reversal waveform with a different
phase/frequency composition, and each split resets the same initial state. The
Student sees fit observations only. Validation is a prediction test, not
another optimization call. Encoder position is ideal in this lesson; public
`qd` is derived by finite differences of that position, not the hidden
integration velocity.

## Checkpoint

If the initial model has zero delay but the Oracle has positive delay, which
quantity should show a phase clue first: the static arm geometry, the target
command, or the torque/angle response? The response is the torque/angle path.
The static schematic is a state snapshot; it does not show the hidden command
buffer.
