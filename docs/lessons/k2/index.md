# K2 · Locate dynamics terms from motion errors

A model can work at one posture and fail after the robot moves. This lesson gives you a practical way to connect a residual pattern to candidate dynamics terms without pretending that one curve identifies one cause.

The equation is a map for asking questions. It is not a promise that every mass, center of mass, or inertia can be recovered from one experiment.

## The same fit does not work everywhere {#failure}

Imagine a joint model that predicts a supported arm well near one angle but misses when the arm moves through another angle. A tempting response is to change inertia until the new curve overlaps. Before doing that, ask whether the mismatch changes with position, velocity, acceleration, or contact.

Predict the pattern for a missing gravity term. Then predict the pattern for an underestimated inertia. They may both create a position error, but they should respond differently to posture and acceleration.

## Draw the plant boundary and terms {#boundary}

For a robot mechanism, a useful dynamics boundary is

$$
M(q)\ddot q + C(q,\dot q)\dot q + g(q) + \tau_f = \tau + J_c^T\lambda.
$$

Here $M$ describes inertia, $C\dot q$ collects velocity-dependent coupling, $g$ is gravity, $\tau_f$ represents friction or other dissipation, and $J_c^T\lambda$ is the generalized force from contact. The applied actuator torque $\tau$ is on the input side only if the actuator boundary makes it observable or known.

The terms have different dependencies:

| Candidate term | Strongest clues | Useful change |
|---|---|---|
| Inertia | acceleration and frequency | change acceleration while holding posture |
| Gravity | posture and direction | repeat a motion at different angles |
| Coupling | another joint's motion | excite one joint and observe the other |
| Friction | speed and direction, especially reversals | repeat at several speeds and directions |
| Contact | contact event and load | compare free space with controlled contact |

A clue narrows hypotheses; it does not choose one automatically.

## Use controlled changes to separate terms {#comparison}

Keep the mechanism, controller, and observation process fixed. Change one condition at a time:

1. hold posture near fixed and vary acceleration to expose inertia;
2. repeat the motion in another orientation to expose gravity;
3. excite one joint while holding or moving the other to expose coupling;
4. compare free-space and contact motions only after free-space evidence is acceptable.

A complete rigid-body equation is not a license to fit every term at once. A Student model should contain only the parameters the data can support. When several terms move together, report a parameter combination or design a new experiment.

## Read term decompositions and residuals {#evidence}

A useful teaching figure shows the candidate torque terms on the same time axis as the residual. Read it in this order:

- Is the term large in the condition where the residual appears?
- Does changing the relevant condition change the residual in the predicted direction?
- Does the same adjustment damage a condition that previously passed?
- Is the term actually visible to the fitter, or is it only an Oracle diagnostic?

Term decompositions explain a simulated truth. They are not observations the Student may use unless the lesson explicitly declares them available. In L2, hidden true link parameters and internal forces remain evaluation or diagnostic signals.

## Think it through {#exercise}

A two-joint leg has a residual on joint 2 that grows when joint 1 accelerates. The same residual is small when joint 1 moves slowly. Which candidate would you test first, and what follow-up motion would distinguish coupling from an actuator delay?

<details markdown="1">
<summary>Read a suggested answer</summary>

Test a coupling or acceleration-dependent hypothesis first, because the residual follows the other joint's acceleration. Repeat the motion with the same command timing but different joint-1 acceleration profiles, and compare a synchronized phase or frequency view. If the residual follows timing relative to the command even when acceleration is changed, delay remains plausible. If it follows the coupled motion across timing changes, coupling is better supported.
</details>

## What this equation cannot tell us {#limits}

The equation organizes hypotheses; it does not guarantee practical identifiability. Contact, actuator, geometry, and observation errors can compensate for one another. A fit that improves one posture may be an effective model rather than a recovered physical parameter set.

K3 narrows the boundary around command-to-torque effects. L2 later uses posture and coupling changes in a fixed-base leg. Continue to [K3 · Trace commands to joint torque](../k3/index.md).
