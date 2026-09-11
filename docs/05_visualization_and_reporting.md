# Visualization and Reporting Strategy

Visualization is a first-class part of this project, not a presentation layer added after fitting. The purpose of the synthetic lab is not only to produce lower scalar losses, but to help engineers understand **where a model is right, where it is wrong, why an experiment is informative, and whether the identified model improves downstream robot behavior**.

A benchmark run should therefore produce a reusable research artifact:

```text
Dataset
+ fitted parameters
+ scalar metrics
+ diagnostic plots
+ synchronized rollout visualizations
+ comparison report
```

A run that reports only a best parameter vector or a single validation loss is incomplete.

## 1. Visualization layers

The project should use a common visualization language from the 1-DoF lab through Microduck and Microban.

### V1 — signal tracking

Question:

> Does the student reproduce the measured signals produced by the Oracle?

Canonical plots:

- command versus measured response;
- Oracle versus nominal student versus identified student;
- joint position and velocity;
- torque/current where available;
- base pose and velocity for floating-base robots;
- contact force and contact state for contact experiments.

For a position-controlled joint, a useful default plot is:

```text
q_des
q_oracle
q_nominal
q_identified
```

This immediately exposes effects such as delay, tracking bandwidth, saturation, damping, and friction.

### V2 — dynamics and residual diagnostics

Question:

> What structure remains in the model error?

Define the residual

```text
e(t) = y_oracle(t) - y_student(t)
```

and make residual diagnostics standard outputs rather than optional debug plots.

Useful views include:

- residual versus time;
- residual versus position;
- residual versus velocity;
- residual versus acceleration;
- residual versus command/estimated torque;
- residual versus motion direction;
- residual spectrum.

These plots should be interpreted as model-diagnosis tools. Examples:

- velocity-correlated residuals suggest damping/friction mismatch;
- direction-dependent offsets suggest asymmetric or Coulomb friction;
- zero-velocity structure suggests stiction/Stribeck/backlash effects;
- frequency-localized residuals suggest a missing dynamic mode or delay/bandwidth mismatch.

### V3 — parameter and identifiability visualization

Question:

> Why can or cannot the parameters be recovered from this experiment?

Synthetic truth makes parameter visualization especially valuable because the hidden ground truth is known.

Standard views should include:

- true versus nominal versus fitted parameter values;
- normalized parameter error;
- parameter estimates across repeated datasets/seeds;
- sensitivity summaries;
- parameter correlation;
- singular-value spectra for local sensitivity matrices where applicable;
- 2-D loss slices/contours for selected parameter pairs.

For a parameter theta_i, a cross-model normalized error can be reported as

```text
(theta_hat_i - theta_true_i) / parameter_range_i
```

rather than mixing quantities with incompatible physical units in one raw-error plot.

A 2-D loss landscape is particularly useful when two parameters compensate for one another. Long flat valleys should be treated as visual evidence of practical non-identifiability, not as an optimizer problem alone.

### V4 — robot behavior visualization

Question:

> How does the model mismatch change the actual robot motion?

Whole-robot benchmarks need more than joint curves. Standard outputs should include synchronized robot rollouts and task-level visual diagnostics.

Important views:

- Oracle/Student side-by-side video;
- Oracle/nominal/identified three-way comparison;
- optional ghost overlay where Oracle and Student share one camera frame;
- base trajectory;
- center-of-mass trajectory;
- left/right foot trajectories;
- contact timing and gait diagram;
- contact-force vectors where useful;
- joint-local error overlays/heatmaps;
- failure-case replay.

### V5 — benchmark comparison

Question:

> Which model or experiment is better, and under what conditions?

This level compares model classes, excitation choices, observation sets, optimizers, prediction horizons, and downstream control results.

The benchmark summary should combine scalar metrics with links to the detailed visual evidence that explains them.

## 2. Time-domain plots

Every dynamic experiment should produce synchronized time-series plots with common timestamps and explicit units.

Recommended signals include, depending on the lab:

```text
command
joint position
joint velocity
joint acceleration / estimate
actuator torque/current
controller output
base pose
base velocity
foot pose
contact force
contact state
```

