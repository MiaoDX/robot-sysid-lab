# Lessons Curriculum Design Review

[中文版](course-design.zh-CN.md) · [Course map](../course/index.html) · [Existing lessons](README.md)

**Status: formal K/L reading pages completed; numerical implementations and individual lesson reviews remain, 2026-09-25.** This document records the agreed scope and tradeoffs from the batch discussion and defines the shared content contract. It owns the K/L teaching sequence and this rollout's scope; the [long-term roadmap](../03_synthetic_lab_roadmap.md) retains research directions. Numerical values, algorithm settings, asset versions, runtime budgets, and media scripts are frozen after individual reviews. The formal pages claim no numerical results that have not been produced and verified.

K0, K1, L0, and L1 already have lesson pages; both L1 delay and friction experiments are delivered. Independent learner acceptance for L0/L1 remains open. Formal pages now cover **K2–K8, L0-E, L1-O, elective L1-S, and L2–L6**. Hardware H lessons are outside this round; D06 retains the earlier draft for future discussion.

Review entry points: [outcomes](#d01) · [sequence and prerequisites](#d02) · [shared structure and evidence](#d03) · [K cards](#d04) · [L cards](#d05) · [delivery](#d07) · [individual review checklist](#d08). Cite lesson IDs in feedback; existing D01–D08 and L anchors remain available.

<a id="d01"></a>
## D01 · What learners should be able to do

The audience is robotics engineers who can read plots and have basic Python experience. The main outcome is independently designing identification experiments, fitting models, and diagnosing failures. L4 also includes one bounded downstream control comparison. RL training is an extension, not a core completion requirement.

After the core sequence, learners should be able to:

1. Draw a plant boundary, distinguish commands, applied torque, state, and observations, and specify what the fitter may use.
2. Choose excitation that exposes target effects and assess parameter correlation and coverage limits.
3. Use controlled comparisons to distinguish optimization failure, insufficient information, and inadequate model structure, then propose a next experiment.
4. Evaluate predictions on conditions withheld from adjustment and separate parameter recovery, behavioral prediction, and downstream performance claims.
5. Carry component evidence into whole robots, choose parameter sharing, and report an operating envelope and remaining uncertainty under mismatch.
6. Generate controller settings from different models using the same design method, then compare them in one Oracle without assuming the identified model wins every metric.

Mathematics uses **engineering derivations**: explain necessary equations, units, and key steps so learners can change models and objectives. Full proofs and advanced optimization details belong in supplementary reading. Each K lesson answers a general judgment question; L lessons test those judgments with data.

Start with a concrete failure: predict its cause, then compare controlled cases. Retain a verifiable matched baseline, but allow conclusions such as “only a range is constrained” or “another experiment is needed.” Before L2, introduce one main difficulty at a time; from L2 onward, explicitly study coupling and compensating solutions.

**Length targets:** 10–15 minutes for a K core reading and 25–40 minutes for a small lab explanation and exercise. Divide L2–L6 into continuous sections around individual questions; time local assignments separately. These are writing targets, not measured runtimes. Static reading must support understanding and plot exercises without installing a simulator or using a GPU.

<a id="d02"></a>
## D02 · Learning sequence and lesson boundaries

K0–K8 organize knowledge by topic; L0–L6 increase experiment complexity. Their numbers do not pair one to one. K lessons remain independent and L lessons link the needed sections; completing the entire knowledge track is not a prerequisite. Suffixed labs stay within their existing level and do not renumber delivered lessons.

| Stage | Recommended reading and experiments | Capability gained |
|---|---|---|
| Start | K0 → K1 → L0 | Complete the smallest inertia/damping identification loop |
| Method | K4 → K5 → K6 → L0-E, revisiting L0 | Understand excitation, fitting, held-out validation, and weak constraints |
| Actuators | K2 basics → K3 → L1 delay → L1 friction | Separate dynamics from the command chain and isolate effects |
| Observations | L1-O; L1-S is an elective branch | Separate measurement errors from plant behavior; study limits as needed |
| Structure | K7 → L2 → L3, revisiting coupling/contact in K2 | Recognize compensation and validate free space before contact |
| Whole robot | K8 → L4 | Compare identification routes and test downstream control effects |
| Scale and mismatch | Default L5 → L6; either is accessible after L4 | Study parameter sharing and models that cannot exactly match the system |

This is a recommended sequence, **not a strict dependency chain**. Necessary prerequisites describe capabilities and may be satisfied by equivalent experience; cards list them explicitly. L5 is not required for L6. Reuse K4–K6 throughout. Introduce the relevant K7 idea locally in L1 and study it systematically before L2. Read K8 before L4 and revisit it in L6.

```text
K0/K1 → L0 → K4/K5/K6 → L0-E
                         ↓
                 K2 basics / K3 → L1 delay → L1 friction → L1-O
                                      └→ L1-S (elective)
                 K7 / K2 coupling → L2 → K2 contact / L3 → K8 / L4
                                                             ├→ L5 sharing
                                                             └→ L6 structure mismatch → cross-engine case
```

The recommended reading path is **K0 → K1 → L0 → L1 (including friction)** and then the formal K/L pages shown in D02. Every released page is readable on its own where its listed prerequisites are met; numerical evidence status is stated per lesson. Required concepts for L1 are explained locally.

Maintain asset and backend continuity: use the same fixed-base two-joint leg for L2/L3 and connect its conventions to the full Microduck in L4. L5 moves to the designated Microban while reusing the primary backend and experiment protocol. Freeze the primary backend and asset versions at L2 review and retain them afterward; introduce the second engine in L6. Geometry adaptation is not assumed to be implemented.

Compliance, backlash, Stribeck friction, active excitation, optimizer leaderboards, broad/targeted randomization, and RL training are topics for extensions. Promote one into a lesson only when a concrete failure motivates it.

<a id="d03"></a>
## D03 · A shared reading structure

| Stage | Learner experience | Author supplies |
|---|---|---|
| 01 · Failure and prediction | See a mismatch and predict a cause | Initial-model comparison and one judgment question |
| 02 · Boundary and derivation | Identify inputs, unknowns, fixed quantities, and equations | Signal visibility diagram, units, and key derivation |
| 03 · Controlled experiment | Explain what changes and what is held fixed | Matched baseline, comparison groups, fit/development/final evaluation split |
| 04 · Evidence and diagnosis | Judge the model, data, or optimizer | Fit/held-out views, residuals or sensitivity, bounded claims |
| 05 · Exercise and answer guide | Predict, then read plots or change one setting | Exercise that needs no code execution, explanation, optional bounded interaction |
| 06 · Limits and next step | Propose a discriminating experiment | Remaining ambiguity, next lesson, and necessary prerequisites |

Use the same three-level signal visibility diagram at the start of each lesson:

| Level | Purpose and access | Examples |
|---|---|---|
| Fitter-visible | Only public inputs, measurements, and metadata from the fitting split may enter estimation | Commands, encoders, declared force measurements |
| Evaluation | Scoring only; unavailable to fitting and tuning. If used for selection, relabel as development data | Final held-out observations, comparable shared-parameter truth |
| Oracle diagnostics | Generation and explanation only; excluded from objectives, initialization, bound selection, and model selection | Applied torque, exact hidden state, solver internal forces |

These levels describe use, not permanent assignments by signal name. L0 explicitly supplies applied torque; L1 delay does not. Every diagram names the split and visibility. Even public measurement types from held-out data are unavailable to the fitter.

The minimum evidence package for computational labs is a True/Initial/Identified comparison, separately reported fit and final held-out metrics, residual or sensitivity plots, an evidence note, and a next-experiment proposal. Label candidate Students separately. K lessons reuse actual L evidence or clearly labeled conceptual illustrations; they do not invent runs to satisfy the template.

Each lesson asks for: “I expected…; this plot or metric shows…; under these conditions it supports…; it still cannot exclude…; next I would test….” Discuss inadequate structure, insufficient data, and optimization failure. Explain when a branch is inapplicable rather than fabricating all three failures in every lesson. Answer guides identify the supporting plot, unsupported conclusions, and an experiment that distinguishes remaining hypotheses.

Model selection is development. Declare candidate structures, bounds, weights, regularization, and controller design rules before final evaluation. Validation used for selection becomes development data; final claims require another untouched split. Declare seeds and budgets for repeated runs; do not repeatedly inspect final evaluation to select the best run.

Use a continuous page for one learning question. Section anchors aid scrolling; clips sit beside the relevant question with a written explanation, and curves retain labels and line styles. Replay never fits; previews and completed results remain distinct. Reuse the existing course visual system and review scripts and controls per lesson.

<a id="d04"></a>
## D04 · Knowledge lesson cards

K0/K1 are delivered and retained: K0 motivates identification; K1 separates inputs, state, observations, models, and parameters. The K2–K8 cards now have corresponding formal reading pages with the shared structure. Conceptual visuals remain explicitly labeled until a numerical run supplies verified evidence. Reuse the [books and references](../02_learning_path_and_references.md).

[K2](#k2) · [K3](#k3) · [K4](#k4) · [K5](#k5) · [K6](#k6) · [K7](#k7) · [K8](#k8)

<a id="k2"></a>
### K2 · Locate dynamics terms from motion errors

- **Core question:** Why do parameters that work in one posture fail in another?
- **Necessary prerequisites:** K1 signal distinctions and L0 inertia/damping intuition; introduce derivatives and torque units here.
- **Content boundary:** Explain terms and dimensions in `M(q)qdd + C(q,qd)qd + g(q) + tau_f = tau + J_c^T lambda`. Core reading covers single-joint inertia, gravity, and dissipation. Revisit coupling/contact before L2/L3; no full rigid-body algorithm derivation is required.
- **Outline:** Constant-speed/acceleration errors → pendulum torque balance → posture-dependent gravity → two-joint coupling → generalized contact force.
- **Key comparison:** Keep the plant fixed and vary posture or frequency to distinguish position-, velocity-, and acceleration-dependent effects. A similar residual pattern is not a unique cause.
- **Visual plan:** Pendulum force diagram, torque-term traces, synchronized motion showing one joint exciting another, and contact-force-to-joint-torque illustration.
- **Exercise and outcome:** Select candidate dynamics terms for three mismatches and propose discriminating experiments. Answer guides acknowledge when multiple candidates remain.
- **Limits and connection:** Do not promise separate recovery of every mass, CoM, and inertia. Supply sections needed by K3, L1, and L2/L3.
- **Individual review:** Derivation length, geometry illustrations, notation, and the split between core and revisit sections.

<a id="k3"></a>
### K3 · Trace commands to joint torque

- **Core question:** Why can correct-looking commands still produce delay or resisting-torque errors?
- **Necessary prerequisites:** K1 and K2 single-joint basics; understand the role of fixed PD feedback.
- **Content boundary:** Locate the controller, delay, saturation, and friction. Treat these as controlled cases rather than adding them all to one Student. Explain `tau_cmd = Kp(q_des-q) + Kd(qd_des-qd)` and changes to applied torque.
- **Outline:** Boundary diagram → ideal actuator → command delay → viscous/smooth Coulomb-like resistance → output limit → evidence that warrants richer structure.
- **Key comparison:** Add only delay, friction, or saturation in each case; examine different clues in frequency, velocity direction, and amplitude.
- **Visual plan:** Command-to-motion diagram, delay timeline, resistance–velocity plot, commanded/applied torque saturation curve, all labeled by visibility.
- **Exercise and outcome:** Locate hidden effects in three boundary diagrams and choose a new experiment. Explain why effective command delay is not the electromagnetic motor time constant.
- **Limits and connection:** Defer compliance, backlash, Stribeck, and thermal models. Connect L1 delay/friction and elective L1-S; deepen parameter interpretation in K7.
- **Individual review:** PD/delay explanation scope, visual correspondence across isolated cases, and extension entry points.

<a id="k4"></a>
### K4 · Decide whether an experiment separates parameters

- **Core question:** Why can many samples and a small fitting error still leave unreliable parameters?
- **Necessary prerequisites:** K1 and L0; introduce local derivatives for sensitivity here.
- **Content boundary:** Use L0's `J/b` to explain excitation, parameter scaling, correlated sensitivity columns, and structural versus practical identifiability. Full information-matrix theory is supplementary.
- **Outline:** Slow-motion blind spots → perturb one parameter → compare sensitivity directions → loss valleys and parameter combinations → design the next input.
- **Key comparison:** Slow input versus broadband chirp with one plant and declared equal budgets; revisit one versus multiple postures in L2 and report actual state coverage.
- **Visual plan:** Input/state coverage, scaled sensitivity directions or columns, two-dimensional loss contours, and multi-start parameter scatter.
- **Exercise and outcome:** Choose an input that separates two candidate parameter combinations and explain why more similar samples may not help. Do not present noiseless weak sensitivity as guaranteed recovery failure.
- **Limits and connection:** Local sensitivity is not proof of global uniqueness. Lead into L0-E and revisit in L2/L5.
- **Individual review:** Scaling, minimum matrix background, and conditions/captions for slow-versus-fast comparisons.

<a id="k5"></a>
### K5 · Understand what fitting actually solved

- **Core question:** Does optimizer success establish a trustworthy model, and what should change when fitting fails?
- **Necessary prerequisites:** L0 and K4 loss-valley intuition; explain summation and derivative notation in context.
- **Content boundary:** Start with L0's bounded nonlinear least squares. Explain residual scales, objectives, initial values, and bounds, deriving one local linearization step. This is not an optimizer catalog.
- **Outline:** `r = model - observed` → unit/noise-scaled loss → local update → termination/bound hits → multiple starts and diagnosis.
- **Key comparison:** Vary start and budget with fixed data/model; then hold the estimator fixed and change excitation or structure to distinguish the three diagnostic branches.
- **Visual plan:** Iterations on a loss surface, channel contributions under poor scaling, and termination states beside fit/held-out errors.
- **Exercise and outcome:** Choose more budget, different excitation, or a richer structure from three fitting records, citing evidence. Write a scaled objective.
- **Limits and connection:** Convergence proves neither uniqueness nor generalization. Introduce methods such as CMA-ES only if L4 needs them; leaderboards are extensions. Connect L0-E/K6 and later labs.
- **Individual review:** Derivation length, objective example, and the minimum useful optimizer-log fields.

<a id="k6"></a>
### K6 · Challenge predictions with new experiments

- **Core question:** What can still falsify a model when training trajectories overlap?
- **Necessary prerequisites:** L0 and K1; use K4/K5 to understand estimation and selection.
- **Content boundary:** Explain fitting, development, final held-out evaluation, residual units/structure, and splits by motion, frequency, direction, and load. Full statistical testing is supplementary.
- **Outline:** Limits of replaying fitted data → withhold conditions relevant to intended use → per-channel errors → residual patterns → prediction envelope.
- **Key comparison:** Small fitting errors versus structured residuals on unseen reversals/frequencies. Contrast random time-point splits with independent whole runs to explain adjacent-sample leakage.
- **Visual plan:** Split diagram, side-by-side fit/held-out trajectories, residuals versus velocity or time, and cross-condition error matrix.
- **Exercise and outcome:** Audit a high-accuracy claim tuned on validation and redesign final evaluation; write a bounded evidence statement.
- **Limits and connection:** Residual shape does not uniquely identify missing physics; low prediction error does not establish control performance. Reuse from L0/L1 through L6.
- **Individual review:** Metrics, leakage example, and ambiguity in residuals and answer guides.

<a id="k7"></a>
### K7 · Interpret fitted parameter values

- **Core question:** If very different parameters fit motion well, which values are credible?
- **Necessary prerequisites:** L1 delay/friction and K4/K6; recap effective delay locally.
- **Content boundary:** Distinguish physical, effective, nuisance, and uncertain parameters. Explain combinations, compensation, and boundary dependence without requiring a unique truth mapping for every parameter.
- **Outline:** Two good fits → omitted effects absorbed by parameters → independent constraints and combinations → stability and uncertainty ranges → reporting.
- **Key comparison:** Correct and incomplete structures fitted to the same public data; test whether compensation persists at new postures/frequencies.
- **Visual plan:** Parameter-pair loss valley, fitted values across conditions, semantic comparison table, and predictions before/after component constraints.
- **Exercise and outcome:** Classify reported parameters, identify which permit recovery error, and propose a measurement that resolves compensation.
- **Limits and connection:** Local optimizer curvature does not summarize all mismatch uncertainty. Lead into L2 and revisit in L5/L6.
- **Individual review:** Compensation example and boundary, depth of range estimation, and reporting format.

<a id="k8"></a>
### K8 · Use identification for control and transfer

- **Core question:** How do we test whether better prediction improves a downstream task?
- **Necessary prerequisites:** K6/K7 and L2/L3; read before L4's downstream case.
- **Content boundary:** Separate same-input prediction, same-controller closed-loop testing, and redesigning controllers from different models. The core uses the third protocol; RL and domain randomization are extensions.
- **Outline:** Prediction versus control metrics → freeze identification data → one design method maps models to controller settings → evaluate in one Oracle → uncertainty and operating envelope.
- **Key comparison:** Initial and identified models each produce controller settings. Fix design rules, budgets, task, constraints, and evaluation conditions; do not repeatedly tune using final Oracle scores.
- **Visual plan:** Two model-to-controller paths, tracking error/control effort/constraint violations, and the relationship between training, identification, and evaluation data.
- **Exercise and outcome:** Spot a claim that changing only the offline model improves an unchanged controller; propose a fair evaluation that permits mixed outcomes.
- **Limits and connection:** Do not assume the identified model wins all metrics. L4 supplies a small control comparison; L6 revisits mismatch. Targeted/broad randomization and retraining RL policies are extensions.
- **Individual review:** L4 controller design method, task and metrics, and separation of extension protocols from the core.

<a id="d05"></a>
## D05 · Synthetic lab cards

All new cards are designs awaiting implementation. Every lab follows D03's visibility levels, data splits, and minimum evidence package; cards specify the new teaching emphasis. Freeze numerical truth, bounds, sampling/integration, tolerances, seeds, and budgets at individual review.

[L0](#l0) · [L0-E](#l0-e) · [L1 delay](#l1) · [L1 friction](#l1-friction) · [L1-O](#l1-o) · [L1-S](#l1-s) · [L2](#l2) · [L3](#l3) · [L4](#l4) · [L5](#l5) · [L6](#l6)

<a id="l0"></a>
### L0 · Recover inertia and damping

**Delivered core foundation; its numerical contract is not redesigned here.** The [lesson](l0/index.md) and [fixed report](../../reports/l0_inertia_damping/report.md) use `J*qdd + b*qd = u`, known applied torque, ideal `t/u/q/qd`, and only unknown `J/b`. K0/K1 are sufficient to begin. Fit a chirp and test held-out multisine motion, showing True, Initial, and Identified models.

Learners change initial inertia or damping, distinguish previews from completed fits, and explain held-out predictions. Matched structure, known torque, and ideal observations bound the claim. Independent learner acceptance remains open. Revisit this plant in K4–K6/L0-E.

<a id="l0-e"></a>
### L0-E · When input hides a parameter's effect

- **Core question / role:** Why can many slow-motion samples still weakly constrain inertia? Core bridge lesson.
- **Necessary prerequisites:** L0 and the core of K4–K6.
- **Boundary and observations:** Keep L0's plant, `J/b`, public observations, estimator, bounds, and loss scaling fixed. Change only excitation. Truth is evaluation-only and observations remain ideal.
- **Outline:** Question a small fit error → acceleration/velocity coverage → loss valley → change excitation → test a new motion.
- **Key comparison:** Slow input and broadband chirp under the same declared amplitude/duration budget, scored on a common final held-out multisine. Report actual state coverage; equal budgets do not imply equal information.
- **Visuals and evidence:** Input/state coverage, scaled sensitivity and two-dimensional loss contours, multi-start results, parameter recovery, and held-out errors.
- **Exercise and outcome:** Choose the next input and explain how it separates inertia and damping. Answer guides distinguish weak sensitivity, practical instability, and structural non-identifiability.
- **Limits and next lesson:** Noiseless weak sensitivity need not cause recovery failure; do not manufacture that conclusion. Noise belongs in L1-O. Continue to K2/K3/L1.
- **Delivery:** Static comparisons and local CPU assignment; optional input presets require measured budgets.
- **Individual review:** Amplitude/duration and frequency bands, parameter scaling, weak-constraint display criteria, and common evaluation input.

<a id="l1"></a>
### L1 · Identify command delay

**Delivered core foundation; retain the implementation.** The [lesson](l1/index.md) and [fixed report](../../reports/l1_servo_loaded_pendulum/report.md) use `q_des → fixed PD → full torque-command delay → gravity-loaded pendulum`. Fit effective delay from public `t/q_des/q/qd` only. Derive `qd` from position; applied torque and delay internals are diagnostics. Geometry, load, gains, and integration settings are known.

Necessary capabilities are L0 and command/state distinctions. K2 basics/K3 are recommended; introduce K7's effective-parameter idea locally. Fit chirp input, predict separately defined reversal motion, and explain phase clues, residuals, and closed-loop effects. Changes to initial delay require explicit fitting; replay reads completed results. The estimate is not a motor electromagnetic time constant. Independent learner acceptance remains open. Continue to the delivered friction experiment.

<a id="l1-friction"></a>
### L1 extension · Separate friction from viscous damping

**Delivered and retained in the core sequence.** The second isolated experiment on the [L1 page](l1/index.md) and its [fixed report](../../reports/l1_friction/report.md) use known inertia and applied torque. Oracle resistance is `b*qd + tau_c*tanh(qd/v_eps)`, with public fixed `v_eps`. Compare a viscous-only Student with one fitting `b/tau_c`. Delay is zero; gravity and saturation are absent.

Study after L1 delay with K3/K6. Bidirectional motion across speeds and predeclared held-out amplitudes/reversal rates expose structural residuals. Learners explain viscous-only mismatch near reversals and propose inputs that separate the resistance terms. Velocity-correlated residuals alone do not uniquely establish friction. This is smooth Coulomb-like resistance, without stiction, Stribeck, or backlash. Static explanation, CPU report, and notebook are delivered; browser comparison remains deferred. Continue to L1-O or elective L1-S.

<a id="l1-o"></a>
### L1-O · Separate observation quality from plant behavior

- **Core question / role:** Does poor-looking differentiated velocity mean the plant or model changed? Core bridge lesson.
- **Necessary prerequisites:** L1 delay and K4/K6; recommended after friction.
- **Boundary and observations:** Reuse the L1 plant and add one position-noise source with declared statistics. Publish noisy position, velocity derived by a declared method, a known sampling clock, and commands. Exact velocity remains an Oracle diagnostic.
- **Outline:** Differentiation amplifies noise → correlated channels → loss scales/weights → repeated-fit variation → observation error versus true-state error.
- **Key comparison:** Position-only versus position-plus-differentiated-velocity objectives. Share data within each comparison and use independent predeclared seeds for fit/development/final evaluation. Choose weights from fitting or explicitly designated development data only.
- **Visuals and evidence:** Noisy position and derived velocity, channel residual scales, delay-estimate distribution, and held-out command predictions. Evaluators may separately report true-state error without returning it to the fitter.
- **Exercise and outcome:** Explain why a derived channel need not add independent information; compare accuracy and stability. Visual smoothness is not a substitute for timing-estimation quality.
- **Limits and next lesson:** Do not simultaneously introduce quantization, filter phase, timestamp offset, or jitter. Establish observation boundaries before K7/L2.
- **Delivery:** Static repeated-run summaries and a local CPU lab; no promise of live browser fitting.
- **Individual review:** Noise model/strength, differencing/endpoints, correlated-channel treatment, weights, and repetitions.

<a id="l1-s"></a>
### L1-S · Make torque saturation visible

- **Core question / role:** Can data that never reach the output limit recover it? Actuator elective, not a prerequisite for L2.
- **Necessary prerequisites:** L1 and K3/K4/K6; compare with friction diagnostics.
- **Boundary and observations:** Public torque command → symmetric saturation → known rotational dynamics. Fit `tau_max`, fixing mechanical parameters and torque scale. Publish motion measurements; applied torque is diagnostic-only. No delay or extra friction.
- **Outline:** A successful-looking gentle-motion fit → flat loss above the command range → excite saturation → compare structures → report a lower bound when appropriate.
- **Key comparison:** Non-saturating versus threshold-crossing fitting data. On each dataset compare unlimited/limited Students and evaluate on a common predeclared held-out amplitude set.
- **Visuals and evidence:** Command/applied torque, saturation fraction, loss versus limit, predictions and residuals across amplitudes.
- **Exercise and outcome:** Select data that constrain the limit. Explain why equally plausible large limits support a constraint range rather than a unique recovered value.
- **Limits and next lesson:** Speed-, voltage-, and temperature-dependent limits are extensions. Return to L1-O/L2 afterward.
- **Delivery:** Static and local CPU; optional amplitude presets.
- **Individual review:** Amplitudes, threshold, reporting non-saturation, and candidate comparison budget.

<a id="l2"></a>
### L2 · Separate actuator and body errors in a fixed-base leg

- **Core question / role:** Can actuator parameters hide wrong link parameters? First multijoint coupling lesson.
- **Necessary prerequisites:** Diagnostic capabilities from L0-E, L1 delay/friction, and L1-O; coupling in K2 and K4–K7. L1-S is not required.
- **Boundary and observations:** Two-joint fixed-base leg, known gravity, one primary backend; public joint commands/encoders with fixed controller and observation processing. Initially fit one link inertial parameter group, later allowing limited actuator parameters. True torque, body parameters, and internal forces remain evaluation/diagnostic-only.
- **Outline:** One-posture success fails elsewhere → individual/joint excitation → A body error → B actuator error → C both → D component constraints.
- **Key comparison:** A/B isolate causes, C exposes compensation, D tests whether lower-level evidence reduces ambiguity. Each comparison uses the same public data, parameter scaling, and declared budget, withholding postures/frequencies. Fit only combinations supported by sensitivity.
- **Visuals and evidence:** Synchronized leg/two-joint replay, per-joint residuals, parameter correlation/loss slices, held-out errors before/after constraints, and extra component-data cost.
- **Exercise and outcome:** Given compensating solutions, choose a posture or input that separates them and name parameters to fix/constrain. Do not assume separate recovery of every mass, CoM, and inertia.
- **Limits and next lesson:** No contact or floating base. Carry settings into L3 only after validating their free-space operating envelope.
- **Delivery:** Static sections, video/precomputed replay, and a local simulator assignment.
- **Individual review:** Leg asset aligned with Microduck, primary backend/version, identifiable groups, motions/budgets, and component-constraint provenance.

<a id="l3"></a>
### L3 · Add contact after validating free space

- **Core question / role:** Can normal contact explain pressing or light-landing errors? Add only contact uncertainty.
- **Necessary prerequisites:** L2 free-space evidence, contact in K2, and K6/K7.
- **Boundary and observations:** Same leg and primary backend, with validated actuator/body settings and fixed foot/ground geometry. The first core case uses compliant normal contact to study stiffness/damping. Publish commands, motion, and declared normal-force measurements; solver internal forces/state are diagnostics.
- **Outline:** Free space passes but contact fails → quasi-static pressing → dynamic release/light landing → separate stiffness/damping → regress upstream evidence.
- **Key comparison:** Controlled compression/release across speeds/loads, withholding speed or load. Repeat free-space validation before/after fitting. Timestep refinement checks numerics; timestep is not a fitted parameter.
- **Visuals and evidence:** Contact-event replay, force–compression and force–velocity relationships, onset/motion/force residuals, held-out metrics, and free-space regression table. Unobserved penetration appears only in diagnostics.
- **Exercise and outcome:** Judge whether one pressing motion separates stiffness/damping and propose another speed/force measurement. Explain why changing mass to hide contact error is invalid.
- **Limits and next lesson:** Exclude tangential friction, slip, and unknown terrain. Report combinations or ranges when parameters cannot be separated. Contact values may be backend-effective; supply bounded contact evidence for L4.
- **Delivery:** Static evidence, video/replay, and local contact simulation.
- **Individual review:** Contact law/semantics, force measurement model, load control, timestep convergence criteria, and separation conditions.

<a id="l4"></a>
### L4 · Compare whole-robot fitting routes and control outcomes

- **Core question / role:** When does component evidence help identification, and does the improved model help one control task? First whole-robot application, split into route comparison and downstream testing sections.
- **Necessary prerequisites:** L2/L3 and corresponding actuator evidence, K4–K8. Read K8 before the control comparison.
- **Boundary and observations:** Microduck Oracle on the primary backend, compact Student parameterization, and declared command/joint/base observations. Begin with supported or fixed-base motions and relax boundaries gradually; full locomotion/RL training is not the first required task.
- **Outline:** A good single-motion fit fails elsewhere → component constraints versus global fitting → data/compute costs → choose models and freeze protocol → model-based controller design → Oracle evaluation.
- **Key comparison:** Route A uses component evidence to constrain a subsequent fit; route B fits globally from whole-robot data. Share whole-robot fitting/final held-out motion families and declared budgets, accounting separately for A's extra data/compute. The downstream case uses the initial model and an identified model chosen by a predeclared rule. Generate settings with **the same controller design method**, then compare in **the same Oracle** with paired initial conditions/disturbances and identical task constraints.
- **Visuals and evidence:** Three-model replay, joint/base errors, route-cost table; two model-to-controller paths, tracking error, control effort, and constraint violations. Report identification and downstream evaluation separately, aggregating conditions as needed.
- **Exercise and outcome:** Recommend a fitting route under a budget, audit downstream fairness, and explain how one metric can improve while another worsens.
- **Limits and next lesson:** Fix the design method, not controller settings. Changing only an offline model with an unchanged controller cannot establish control improvement. Do not select models or repeatedly tune controllers using final Oracle scores; do not assume universal improvement. RL and broad/targeted randomization belong in K8 extensions. L5 and L6 are independent next branches.
- **Delivery:** Static/precomputed results, local or scheduled whole-robot fitting and a small control experiment; no RL training inside the fit loop.
- **Individual review:** Parameterization/motion families, component-data cost, control task/design method, model selection rule, evaluation conditions, and metrics.

<a id="l5"></a>
### L5 · Share parameters across Microban joints

- **Core question / role:** Is fitting every joint independently better than sharing? Study scale and parameterization without adding many new physical effects.
- **Necessary prerequisites:** L4 and K4/K5/K7; L6 is not required.
- **Boundary and observations:** Designated Microban on L4's primary backend, fixed observation protocol, and declared actuator families. Compare independent joints, family sharing plus bounded joint residuals, and compact whole-robot effective parameters. True joint deviations are scoring/explanation-only.
- **Outline:** More parameters but worse held-out predictions → family sharing → joint exceptions → freedom/stability → complexity selection.
- **Key comparison:** Share public fitting data, final held-out whole-body motions, and declared budgets across three schemes. Use a family-similar baseline and a controlled joint-specific deviation; examine stability over repeated datasets/runs. Choose groups/penalties from metadata, fitting, or explicit development data, never final evaluation.
- **Visuals and evidence:** Joint/body error heatmaps, parameter counts and estimate distributions, residuals hiding exceptions, cross-motion predictions, and runtime costs.
- **Exercise and outcome:** Identify joints needing residual parameters and justify the choice. Distinguish variance reduction from sharing bias; neither more nor fewer parameters is automatically better.
- **Limits and next lesson:** Report recovery only for semantically shared, identifiable parameters. This is not a new friction/compliance catalog. Continue to L6 if desired; L6 does not depend on this lesson.
- **Delivery:** Static summaries, precomputed replay, local CPU/GPU or scheduled work with actual resource requirements declared.
- **Individual review:** Microban version, families, controlled exceptions, residual constraints, repetition budget, and stability metrics.

<a id="l6"></a>
### L6 · From structural mismatch to a true cross-engine test

- **Core question / role:** How should success and an operating envelope be defined when the Student can never exactly represent the Oracle? Core conclusion.
- **Necessary prerequisites:** L4 and K6–K8; reuse L1 small-system boundary knowledge. L5 is not required.
- **Boundary and observations:** Return to one verified single-joint plant. Case A isolates one structural mismatch using a richer actuator Oracle and restricted Student within the primary backend. Case B introduces a **genuinely different physics engine for the same small plant and task**. Publish semantically aligned input/motion observations and hide internal forces/state; do not start with cross-engine whole-humanoid fitting.
- **Outline:** Matched baseline → A irreducible structural residual → valid operating range → align units/frames/timing/observations → B cross-engine case → remaining errors and uncertainty.
- **Key comparison:** A removes one effect at a time. B fixes the task, public interface, and comparable modeling assumptions, documenting backend semantics that cannot align. Both compare fitting and held-out frequencies/loads/motions and include timestep refinement. B may differ through multiple engine mechanisms; do not attribute all errors to one physical term.
- **Visuals and evidence:** Model/parameter semantics table, residuals, timestep-refinement error, cross-condition error matrix, prediction horizon, and operating envelope. Use the shared minimum evidence package, reporting recovery only for semantically shared parameters.
- **Exercise and outcome:** Choose a richer Student, a better experiment, or a narrower use envelope from a failure case, citing evidence. Explain why cross-engine error is not a direct estimate of real-world error.
- **Limits and next lesson:** Completing A alone does not complete L6; B is agreed scope. The second engine remains to be selected. Cross-simulator success does not establish hardware performance. Return to K8 uncertainty; RL/randomization are later extensions.
- **Delivery:** Static/replay and local reproduction paths for both backends; no browser-fitting promise.
- **Individual review:** Plant and first omitted effect, second engine, interface alignment table, timestep checks, shared parameter meanings, and evaluation conditions.

<a id="d06"></a>
## D06 · Hardware lesson cards

**Outside this round: the existing draft is retained without renewed review and does not create K/L prerequisites.**

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


The agreed curriculum now has formal reading pages for every row below. The table records the remaining numerical and evidence work; a static page does not claim that its local experiment has already run:

| Lessons | Main reading and presentation | Full computation |
|---|---|---|
| K2–K8 | Static knowledge pages, illustrations, and cited fixed lab evidence | No independent fitting requirement |
| L0-E, L1-O, L1-S | Static comparisons; optional bounded interaction after budget checks | Local CPU |
| L2/L3 | Static, video, and precomputed replay | Local native simulation and fitting |
| L4/L5 | Static lessons, report summaries, and precomputed replay | Local CPU/GPU or scheduled work with actual requirements declared |
| L6 | Static evidence and replay for both cases | Local reproduction with both backends |

K and L pages share the explanatory structure; only computational labs require full numerical artifacts. The formal static pages are complete, while local reports, simulator replays, and performance evidence remain per-lesson implementation work. Large experiments are accepted in their declared CPU/GPU environment rather than requiring CPU for every lesson. Static reading still requires no compute setup. A planned visual becomes a course result only after an actual run produces and verifies it.

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
## D08 · Individual review and next steps

This round delivers a unified content design, not new lesson prose, runnable experiments, or measured reports. Delivered L1 friction is no longer listed as the next experiment to build from scratch. Agreement on the overall design neither replaces independent L0/L1 learner acceptance nor freezes the details below.

| Review batch | Scope | Decisions to produce |
|---|---|---|
| 1 · Method bridge | K4/K5/K6 and L0-E | Derivation depth, excitation comparison, scaling, diagnostic plots, and answer guides |
| 2 · Actuators and observations | K2 basics/K3, L1-O; elective L1-S | Noise/correlated channels, objectives, saturation comparison; reuse delivered delay/friction evidence |
| 3 · Structure and contact | Later K2/K7, L2/L3 | Primary asset/backend, parameter combinations, component constraints, normal contact, force measurements, and numerical checks |
| 4 · Whole robot and control | K8 and L4 | Costs of the two fitting routes, control task/design method, model selection, and final evaluation |
| 5 · Two later branches | L5 and L6, reviewed independently | Sharing/exceptions and repeat budget; small plant, second engine, and interface semantics |

These are suggested review batches, not implementation dates, and an individual lesson need not wait for the entire sequence to be reviewed. After its review, freeze one numerical contract and content outline, then progress through local numerics → fixed evidence → bilingual lesson → optional interaction. K lessons may begin with clearly labeled conceptual illustrations; experimental plots and performance claims must come from actual later runs.

Each review asks whether the question is focused, prerequisites are reasonable, comparisons distinguish hypotheses, signals/splits are explicit, plots support the claims, and exercise answers follow from evidence. Identify remaining values, budgets, and media decisions. Amend the card here when a detail changes rather than creating a parallel design.

**Agreed decision index:** The table records conclusions from batch questions Q1–Q18 for traceability; it is not a new approval checklist.

| Discussion IDs | Agreed direction | Location |
|---|---|---|
| Q1, Q11, Q17 | Identification/diagnosis is the main outcome; L4 requires a small control comparison with one design method, model-dependent settings, and one Oracle. RL/randomization comparisons are extensions | D01, K8, L4 |
| Q2, Q6 | Engineering derivations; independent K judgment lessons, with L linking needed sections and testing them using data | D01, D04 |
| Q3, Q13 | L0-E/L1-O are core, L1-S elective; advanced physics, active excitation, and leaderboards are extensions | D02, D05 |
| Q4, Q7 | Begin with failure/prediction, isolate effects before compensation from L2, and allow ranges or calls for new experiments | D01, D03, D05 |
| Q5, Q12 | Compact core; static-first explanation, precomputed replay, full fitting locally | D01, D07 |
| Q8 | One leg for L2/L3 aligned with Microduck in L4; Microban in L5 retains the primary backend; L6 adds a second engine | D02, L2–L6 |
| Q9, Q10 | Three signal visibility levels and a shared evidence template, with diagnosis and a next experiment in every lesson | D03 |
| Q14 | Separate suggested sequence from prerequisites; L5/L6 are independent after L4; introduce K8 before L4 | D02 |
| Q15, Q16 | L3 begins with normal contact only; L6 contains both single-engine structural mismatch and a genuine cross-engine case | L3, L6 |
| Q18 | Update this bilingual draft and related entry points; retain H's old draft outside this review; implement no new labs | This document, course homepage |

Feedback format: **lesson ID → proposed adjustment → reason or hypothesis to test**. Example: “L3 → add force comparisons at equal compression but different speeds → test whether stiffness and damping can actually be separated.” The [delivery backlog](../plans/course-delivery-split.md) owns packaging/deployment, not curriculum content design.
