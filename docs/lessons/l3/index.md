# L3 · Add contact after validating free space

A foot can fit free-space motion and still fail when it presses or lands. This lesson adds only a normal contact effect and asks whether the contact evidence is enough to explain the new residual without damaging the upstream model.

Tangential friction, slip, and unknown terrain are separate future questions.

## Contact can expose an upstream error {#failure}

Suppose a leg's contact trajectory is wrong. Changing link mass may improve the force trace while making free-space prediction worse. Before fitting contact parameters, rerun the L2 free-space cases and check the contact event timing.

Predict which part of a pressing or release motion should reveal stiffness and which should reveal damping. A single static compression may not separate them.

## Declare the normal-contact boundary {#boundary}

Reuse the validated leg:

```text
joint commands → validated actuator/body model → normal contact law → motion and declared normal force
```

The first contact law is a fixed-geometry compliant normal model. The Student may fit a normal stiffness/damping pair only if the chosen motions separate them. Contact-solver internals, exact penetration, and hidden forces remain diagnostic-only unless explicitly declared.

The contact law, integration step, force sampling, and ground geometry must be frozen before fitting. These numerical choices affect what a fitted contact parameter means.

## Add one contact condition at a time {#comparison}

Use controlled compression/release or light-landing motions:

1. fit on one declared speed/load range;
2. withhold another approach speed or load;
3. refit only the declared normal-contact parameters;
4. rerun the original free-space validation.

Timestep refinement is a numerical check, not a new fitted parameter. If changing the step changes the conclusion, report a numerical limitation before interpreting stiffness or damping.

## Read contact evidence {#evidence}

This is a planned contact experiment contract. The listed traces and regression table are required outputs, not measured results on this page.

The evidence package should show contact onset, force–compression and force–velocity views, motion and force residuals, held-out behavior, and a free-space regression table. If penetration is not observable to the Student, show it only as an Oracle diagnostic.

Separate the questions: did contact start at the right time, did the force response have the right magnitude, and did the leg motion remain consistent? One aggregate score can hide a failure in one of these stages.

## Think it through {#exercise}

A single slow compression fits well, but a faster release has a large force residual. The free-space regression still passes. What should the next experiment change, and why is changing link mass an invalid shortcut?

<details markdown="1">
<summary>Read a suggested answer</summary>

Change approach/release speed and collect a condition that makes velocity-dependent damping visible, while keeping geometry and free-space parameters fixed. Link mass belongs to the upstream rigid-body model; changing it to fix contact would spend free-space evidence on a contact error and change the meaning of the fitted result.
</details>

The common wrong turn is to change link parameters because they are already available. If you cannot choose, inspect contact onset and free-space regression first, then vary release speed while holding the upstream model fixed. Continue when contact and free-space claims remain separate.

## What this contact lesson cannot prove {#limits}

It does not identify tangential friction, slip, unknown terrain, foot geometry, or every contact parameter at once. Contact values may be effective properties of the chosen backend and timestep. If stiffness and damping remain correlated, report a combination or range.

L4 carries the bounded free-space/contact evidence into the Microduck whole-robot comparison. Continue to [L4 · Compare whole-robot fitting routes](../course-design.md#l4).