For each signal, distinguish at least:

```text
Oracle
nominal Student
identified Student
```

Fit-set and validation-set plots must be visually distinguishable in the report. A model should never look successful only because the report shows the training trajectory.

## 3. Phase-space and hysteresis plots

Time traces can hide important dynamics. Add phase-space views where they expose structure more directly.

Examples:

- q versus qd;
- qd versus estimated friction torque;
- actuator command versus response;
- motor-side versus output-side displacement for backlash/compliance;
- loading versus unloading trajectories for hysteresis.

These are especially important in the actuator benchmark because friction, backlash, and compliance can produce loops that are hard to diagnose from MAE alone.

## 4. Frequency-domain visualization

Chirp and multisine experiments should automatically produce frequency-domain outputs.

Default views:

- FRF/Bode magnitude;
- FRF/Bode phase;
- input spectrum;
- output spectrum;
- residual spectrum.

Compare Oracle, nominal Student, and identified Student on the same axes.

Frequency-domain diagnostics are particularly useful for:

- command/measurement delay;
- closed-loop bandwidth mismatch;
- damping;
- resonance and anti-resonance;
- compliance/flexible modes;
- insufficient model order.

A time-domain model that looks visually close on one trajectory can still have a clear phase or bandwidth mismatch. The report should make that easy to see.

## 5. Excitation coverage visualization

Experiment design is part of SysID, so each excitation benchmark should visualize what part of state/input space was actually explored.

Useful views include:

- q versus qd coverage;
- velocity histograms;
- acceleration histograms;
- command/torque histograms;
- input frequency spectrum;
- posture distribution;
- load distribution;
- contact/no-contact occupancy where relevant.

For comparing excitation families such as slow sine, chirp, multisine, reversal, and PRBS-like inputs, add a sensitivity summary showing which parameters the experiment excites strongly or weakly.

An illustrative reporting layout could be:

```text
                 inertia   friction   delay   backlash
slow sine           low       high      low       low
chirp               high      med       high      low
reversal            low       high      med       high
multisine           high      med       high      med
```

The metric behind this table should be defined explicitly; the visualization must not imply more certainty than the chosen sensitivity proxy provides.

## 6. Parameter recovery and stability

Synthetic experiments should take advantage of known truth.

Every matched-structure benchmark should report:

```text
parameter
truth
nominal
fitted
absolute error
normalized error
```

In addition, plot parameter estimates across:

- repeated random seeds;
- different fit trajectories;
- different excitation families;
- different operating conditions.

A parameter that changes dramatically across datasets may indicate model mismatch or poor identifiability even if every individual trajectory is fitted well.

For mismatched teacher/student model classes, parameter-recovery plots should be labeled carefully. Effective simulator parameters are not expected to recover nonexistent one-to-one physical truth.

## 7. Contact visualization

Contact experiments need dedicated visual outputs.

Recommended quantities:

- contact/no-contact state over time;
- normal force;
- tangential force;
- slip velocity;
- foot height;
- center of pressure where the contact model supports a meaningful definition;
- contact-point or resultant-force visualization in the rendered scene.

Useful synchronized rendering overlays include:

```text
normal force vector
friction/tangential force vector
contact point/resultant location
foot slip indicator
```

For whole robots, add a gait/contact diagram:

```text
time ------------------------------------------------->
Oracle L:   ######       ######
Oracle R:      #######       ######
Student L:  ######        ######
Student R:     #######        ######
```

This makes touchdown, liftoff, duty-factor, and double-support differences immediately visible.

## 8. Floating-base and whole-body plots

Microduck and Microban reports should include a consistent set of whole-body metrics.

At minimum:

- base x/y/z position;
- base roll/pitch/yaw or another well-defined orientation representation;
- base linear/angular velocity;
- center-of-mass path;
- left/right foot path and height;
- joint errors grouped by limb;
- contact timing;
- commanded versus achieved task velocity for locomotion.

