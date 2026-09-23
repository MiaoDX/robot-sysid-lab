# Lesson design for review

[中文版](course-design.zh-CN.md) · [Course map](../course/index.html) · [Existing lessons](README.md)

**Status: curriculum proposal, 2026-09-21.** This document turns the [roadmap](../03_synthetic_lab_roadmap.md) into teachable lessons. L0 and L1 already have implementations, notes, videos, and reports; independent learner acceptance remains open. All other lab cards below are proposals, not runnable lessons or measured results. [K0](k0/index.md) and [K1](k1/index.md) now have independent reading pages; other knowledge lessons remain in preparation.

English and Chinese versions share section and lesson IDs. Feedback can reference `D02`, `K4`, or the L1 friction extension without depending on a translation's paragraph numbers. The proposals here extend the L1 experiment contract without changing its public course level.

Review entry points: [sequence](#d02) · [page structure](#d03) · [knowledge chapters](#d04) · [lab cards](#d05) · [hardware](#d06) · [next steps](#d08).

<a id="d01"></a>
## D01 · What the learner should be able to do

The audience is a robotics engineer who can read plots and has basic Python experience. Reading the static lessons requires neither a GPU nor a simulator installation. Basic derivatives and feedback intuition are introduced when needed; optimization and rigid-body dynamics are not entry requirements.

By the end of the synthetic path, the learner should be able to:

1. Draw a plant boundary and distinguish a command, an applied torque, a state, and an observation.
2. Design an excitation that reveals a target effect and state which observations the estimator may use.
3. Distinguish an optimizer problem, an uninformative experiment, and an inadequate model using additional evidence.
4. Evaluate a fitted model on withheld conditions and bound the conclusion to those conditions.
5. Carry component evidence into a whole robot and distinguish parameter recovery, prediction, and control/RL transfer.

The recurring learner output is a short **evidence note**: “I expected …; this curve or metric shows …; the result supports … under …; the next experiment would be …”. Naming a fitted number alone does not complete a lesson.

<a id="d02"></a>
## D02 · Sequence and lesson boundaries

K chapters supply concepts when a lab needs them. Learners do not have to finish K0–K8 before opening L0. L0–L6 retain the meanings in the existing course map. Suffixes name smaller lessons inside a level; they do not renumber the ladder or rename existing files.

| Stage | Reading and lab sequence | New capability |
|---|---|---|
| First complete loop | K0 + K1 → L0 → introduction to K6 | Explain what fitting and held-out prediction establish |
| Make the experiment informative | K4 + essential K5 → L0-E | Recognize when changing the input helps more than changing the optimizer |
| Understand the actuator boundary | K3 + K7 → L1 → L1 extensions | Separate timing, friction, and output-limit hypotheses |
| Prepare realistic observations | L1-O, revisiting K4/K6 | Reason about measured position, derived velocity, and uncertainty |
| Add robot structure | K2 as needed → L2 → L3 | Separate actuator, rigid-body, and contact errors |
| Scale and challenge the model | L4 → L5 → L6; K8 alongside L4/L6 | Compare fitting strategies, parameter sharing, and model mismatch |
| Transfer to hardware | H0 → H1 → H2 when the corresponding subsystem is ready | Support conclusions with calibration and repeatable physical measurements |

L0-E is a return to the same tiny plant, not a new robot. L1's delay, friction, and saturation sections isolate their new effects instead of accumulating every previous imperfection. Combining effects is a later extension after the individual cases are understood.

Hardware is a branch of the course: H0 can begin after the actuator lessons and its bench procedure are ready. H1 requires the relevant whole-robot and contact evidence; H2 requires H1 and the platform-specific acquisition procedure. Completing every synthetic extension is not a prerequisite for a bench experiment.

**Planning estimates:** 10–15 minutes for a K chapter; 25–40 minutes for a small lab's narrative and exercise. L2–L6 should be split into reading/replay and a separate local assignment. These are lesson-length targets, not measured computation times.

<a id="d03"></a>
## D03 · A repeatable lesson page

| Step | Learner experience | Author must provide |
|---|---|---|
| 01 · Question and prediction | See a concrete mismatch; predict what will change | One question and an initial comparison |
| 02 · Boundary and intuition | Name the input, observations, unknowns, and fixed quantities | A signal-flow diagram, units, and only the equations needed here |
| 03 · Experiment | Explain why this input can reveal the unknown | Fit/validation conditions, resets, and estimator-visible signals |
| 04 · Evidence | Compare True system, Initial model, and Identified model | Side-by-side fit/validation views, residuals, and a supported conclusion |
| 05 · Exercise | Make one prediction, change one setting, interpret the outcome | A static evidence exercise plus optional bounded computation |
| 06 · Limits and next question | State where the conclusion stops applying | Omitted effects, an answer guide, and the next lesson link |

The homepage explains the learning value and recommends K0 → K1 → L0, while allowing direct entry to other available lessons. Future lessons show a learning objective and a “Coming later” label without placeholder body links. Curriculum and delivery documents sit behind a separate project-resources entry.

Write for learners using concrete questions and connected explanations. Omit unnecessary terminal periods in headings. Align concepts, data, and conclusions across languages while using natural phrasing in each.

Each learning question gets one continuous page. Chapter links support scrolling; a row of tabs must not hide the narrative. A teaching clip sits beside its question, with a caption explaining what to observe. Curves retain labels and line styles as well as the established colors.

Every exercise can start from fixed figures or recorded alternatives, so the static path remains useful. Interaction exposes only one or two controls that answer the question. Replay controls do not run fitting. A parameter edit must clearly distinguish the pending setup from a completed result.

Model selection is part of fitting: if validation feedback is used to choose a model, bounds, or hyperparameters, that split has become development data. Reserve a new untouched evaluation split before claiming final held-out performance. In teaching comparisons, predeclare the candidate models and comparison axes before revealing validation outcomes.

<a id="d04"></a>
## D04 · Knowledge chapters

The table describes the goals of independent knowledge lessons. K0 and K1 have reading pages; the other chapters are in preparation and can draw on existing notes.

| ID | Main question | Visual anchor and learner task | Lab connection |
|---|---|---|---|
| K0 | Why does a plausible robot model still fail? | Compare before/after trajectories; distinguish parameter, prediction, and transfer claims | L0 introduction; revisit in L4 |
| K1 | What exactly is being identified? | Annotate an input → plant → observation diagram; separate state, parameter, and measurement | L0 boundary; L1 command path |
| K2 | Which dynamics term could explain this behavior? | Show inertia, gravity, coupling, and contact on a leg; predict the effect of a posture change | Minimal inertia in L0; gravity in L1; full treatment in L2/L3 |
| K3 | What lies between a command and joint torque? | Walk through a model ladder; locate delay, friction, and saturation at their declared boundaries | L1 and its extensions |
| K4 | Did the experiment reveal enough information? | Compare input coverage and loss contours; select an excitation that separates two parameters | L0-E; revisit in L2 |
| K5 | What does an optimizer's answer establish? | Follow a least-squares cost surface and several starts; choose a diagnostic for failed fitting | L0 and L0-E; population methods become optional in L4 |
| K6 | What evidence would challenge this fitted model? | Compare withheld-motion predictions and residuals; design a condition not used in fitting | L0 onward; develop the full chapter with L1 |
| K7 | Is the fitted value a physical quantity? | Contrast physical, effective, and nuisance parameters; state the interpretation and remaining uncertainty | L1 effective delay; L2 compensation; L6 mismatch |
| K8 | How does identification help control or RL? | Draw collection → frozen data → fit → new controller/policy → evaluation; propose targeted randomization | L4/L6 extension and hardware transfer |

K5 begins with the estimator used by L0. CMA-ES, Bayesian optimization, differentiable simulation, and optimizer comparisons are later options, introduced when a lab exposes a concrete need. References live in the [learning path](../02_learning_path_and_references.md).

<a id="d05"></a>
## D05 · Synthetic lesson cards

Unless a card says otherwise, Oracle truth is available only to the generator/evaluator, candidate Students use the same public fitting data, and validation is a separate run with declared initial conditions. “Evidence” below names what a future run must produce, not a result already observed. Numerical bounds, tolerances, and execution budgets must be frozen in each implementation plan.

<a id="l0"></a>
### L0 · Recover inertia and damping

- **Question / prerequisite:** Can two unknowns explain motion under a known torque and predict another input? K0/K1 are enough to start.
- **Boundary:** `J*qdd + b*qd = u`; applied torque is known; public observations are `t/u/q/qd`. Only `J` and `b` are fitted. Oracle and Student share the equation, with ideal observations.
- **Experiment:** Fit a chirp, then predict the fixed held-out multisine with the declared reset. The public initial guess is distinct from the hidden truth.
- **Evidence:** Three-model position/velocity overlays, parameter recovery, separate fit/validation errors, residuals, and the existing sensitivity diagnostic. Several successful starts support convergence for this problem, not universal identifiability.
- **Exercise / expected explanation:** Predict the effect of changing initial inertia or damping, then compare the preview and a completed fit. Explain why validation adds evidence beyond fit error.
- **Delivery / limit:** [Existing lesson](l0/README.md), [report](../../reports/l0_inertia_damping/report.md), and local CPU path. Matched structure and ideal torque/observations bound the conclusion. Independent reader acceptance remains open.

<a id="l0-e"></a>
### L0-E · When the input hides a parameter

- **Question / prerequisite:** Can many samples still leave inertia poorly constrained? Reuse L0 with K4 and essential K5.
- **Boundary:** Keep L0's plant, `J/b` unknowns, observation schema, estimator, bounds, and objective scaling fixed. Introduce only excitation choice.
- **Experiment:** Compare a slow input with a broader-band chirp under the same declared amplitude and duration budget. Use the same untouched multisine for both evaluations. Disclose resulting state coverage rather than assuming equal input budgets mean equal information.
- **Evidence:** Sensitivity directions and scaled loss contours, repeated starts, parameter variation, and held-out error. Weak sensitivity in noiseless data is an ill-conditioning warning; it does not guarantee failed recovery.
- **Exercise / expected explanation:** Pick which input better separates acceleration and velocity effects, then justify the choice using the figures. Distinguish structural non-identifiability from weak practical information.
- **Delivery / limit:** Proposed short CPU experiment; static comparison first, bounded browser input selector only after timing it. Noise and preprocessing are reserved for L1-O.

<a id="l1"></a>
### L1 · Identify a command delay

- **Question / prerequisite:** Can a timing effect invisible in the machine drawing be inferred from motion? Follow L0 and the relevant K3/K7 concepts.
- **Boundary:** `q_des → fixed PD → torque-command delay → gravity-loaded pendulum`. Geometry, payload, gains, and integration settings are known. Fit only effective delay from `t/q_des/q/qd`; public `qd` is derived from position. True torque and internal delay state are privileged diagnostics.
- **Experiment:** Fit the frozen chirp and predict the separately defined reversal waveform. Delay applies to the complete PD torque command, with the declared command history and split resets.
- **Evidence:** Boundary animation, frequency-dependent phase clues, residuals, and held-out position/velocity error. A pure delay's phase relation explains a clue; the closed-loop position response also depends on the plant and controller.
- **Exercise / expected explanation:** Predict what changing Initial delay will do, submit a fit, then explain the validation result. In the existing L1 app, this edit is pending until submission; replay and signal selection use the completed run.
- **Delivery / limit:** [Existing lesson](l1/README.md), [report](../../reports/l1_servo_loaded_pendulum/report.md), and local CPU path. The fitted delay is boundary-dependent, not an electromagnetic motor constant. Independent reader acceptance remains open.

<a id="l1-friction"></a>
### L1 extension · Distinguish friction from viscous damping

- **Question / prerequisite:** Why can a viscous-only model miss reversals even after fitting? Follow L1 and K3/K6.
- **Boundary:** A known-inertia rotary load with known applied torque. Oracle resistance is `b*qd + tau_c*tanh(qd/v_eps)`, with public fixed `v_eps`. Compare a viscous-only Student against a Student fitting `b` and `tau_c`. Delay is zero; gravity and saturation are absent in this isolated experiment.
- **Experiment:** Fit bidirectional motions covering low and moderate velocities. Hold out a predeclared different amplitude and reversal rate; report the achieved velocity coverage. Freeze both Student structures before evaluation.
- **Evidence:** Resistance-versus-velocity illustration, residuals around reversals, candidate prediction errors, and recovery of shared parameters only where sensitivity supports it. True resistance is explanatory evidence, not an estimator input.
- **Exercise / expected explanation:** Predict where the viscous-only residual will concentrate and propose data that separate `b` from `tau_c`. Explain why a residual-versus-velocity pattern alone does not prove friction.
- **Delivery / limit:** Delivered as the second L1 experiment with static explanation plus local CPU. This is smooth Coulomb-like resistance; it does not implement static sticking, Stribeck behavior, or backlash. A browser comparison is intentionally deferred.

<a id="l1-s"></a>
### L1-S · Reveal a torque limit

- **Question / prerequisite:** Can gentle motion identify a limit it never reaches? Follow L1 and compare the diagnosis with its friction extension.
- **Boundary:** Public torque command → symmetric clipping → known rotary dynamics. Estimate `tau_max`; torque scale and mechanics are fixed, with delay and extra friction absent. Applied Oracle torque is not given to the fitter.
- **Experiment:** Contrast a fit dataset entirely below clipping with one that crosses the limit. Predeclare a validation amplitude that exercises the limit. Compare unclipped and clipped Students on the same data.
- **Evidence:** Command/applied-torque illustration for evaluation, loss versus `tau_max`, and amplitude-dependent prediction errors. Below clipping, any sufficiently high limit produces the same behavior; report that bound instead of claiming a recovered value.
- **Exercise / expected explanation:** Choose the dataset that can constrain the limit, then explain why the other dataset needs a new experiment rather than a longer optimization run.
- **Delivery / limit:** Proposed static/local CPU lesson; optional amplitude preset in the browser. Velocity-, voltage-, and temperature-dependent limits are later extensions.

<a id="l1-o"></a>
### L1-O · Separate observation quality from plant behavior

- **Question / prerequisite:** What changes when velocity is computed from imperfect position? Follow L1 and K4/K6, before interpreting hardware logs.
- **Boundary:** Reuse the declared L1 plant and known sampling clock. Add one position-noise model with stated statistics. The Student receives noisy position and declared finite-difference velocity; exact integration velocity remains privileged.
- **Experiment:** Use predetermined independent noise seeds across fit/evaluation repeats. Compare a position-only objective with a properly scaled position-plus-derived-velocity objective. Declare that the two channels have correlated errors; freeze weights using fitting data only.
- **Evidence:** Raw position, derived velocity, residual scale, delay variation across runs, and prediction on withheld commands. Separate noisy observation error from optional evaluator-only latent-state error.
- **Exercise / expected explanation:** Explain why an additional derived channel does not necessarily add independent information. A visually smoother trace is not evidence of a more accurate timing estimate.
- **Delivery / limit:** Proposed local CPU lesson with static repeat summaries. Quantization, filter phase, timestamp offset, and jitter each need a separately controlled extension; this card does not fit them jointly.

<a id="l2"></a>
### L2 · Separate actuator and rigid-body errors in a fixed-base leg

- **Question / prerequisite:** Can a link error be hidden by changing an actuator parameter? Follow actuator lessons and K2/K4/K7; add coupling while excluding contact.
- **Boundary:** Proposed two-joint fixed-base leg under known gravity with declared joint commands and encoder observations. Begin with known actuator behavior and one link inertial group. Expand only to parameter combinations supported by sensitivity; do not promise recovery of every mass, CoM, and inertia separately.
- **Experiment:** Start with one body mismatch and a withheld posture/frequency. Then stage the roadmap's cases: A body error only, B actuator error only, C both, D lower-level constraints. Each comparison fixes its public dataset and fitting budget.
- **Evidence:** Synchronized leg replay, per-joint residuals, parameter correlation, and held-out prediction with/without component constraints. Distinguish physically shared parameters from compensating effective values.
- **Exercise / expected explanation:** Select a new posture or joint excitation that could distinguish two compensating solutions, and justify which parameters to fix or constrain.
- **Delivery / limit:** Proposed local simulator workflow and static/replay browser path. Asset, backend, parameter grouping, and runtime are implementation decisions to freeze before coding. No contact or floating base yet.

<a id="l3"></a>
### L3 · Add contact after free-space validation

- **Question / prerequisite:** Does a stance mismatch require a contact change or expose an unresolved upstream error? Require L2 free-space evidence.
- **Boundary:** Retain validated actuator/body settings. Begin with one declared compliant normal-contact model and fixed foot/surface geometry; fit a normal stiffness/damping pair only if the data separate them. Tangential friction is a subsequent controlled case.
- **Experiment:** Fit normal approach/compression and release motions; hold out approach speed or load. Declare joint and force measurements available to the Student. Contact-solver internals remain evaluator-only; rerun free-space validation after fitting.
- **Evidence:** Contact onset, penetration/force and motion traces, residuals, and held-out behavior. Freeze contact law, timestep, and force sampling; their settings affect the interpretation of fitted values.
- **Exercise / expected explanation:** Explain why changing a link mass to improve contact can invalidate existing free-space evidence. State what extra measurement would help separate stiffness and damping.
- **Delivery / limit:** Proposed local contact simulation with static/video/replay. Initially exclude slip, unknown terrain geometry, and simultaneous calibration of all contact terms; fitted contact values may be simulator-effective.

<a id="l4"></a>
### L4 · Compare two whole-Microduck fitting routes

- **Question / prerequisite:** When do component measurements help a whole-robot fit? Require L2/L3 and the corresponding actuator evidence.
- **Boundary:** One frozen Microduck Oracle, realistic declared command/joint/base observations, and a compact Student parameterization. Compare component-constrained fitting with global fitting.
- **Experiment:** Share whole-robot fitting motions and held-out motion families. Explicitly account for extra component data and fitting cost in the constrained route. Start with supported/fixed-base motions, then progress to stance or locomotion when the contract supports them.
- **Evidence:** Three-model robot replay, joint/base errors, prediction horizon, parameter interpretation, and compute/data budgets. The comparison measures two workflows; unequal data or constraints must not be described as an optimizer-only advantage.
- **Exercise / expected explanation:** Recommend a route for a stated data and compute budget, using both prediction evidence and remaining ambiguity.
- **Delivery / limit:** Proposed local or scheduled jobs; browser presents completed runs. RL transfer is a separate K8 extension: freeze identification data, train fresh policies with a declared budget, and evaluate them in the Oracle. Trajectory improvement alone does not establish transfer.

<a id="l5"></a>
### L5 · Share parameters across Microban joints

- **Question / prerequisite:** How much joint-specific freedom is useful? Follow L4; Microban remains the designated small humanoid.
- **Boundary:** One Microban Oracle with declared actuator families. Compare independent per-joint parameters, family-shared parameters plus bounded joint residuals, and a compact whole-robot effective model.
- **Experiment:** Use the same public fitting dataset and predeclared whole-body validation motions. Set family assignments and residual penalties from metadata/fitting data, not evaluation outcomes. Include a controlled joint-specific deviation to test whether sharing hides it.
- **Evidence:** Joint/body error maps, held-out motion predictions, parameter count, parameter stability, and computation cost. Separate reduced variance from biased underfitting.
- **Exercise / expected explanation:** Choose which parameters should be shared and which need a joint residual, citing the controlled deviation and held-out evidence.
- **Delivery / limit:** Proposed local CPU/GPU workflow with static summaries and optional result exploration. Numerical recovery claims require identifiable shared parameters; more joints do not by themselves justify more hidden physics.

<a id="l6"></a>
### L6 · Predict across model or simulator mismatch

- **Question / prerequisite:** What counts as success when the Student cannot represent the Oracle exactly? Follow L4; use L5 only when studying scale.
- **Boundary:** Start with one small previously validated plant, using a richer Oracle actuator and a restricted Student, or different numerical implementations. Align units, frames, command timing, and observation semantics before attributing errors to physics.
- **Experiment:** Change one source of mismatch at a time; fit within one operating range and evaluate withheld frequencies, loads, or motion families. Include timestep-refinement checks to distinguish numerical error from model limitations.
- **Evidence:** Residual structure, prediction horizon, cross-condition errors, and parameter interpretation. Report parameter recovery only for quantities whose meaning is shared across both models.
- **Exercise / expected explanation:** Identify the supported prediction envelope and propose either a richer Student or a better experiment. Justify the choice with a failure case.
- **Delivery / limit:** Proposed local/native simulator path; browser uses static evidence or replay. K8 may add targeted randomization and separate policy evaluation. Cross-simulator success alone is not hardware validation.

<a id="d06"></a>
## D06 · Hardware lesson cards

These are procedure and interpretation designs. Hardware, instrumentation, and operating limits must be specified for a concrete platform before an acquisition exercise exists. There are no generic hardware execution commands in this proposal.

| ID | Question and prerequisites | Experiment and evidence | Learner output / delivery |
|---|---|---|---|
| H0 | Which bench measurements support the chosen actuator boundary? Actuator lessons, L1-O, and a platform-specific bench procedure | Establish signs, units, torque/current calibration, clocks, and operating limits. Fit repeated bench motions; withhold a session or operating condition. Record voltage/temperature and distinguish sensor uncertainty from parameter variation. No assumption of known physical ground truth. | Annotated signal boundary, calibration record, repeated-fit/validation note. Static procedure and recorded example; acquisition and fitting run locally. |
| H1 | Does component evidence predict the real Microduck or Microban? H0 plus the applicable L2–L4 evidence | Progress from supported subsystem motions to whole-robot tests; preserve upstream validation. Hold out motion families or sessions and record hardware/controller versions. Report joint/base/contact evidence only for measured signals. | Explain one transfer success and one remaining mismatch; distinguish simulation prediction from demonstrated physical behavior. Local acquisition and completed-run review. |
| H2 | Can another engineer reproduce the full-humanoid result? H1 and platform-specific collection/operation procedures | Track actuator families, per-joint calibration, dataset lineage, fit budgets, and evaluation sessions. Recheck the downstream controller/policy under declared conditions rather than assuming identification implies deployment readiness. | Reproducible data-to-model handoff with a bounded claim and unresolved uncertainty. Local/server computation; static report and replay for review. |

<a id="d07"></a>
## D07 · Delivery and bilingual review

Follow the [delivery policy](../lesson_delivery_policy.md) and [lesson pipeline](../lesson_pipeline.md): the static explanation/video is the primary learning surface, the local experiment supplies the numerical evidence, and bounded WASM is optional. Build and verify the local numerical path before producing its static evidence and deciding on browser interaction. The present L0/L1 Marimo apps run through a local Python server; a self-contained WASM release is still backlog work.

| Surface | Review requirement |
|---|---|
| Static lesson | Question, boundary, evidence, exercise answer guide, limits, and local instructions are readable without running an app. Include captions or surrounding text that carry each video's lesson. |
| Browser interaction, if delivered | Declare dependencies and measured cold-start/run/memory budgets; check the worst allowed control setting. State whether it fits, previews, or only replays. |
| Local experiment | One implementation/configuration produces the report and lesson evidence. Document dependencies, runtime/resources, outputs, and reproduction command once available. |
| English and Chinese | Keep lesson IDs, equations, units, numbers, observation boundaries, and status aligned. Use the same report/data/assets; update both narratives when a contract changes. |

The static website provides English and Chinese course pages, lesson notes, report explanations, and curriculum design, with a language switch on each page. Teaching videos have both subtitle tracks and matching written explanations; the source footage and numerical data are shared. The local Python app and implementation records remain separate research tools. Maintain both languages when adding a lesson or changing its contract.

Shared terminology for future lesson translations:

| English | Chinese | Meaning in the course |
|---|---|---|
| System identification / SysID | 系统辨识 | Infer a declared model from observations |
| Plant boundary | 被辨识系统边界 | Defines what input enters which system and which output is observed |
| True system / Oracle | 真实系统 / Oracle | Synthetic source of hidden ground truth; not physical hardware |
| Student model | 待辨识模型 / Student | Declared candidate structure and tunable parameters |
| Initial model / Identified model | 初始模型 / 辨识后模型 | Before/after fitting roles |
| Fit / held-out validation | 拟合 / 留出验证 | Estimation data / data withheld from estimation and tuning |
| Residual | 残差 | `model - observed`, with the quantity and units stated |
| Excitation / identifiability | 激励 / 可辨识性 | How the input reveals effects / whether data can distinguish parameters |
| Physical / effective parameter | 物理参数 / 等效参数 | Independently meaningful quantity / value tied to a modeling boundary |

<a id="d08"></a>
## D08 · Next authoring work and feedback

| Order | Concrete output | Completion evidence |
|---|---|---|
| 1 | Review this bilingual sequence and the L0/L1 teaching questions | Feedback references lesson IDs and states what to keep, split, reorder, or clarify |
| 2 | Complete the static L0/L1 narrative and Chinese learner pages | Both languages explain the boundary, fit/validation, exercise, limits, and local mode; record actual independent reader answers |
| 3 | Freeze the L1 friction extension | Numerical contract, parameter/observation boundaries, held-out conditions, tolerances, and execution budget |
| 4 | Deliver the L1 friction extension locally with a report | Reproduction and learner evidence; make the browser decision after measuring the run |
| 5 | Add L0-E/L1-S and the observation bridge as needed, then freeze L2 | Every extension answers its own question; L2 explicitly states which upstream evidence it relies on |

Teaching order and implementation order differ: L0-E belongs early in the learner route, while the L1 friction extension is the first additional actuator experiment after current acceptance work. Advanced compliance/backlash, active excitation, optimizer leaderboards, and broad condition matrices stay optional until a lesson's residuals justify them. The [delivery backlog](../plans/course-delivery-split.md) owns packaging/deployment tasks.

Suggested review points: Does `D02` match how you want engineers to learn? Does each lab introduce a distinguishable uncertainty? Do the visuals and checkpoint answers make the lesson reviewable without executing code? Is a proposed exercise too shallow or too broad?

Feedback format: **ID → issue or preferred change → reason**. For example: “L1 friction → add two recorded speed ranges to the static exercise → make the separation between viscous and Coulomb-like resistance visible.” Feedback on this design is separate from the maintainer learner acceptance of a delivered lesson.
