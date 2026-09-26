# K2 · Locate dynamics terms from motion errors

A model can work at one posture and fail after the robot moves. Start there: look at the residual and predict which change in the motion should make it larger or smaller. This lesson gives you a practical way to connect that pattern to candidate dynamics terms without pretending that one curve identifies one cause.

The equation is a map for asking questions. It is not a promise that every mass, center of mass, or inertia can be recovered from one experiment.

In this page, **Student** means the model being fitted and **Oracle** means the system that generated the reference motion. A **diagnostic signal** is available to the Oracle or the explanation, but is hidden from the Student's fitting objective.

## The same fit does not work everywhere {#failure}

Imagine a joint model that predicts a supported arm well near one angle but misses when the arm moves through another angle. Before changing a parameter, you predict: should the residual change with position, velocity, acceleration, or contact? A tempting response is to change inertia until the new curve overlaps, but that move spends evidence before we know what changed.

Predict the pattern for a missing gravity term. Then predict the pattern for an underestimated inertia. They may both create a position error, but they should respond differently to posture and acceleration.

## Draw the plant boundary and terms {#boundary}

For a robot mechanism, draw the boundary before choosing a parameter. A useful dynamics boundary is

$$
M(q)\ddot q + C(q,\dot q)\dot q + g(q) + \tau_f = \tau + J_c^T\lambda.
$$

Here $M$ describes inertia, $C\dot q$ collects velocity-dependent coupling, $g$ is gravity, $\tau_f$ represents friction or other dissipation, and $J_c^T\lambda$ is the generalized force from contact. The applied actuator torque $\tau$ is on the input side only if the actuator boundary makes it observable or known.

![Illustrative single-joint pendulum boundary: angle, gravity, applied torque, and moment balance. This conceptual diagram is not experiment evidence.](assets/pendulum-boundary.svg)

For the one-joint sketch, the gravity term follows from the height $h=\ell(1-\cos q)$: $U=mgh$ and $\partial U/\partial q=mg\ell\sin q$. With viscous dissipation $\tau_f=b\dot q$, the balance is

$$J\ddot q=\tau-b\dot q-mg\ell\sin q.$$

The units provide a quick check: $J$ is kg·m², $\ddot q$ is rad/s², and every term on both sides is N·m (radians are dimensionless). Define a torque residual as $\varepsilon=\tau_{\mathrm{model}}-\tau_{\mathrm{reference}}$, evaluated along the same declared motion. This is a torque-balance diagnostic, unlike the trajectory residuals in L0. The decomposition is illustrative here; no observations or fitted result are being claimed.

The following plot uses $q(t)=0.45\sin(1.3t)$ rad, $J=0.8$ kg·m², $b=0.12$ N·m·s/rad and $mg\ell=1.4$ N·m. Derivatives are analytic. The dashed residual is a declared placeholder $0.18\sin(0.9t+0.4)|\dot q|/0.585$ N·m; it was chosen for reading practice and is not attributed to a physical cause. Reproduce the illustration with `python docs/lessons/k2/assets/generate_concept_figures.py`. It is **illustrative, not a recorded experiment**.

![Illustrative analytic torque decomposition and residual. The trajectory and placeholder residual are generated from the equation above; no simulator or report produced these curves.](assets/torque-residual-illustrative.png)

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

A complete rigid-body equation is not a license to fit every term at once. Keep the mechanism, controller, observation process, and fitting budget fixed while you change one declared condition. A Student model should contain only the parameters the data can support. When several terms move together, report a parameter combination or design a new experiment.

## Read term decompositions and residuals {#evidence}

A useful **conceptual or diagnostic** figure shows the candidate torque terms on the same time axis as the residual. It is diagnostic when the terms come from the Oracle; it is Student-visible only when the lesson declares them as observations. Read it in this order:

- Is the term large in the condition where the residual appears?
- Does changing the relevant condition change the residual in the predicted direction?
- Does the same adjustment damage a condition that previously passed?
- Is the term actually visible to the fitter, or is it only an Oracle diagnostic?

Term decompositions explain a simulated truth. They are not observations the Student may use unless the lesson explicitly declares them available. In L2, hidden true link parameters and internal forces remain evaluation or diagnostic signals.

## Think it through {#exercise}

First read the supplied figure: near $t=1.2$ s, the angle reaches a turning point. Which torque term is near zero, and why can the other two remain large? Can the dashed curve prove a missing coupling term?

Then consider a two-joint leg that has a residual on joint 2 that grows when joint 1 accelerates. The same residual is small when joint 1 moves slowly. Which candidate would you test first, and what follow-up motion would distinguish coupling from an actuator delay?

Use the conceptual figure above as a check: the coloured curves show how terms have different phase but the same torque units, but they do not identify a hidden cause by themselves. In the sketch, the exercise answer should name the signal that changes, the term it makes plausible, and the one controlled comparison that would make the alternatives disagree.

<details markdown="1">
<summary>Read a suggested answer</summary>

At the turning point, velocity is zero, so viscous resistance $b\dot q$ is near zero. Acceleration and the nonzero angle leave inertia and gravity appreciable. The dashed curve was chosen analytically, so it proves no missing physics.

For the two-joint scenario, test a coupling or acceleration-dependent hypothesis first, because the residual follows the other joint's acceleration. Repeat the motion with the same command timing but different joint-1 acceleration profiles, and compare a synchronized phase or frequency view. If the residual follows timing relative to the command even when acceleration is changed, delay remains plausible. If it follows the coupled motion across timing changes, coupling is better supported.
</details>

If you cannot decide, first align the residual with joint 1 acceleration and then repeat the comparison after changing only its acceleration profile. Continue when you can state which observation would make delay and coupling disagree; a lower residual on one run is not enough.

## What this equation cannot tell us {#limits}

The equation organizes hypotheses; it does not guarantee practical identifiability. Contact, actuator, geometry, and observation errors can compensate for one another. A fit that improves one posture may be an effective model rather than a recovered physical parameter set.

K3 narrows the boundary around command-to-torque effects. L2 later uses posture and coupling changes in a fixed-base leg. Continue to [K3 · Trace commands to joint torque](../k3/index.md).