Top-down x/y trajectories are useful for showing heading and drift. Foot-height plots and gait diagrams are useful for showing contact timing. Base roll/pitch traces are useful for exposing balancing differences that a mean joint-position metric can hide.

## 9. Synchronized rollout comparison

Whole-robot visualization should provide a standard side-by-side comparison mode.

Suggested layout:

```text
Oracle                Student
+----------------+    +----------------+
| synchronized   |    | synchronized   |
| robot rollout  |    | robot rollout  |
+----------------+    +----------------+

same simulation time
same camera convention
same command segment
```

A three-way mode can compare:

```text
Oracle | nominal Student | identified Student
```

The viewer/report should show useful synchronized diagnostics alongside the video, for example:

- current command;
- base pose error;
- selected joint error;
- left/right contact state;
- task tracking error.

This should be treated as an engineering diagnostic, not merely a demo video.

## 10. Ghost overlay

Where rendering infrastructure makes it practical, provide a ghost-overlay view in which Oracle and Student configurations are rendered from the same camera and reference frame.

Typical use:

```text
Oracle: opaque
Student: semi-transparent
```

This can reveal small differences in:

- torso pitch;
- knee flexion;
- swing-foot height;
- foot touchdown timing;
- head/arm movement;
- accumulated drift.

If the two rollouts use different floating-base frames, the report must state whether the overlay is world-aligned, root-aligned, or otherwise registered. Alignment must not silently remove an error that is relevant to the benchmark.

## 11. Dynamic joint/body error visualization

For Microduck and Microban, provide a way to localize error spatially on the robot.

Possible overlays:

- joint position RMSE;
- velocity RMSE;
- torque residual;
- fitted friction/residual parameter;
- parameter uncertainty;
- current frame joint error.

A robot skeleton/body heatmap is often more readable than a 19-row Microban table when the question is simply "where is the mismatch concentrated?"

For dynamic replay, selected joints may display current signed error values near the joint.

## 12. Prediction-horizon visualization

Protocol A in the Oracle experiment design replays fixed Oracle commands through Student models. This naturally supports a prediction-horizon benchmark.

For a rollout initialized at t_0, define an error metric as a function of horizon h:

```text
E(h) = error between Oracle and Student after predicting h seconds
```

Plot E(h) for:

```text
nominal Student
intermediate model classes
identified Student
```

This answers a useful question:

> How long does the model remain predictively accurate before errors compound?

This is more informative than a single long-trajectory RMSE.

Because contact systems can diverge rapidly after a small timing difference, prediction-horizon curves should be paired with state/contact visualizations rather than interpreted alone.

## 13. Multiple-shooting visualization

When fitting uses multiple short prediction windows, visualize the fitting protocol itself.

Example:

```text
Oracle trajectory:
------------------------------------------------------

Student windows:
|------|
      |------|
            |------|
                  |------|
```

Report endpoint/window errors as a function of horizon and starting condition.

The report must state how Student hidden/internal states are initialized at each window. Privileged Oracle-state initialization and realistic history-based initialization are different benchmarks and should never be silently mixed.

## 14. RL/control visualization

For Protocol B and Protocol C, add controller/task visualizations beyond physics prediction.

Recommended plots:

- commanded versus achieved linear/angular velocity;
- task error versus time;
- policy action/joint target traces;
- base stability metrics;
- foot slip/contact metrics;
- termination/fall events;
- task success rate across episodes;
- reward decomposition when RL reward is used.

Reward decomposition is preferred over total reward alone. It should be possible to see whether a model changes performance through velocity tracking, posture, action smoothness, energy, slip, or another component.

For transfer studies, include representative failure replays instead of reporting only an aggregate success percentage.

## 15. Failure-case reporting

The report should automatically surface interesting failures.

Candidate selection criteria include:

- largest trajectory error;
- earliest fall;
- largest contact-timing mismatch;
- worst held-out condition;
- largest parameter-recovery failure;
- strongest residual structure.

For every aggregate benchmark, keep enough per-episode information to inspect both representative and worst-case rollouts.

A model that improves the mean but creates a new catastrophic failure mode must not hide that failure behind a scalar average.

