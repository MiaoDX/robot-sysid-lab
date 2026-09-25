# L6 · From structural mismatch to a true cross-engine test

A Student model may never contain the Oracle exactly. The final lesson asks what success means then: first isolate one structural mismatch in the primary backend, then compare the same small plant across genuinely different physics engines.

Completing only the first case is not the full L6. The cross-engine case is part of the agreed scope, but it is not a hardware result.

## A model can be useful without being exact {#failure}

If the Oracle includes an actuator effect that the Student cannot represent, the fit may find an effective compromise. The residual can remain structured even after optimization succeeds. A second simulator can add integration, contact, or convention differences that are not reducible to one parameter.

Predict what should be aligned before attributing a cross-engine difference to physics.

## Declare the small-plant interface {#boundary}

Return to one verified single-joint plant and its public interface:

```text
commands → declared plant boundary → motion observations
```

**Case A, structural mismatch:** keep the primary backend, make the Oracle actuator richer, and restrict the Student by removing one declared effect.

**Case B, cross-engine mismatch:** use the same small task in a second physics engine. Align units, frames, command timing, initial state, observation semantics, and comparable model assumptions before comparing predictions.

Internal forces, hidden states, and backend solver details remain diagnostic-only. Do not start with cross-engine fitting of a whole humanoid.

## Run the two mismatch cases {#comparison}

For Case A, remove one effect at a time, fit in one operating range, and withhold frequencies, loads, or motion families. For Case B, freeze the public task and interface, reproduce the same fit/evaluation split where semantics allow it, and document what cannot align.

Both cases require timestep refinement. If the conclusion changes with the step, separate numerical error from model-class error before widening the Student.

## Read mismatch evidence {#evidence}

Show the model/parameter semantics table, residual structure, timestep-refinement error, cross-condition error matrix, prediction horizon, and operating envelope. Report recovery only for parameters whose meaning is shared. For the second engine, avoid claiming that all remaining error belongs to one physical mechanism.

A useful final claim has the form: “Under these inputs, observations, and backend alignment rules, the Student predicts within this range; outside it, the residual pattern requires a richer model, a better experiment, or a narrower use envelope.”

## Think it through {#exercise}

Case A leaves a frequency-dependent residual. Case B adds a second engine and shows a different residual near the same frequency, but its timestep refinement is incomplete. Should you expand the Student now?

<details markdown="1">
<summary>Read a suggested answer</summary>

Complete the timestep refinement and interface checks first. The cross-engine difference may include numerical error or semantic misalignment. If the residual survives those checks, decide among a richer Student, a new excitation, or a narrower operating envelope. Do not use cross-engine error as a direct estimate of real-world uncertainty.
</details>

## What cross-engine evidence cannot prove {#limits}

A successful cross-engine prediction does not establish hardware transfer, universal robustness, or a unique physical parameter set. The second engine remains a separate implementation choice to freeze during individual review. L5 is not a prerequisite; K8 returns as the final uncertainty and downstream-transfer lens.

The synthetic ladder ends here. Hardware H0–H2 remains outside this rollout and requires its own platform-specific contracts.
