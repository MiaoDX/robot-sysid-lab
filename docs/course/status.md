# Course delivery status

This page distinguishes available lessons from curriculum proposals. The [course design](../lessons/course-design.md) describes the complete learning path.

## Available to read and run

K0 and K1 have independent English and Chinese lessons introducing motivation and fundamentals.

L0 inertia/damping and L1 command delay have static lessons, teaching videos, lesson notes, local Marimo apps, notebooks, numerical runners, and fixed reports. L1 now also contains a second isolated friction-versus-viscous-damping experiment with a frozen local CPU runner, report, and notebook; no separate browser surface is planned for this extension. The website provides English and Chinese reading pages with a language switch. Existing lessons use the same numerical configuration and evidence.

The interactive Marimo apps are local Python applications. Their deployment and browser execution are separate from this static reading site. A self-contained WASM export remains planned.

## Acceptance still open

Engineering verification exists for both lessons. Independent learner acceptance remains open: an actual reader must identify the initial mismatch, explain held-out performance, change one setting, and state the assumptions. Translating a page or passing automated checks does not supply this learner evidence.

## Planned lessons

Knowledge chapters K2–K8 are still in preparation. L0-E and additional L1 actuator effects such as saturation and observation quality remain proposals; the friction extension is implemented inside L1 and still needs maintainer learner acceptance. L2–L6 cover a fixed-base leg, contact, Microduck, Microban, and simulator mismatch. H0–H2 apply the method to hardware. These remain design proposals unless linked to an implemented experiment.

## Next work

Record the maintainer learner walkthrough for L0/L1, including both the delay and friction sections, then decide whether the measured value justifies a browser surface. Use the [delivery policy](../lesson_delivery_policy.md) for static, browser, and local execution decisions.

The original [engineering status record](../../STATUS.md) contains historical commands, commits, and verification links.