## 16. Standard visualization suite per lab

The following should be treated as a baseline rather than an exhaustive list.

| Lab | Required/core visualizations |
|---|---|
| 1-DoF | time-series overlay, residual, phase plot, selected loss landscape, FRF when frequency excitation is used |
| Actuator | command/response, friction versus velocity, hysteresis where relevant, Bode/FRF, parameter recovery/stability |
| Fixed-base leg | per-joint tracking, coupling residuals, posture-conditioned residuals, sensitivity/correlation views |
| Contact leg | contact timing, force/slip plots, foot/contact rendering overlays, contact-parameter diagnostics |
| Microduck | synchronized rollout, gait diagram, base/foot trajectories, joint-local error visualization, task tracking |
| Microban | synchronized whole-body rollout, joint/body heatmap, parameter-sharing comparison, whole-body coupling views, task tracking |
| Sim-to-sim | same-command rollout divergence, prediction-horizon curves, cross-backend residual comparison |
| RL/control transfer | task tracking, stability/fall statistics, reward/task decomposition, representative failure replay |

An experiment is not considered fully reported until the required visualization suite exists for its level.

## 17. Scientist, robotics, and comparison views

The same underlying run may need different presentations for different users.

### Scientist view

Prioritize:

- residual diagnostics;
- FRF;
- loss landscapes;
- parameter sensitivity/correlation;
- uncertainty/stability;
- prediction-horizon plots.

### Robotics view

Prioritize:

- synchronized rollout;
- joint/base trajectories;
- feet/contact timing;
- CoM and body pose;
- robot heatmaps;
- failure replay.

### Comparison view

Prioritize:

- model A/B/C ranking;
- fit and held-out metrics;
- parameter-recovery quality;
- compute cost;
- prediction horizon;
- downstream policy/control performance;
- known failure regimes.

These do not need to be separate software products initially. A generated HTML report can expose the same artifacts in different sections.

## 18. Scalar metrics should have visual explanations

As a design principle, every important scalar metric should have an associated visualization whenever practical.

Examples:

```text
trajectory RMSE
  -> synchronized time-series overlay

friction parameter error
  -> friction-versus-velocity plot

contact timing error
  -> gait/contact timeline

parameter uncertainty
  -> parameter distribution / loss landscape / sensitivity view

prediction error
  -> prediction-horizon curve + rollout

policy success rate
  -> task traces + failure replays
```

This prevents benchmark results from collapsing into small numerical differences that are difficult to interpret physically.

## 19. Run artifact contract

A benchmark run should be self-contained enough to inspect later without rerunning optimization.

A possible structure is:

```text
runs/
  <run_id>/
    config.yaml
    oracle.yaml
    fitted_params.yaml
    metrics.json

    data/
      rollout.parquet
      metadata.json

    plots/
      tracking/
      residuals/
      frequency/
      parameters/
      contact/
      task/

    videos/
      oracle.mp4
      nominal.mp4
      identified.mp4
      side_by_side.mp4
      ghost_overlay.mp4        # optional
      failures/

    report/
      index.html
```

Exact serialization formats can evolve, but the conceptual contract should remain stable:

> preserve inputs, configuration, truth metadata, fitted results, metrics, visual diagnostics, and representative rollouts together.

For synthetic benchmarks, distinguish truth metadata that is exposed to the evaluation/reporting code from observations that were actually available to the identification algorithm.

## 20. Offline plotting versus interactive visualization

Use two layers.

### Offline/static layer

Purpose:

- CI artifacts;
- deterministic benchmark reports;
- papers/notes;
- easy comparison across runs.

Likely tools:

```text
NumPy
Pandas / Arrow/Parquet readers
Matplotlib
```

Generate publication/report-friendly PNG/SVG/PDF-compatible plots where appropriate.

### Interactive layer

Purpose:

- joint/signal selection;
- zoom and time inspection;
- synchronized video/plot scrubbing;
- Oracle/nominal/identified toggles;
- whole-robot debugging.

A generated HTML report is a reasonable target. The first implementation should prefer existing MuJoCo/mjlab rendering infrastructure for robot visualization rather than building a custom WebGL robot renderer prematurely.

