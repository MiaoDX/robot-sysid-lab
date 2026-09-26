# Course delivery status

This page is the delivery ledger for the 19 K/L lesson IDs. It separates the
reading or concept page from usable numerical evidence and from teaching media.
A published page is not automatically a runnable experiment or a video lecture.
The shared rules are in the [lesson delivery policy](../lesson_delivery_policy.md).

## Evidence and media matrix {#evidence-media-matrix}

`Available` means that the linked artifact is checked in and usable for the
named question. `Planned` means the question is useful but its run or render is
not complete. `Not needed` means a static derivation or compact figure carries
the question more clearly; the reason is stated in the row.

| ID | Page class | Usable evidence | Video status and named question |
|---|---|---|---|
| [K0](../lessons/k0/index.md) | Concept + cited lab | [L0 mismatch report](../../reports/l0_inertia_damping/report.md) and replayed mismatch clip | **Available · 1:** [l0-mismatch.mp4](../../demos/manim/rendered/l0-mismatch.mp4), reused for “what does a bad model look like?” |
| [K1](../lessons/k1/index.md) | Reading | Signal and parameter explanation on page | **Not needed:** the boundary table and exercise are shorter and clearer as static text |
| [K2](../lessons/k2/index.md) | Concept | [Labelled pendulum diagram](../lessons/k2/assets/pendulum-boundary.svg) and [analytic decomposition](../lessons/k2/assets/torque-residual-illustrative.png); explicitly illustrative | **Not needed:** a static derivation and figure answer the units/force-balance exercise; no experiment evidence is implied |
| [K3](../lessons/k3/index.md) | Concept + cited L1 | [L1 friction report](../../reports/l1_friction/report.md) and L1 boundary evidence | **Available · 3 reused:** [l1-boundary.mp4](../../demos/manim/rendered/l1-boundary.mp4), [l1-phase.mp4](../../demos/manim/rendered/l1-phase.mp4), [l1-friction.mp4](../../demos/manim/rendered/l1-friction.mp4) for command delay and resisting torque |
| [K4](../lessons/k4/index.md) | Concept + L0-E evidence | [L0-E report](../../reports/l0_excitation/report.md) and sensitivity/coverage figures | **Available · 1 reused:** [l0-excitation.mp4](../../demos/manim/rendered/l0-excitation.mp4) for the excitation comparison |
| [K5](../lessons/k5/index.md) | Concept + L0 evidence | [L0 report](../../reports/l0_inertia_damping/report.md), fit path and multi-start metrics | **Available · 1 reused:** [l0-fit-walk.mp4](../../demos/manim/rendered/l0-fit-walk.mp4) for how an optimizer path changes the model |
| [K6](../lessons/k6/index.md) | Concept + held-out evidence | [L0 report](../../reports/l0_inertia_damping/report.md), fit/held-out split and residuals | **Available · 1 reused:** [l0-heldout.mp4](../../demos/manim/rendered/l0-heldout.mp4) for a prediction on a withheld motion |
| [K7](../lessons/k7/index.md) | Concept + cited friction evidence | [L1 friction report](../../reports/l1_friction/report.md), with effective-parameter limits | **Not needed:** the report figure and comparison table carry the compensation question; no extra clip is required |
| [K8](../lessons/k8/index.md) | Concept | Control/transfer protocol and answer guide on page | **Not needed:** the bounded protocol is a static design decision; downstream robot evidence is planned with L4 |
| [L0](../lessons/l0/index.md) | Runnable | [L0 fixed report](../../reports/l0_inertia_damping/report.md), metrics and local runner | **Available · 5:** [mismatch](../../demos/manim/rendered/l0-mismatch.mp4), [fit lands](../../demos/manim/rendered/l0-fit-lands.mp4), [fit walk](../../demos/manim/rendered/l0-fit-walk.mp4), [robust starts](../../demos/manim/rendered/l0-fit-robust.mp4), [held-out](../../demos/manim/rendered/l0-heldout.mp4) |
| [L0-E](../lessons/l0-e/index.md) | Runnable | [L0-E frozen report](../../reports/l0_excitation/report.md), sensitivity/coverage/loss/multistart/held-out outputs | **Available · 1:** [l0-excitation.mp4](../../demos/manim/rendered/l0-excitation.mp4) for weak excitation and comparison |
| [L1](../lessons/l1/index.md) | Runnable | [L1 report](../../reports/l1_servo_loaded_pendulum/report.md) plus [friction report](../../reports/l1_friction/report.md) | **Available · 4:** [boundary](../../demos/manim/rendered/l1-boundary.mp4), [phase](../../demos/manim/rendered/l1-phase.mp4), [held-out](../../demos/manim/rendered/l1-heldout.mp4), [friction](../../demos/manim/rendered/l1-friction.mp4) |
| [L1-O](../lessons/l1-o/index.md) | Design draft | Contract and planned observation-noise comparison on page; no checked run | **Planned:** observation noise has a named residual question, but no rendered clip or report yet |
| [L1-S](../lessons/l1-s/index.md) | Design draft | Contract and planned saturation comparison on page; no checked run | **Planned:** saturation would benefit from a clip once its local run exists |
| [L2](../lessons/l2/index.md) | Design draft | Coupled-leg contract; simulator/report pending | **Planned:** coupling and parameter compensation need a real leg run before a clip is made |
| [L3](../lessons/l3/index.md) | Design draft | Contact contract; simulator/report pending | **Planned:** contact onset and residuals need a real run |
| [L4](../lessons/l4/index.md) | Design draft | Whole-robot/control-comparison contract; report pending | **Planned:** component/global route and bounded controller comparison need checked evidence |
| [L5](../lessons/l5/index.md) | Design draft | Parameter-sharing contract; report pending | **Planned:** comparing independent and shared parameters needs the actual scaling run before a clip can be made |
| [L6](../lessons/l6/index.md) | Design draft | Structural-mismatch and cross-engine contract; reports pending | **Planned:** two mismatch cases require actual backend runs before media can be scoped |

The ten independent current clips are short, silent teaching aids; subtitles
and written explanations carry the language-specific narrative. Reused clips
are counted in each lesson only when their question and boundary are stated.
L1-O, L1-S, and L2–L6 remain design drafts; independent learner acceptance for
L0/L1 and the full course is still pending.

## Current delivered path

K0, K1, L0 and L1 are readable today. L0 and L1 have reproducible local CPU
runners and checked reports; L1 includes the isolated friction extension. L0-E
is now a runnable CPU evidence package. K2 is a concept lesson with a derivation
and analytic teaching figure, explicitly separate from experiment evidence.
K3–K8 cite the evidence that answers their questions or state why a clip is not
needed. The remaining L pages are contracts awaiting their numerical paths.

The website provides paired English and Chinese pages. Marimo apps remain local
adapters; a browser/WASM surface is optional and is never inferred from page
publication. Independent learner acceptance still requires an actual reader to
identify the initial mismatch, explain held-out performance, change one setting,
and state the assumptions.