The interactive report should enhance, not replace, static benchmark outputs.

## 21. Automated SysID report

A future command such as

```text
sysid report <run>
```

should generate a standard report with sections similar to:

1. Experiment definition
2. Oracle truth and hidden conditions
3. Student observation/model boundary
4. Excitation and state-space coverage
5. Fitted parameters
6. Training trajectories
7. Held-out trajectories
8. Residual diagnostics
9. Frequency-domain diagnostics
10. Identifiability / parameter stability
11. Prediction-horizon / multiple-shooting results
12. Whole-robot rollout comparison
13. Contact/gait analysis where applicable
14. RL/control performance where applicable
15. Representative and worst failure cases
16. Conclusions and known validity limits

The exact report format can evolve, but the ordering should tell a scientific/engineering story rather than display unrelated plots.

## 22. Relationship to the knowledge track

The visualization strategy should directly support team education.

Every major conceptual claim in the knowledge track should have a lab visualization demonstrating it where possible.

Examples:

```text
"delay creates phase lag"
  -> Bode phase + time-domain tracking

"slow excitation hides inertia"
  -> excitation spectrum + sensitivity + parameter recovery

"friction model is incomplete"
  -> residual versus velocity + friction loop

"two parameters compensate"
  -> loss-landscape valley + dataset-dependent fitted values

"contact model is wrong"
  -> contact timing + force/slip visualization

"better SysID improves task transfer"
  -> prediction metrics + policy transfer task results + rollout comparison
```

This mapping is part of the project's teaching value: engineers should be able to connect an abstract SysID concept to a concrete visual failure mode.

## 23. Design principles

1. **Visualization is part of the benchmark contract.** It is not optional report polish.
2. **Always show held-out behavior.** Training-trajectory figures alone are insufficient.
3. **Show commands and responses together.** Output-only plots can hide the cause of mismatch.
4. **Residuals are signals, not only scalar losses.** Preserve their dependence on state, direction, load, frequency, and contact.
5. **Use synthetic truth explicitly.** Plot parameter recovery where the mapping is meaningful.
6. **Do not imply physical meaning for effective parameters.** Label mismatched-model results carefully.
7. **Whole-robot benchmarks need motion visualization.** Curves alone are insufficient for contact and locomotion.
8. **Keep rollouts synchronized and registration explicit.** Do not visually align away meaningful model error.
9. **Surface failure cases.** Aggregate improvements must not hide catastrophic regressions.
10. **Every important scalar should be visually explainable.** Prefer evidence that a robotics engineer can interpret physically.
11. **Static artifacts come first; interactivity is an enhancement.** Benchmark results must remain reproducible without a custom UI.
12. **Reuse simulator rendering infrastructure.** Do not build a bespoke 3-D engine before the benchmark requirements demand it.

## 24. Implementation order

A practical implementation sequence is:

### Phase V0 — static report contract

Implement common plotting helpers for:

- Oracle/Student time-series overlays;
- residual plots;
- parameter truth/estimate comparisons;
- excitation coverage;
- validation summaries.

Use these from the rebuilt 1-DoF and actuator labs.

### Phase V1 — frequency and identifiability diagnostics

Add:

- spectra/FRF;
- loss slices;
- parameter stability/correlation;
- prediction-horizon plots.

### Phase V2 — multibody/contact diagnostics

Add:

- multi-joint grouping;
- contact/gait timelines;
- foot/base trajectories;
- contact-force/slip views.

### Phase V3 — whole-robot synchronized replay

For Microduck and Microban, generate:

- Oracle video;
- nominal video;
- identified video;
- synchronized side-by-side video;
- joint/body error summaries;
- optional ghost overlay.

### Phase V4 — interactive report

Add time scrubbing, signal selection, model toggles, and linked rollout/plot inspection once the static artifact contract has stabilized.

The visualization API should emerge from the concrete labs in the same way as the broader SysID framework: avoid premature generic UI abstraction, but keep output schemas stable enough that later interactive tools can consume old runs.
