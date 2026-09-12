# Visual Learning Experience and Interactive Lab Delivery

This document defines how `robot-sysid-lab` should present its knowledge and experiments to robotics engineers.

The project should remain Git- and Markdown-friendly, but the primary learning experience should not be limited to reading long Markdown pages. System identification is unusually well suited to visual and interactive explanation: delay is easier to understand when phase visibly moves, friction is easier to understand as a force-velocity curve, identifiability is easier to understand as a changing loss landscape, and whole-robot model mismatch is easier to understand when Oracle and Student rollouts are synchronized side by side.

The intended direction is therefore:

```text
Markdown as source of truth
        +
visual diagrams and generated figures
        +
interactive executable labs
        +
experiment reports with synchronized robot rollouts
        =
Robot SysID Lab learning experience
```

The website or notebook technology is an implementation detail. The important design decision is that **visual explanation and interaction are first-class teaching tools rather than decorative additions**.

## 1. Three layers of presentation

The project should eventually expose three complementary surfaces.

### Layer 1 — Knowledge site

Purpose: explain concepts and connect them to the experimental ladder.

Typical content:

- short conceptual explanations;
- equations only where they improve understanding;
- block diagrams and signal-flow diagrams;
- static plots generated from canonical examples;
- short videos/GIFs for dynamic phenomena;
- links into executable labs and benchmark reports.

A documentation-site generator such as MkDocs Material is a strong initial candidate because the repository already uses Markdown and because it can preserve readable source files while adding navigation, search, math rendering, diagrams, media, and custom interactive elements.

This is a recommended implementation path, not a permanent dependency contract. The content should remain portable.

### Layer 2 — Interactive labs

Purpose: let engineers manipulate the concepts rather than only read about them.

Examples:

```text
change delay
  -> observe time-domain lag
  -> observe phase change

change friction model
  -> observe force-velocity curve
  -> observe tracking residual

change excitation
  -> observe state coverage
  -> observe loss landscape / identifiability

change Student model class
  -> observe compensation and validation failure
```

A reactive Python notebook environment such as Marimo is a strong candidate for these labs because parameter controls can trigger simulation and plot updates while remaining close to normal Python source. Jupyter remains a valid alternative where ecosystem compatibility is more important.

Again, the requirement is the interactive experience, not a specific notebook product.

### Layer 3 — Experiment reports

Purpose: present actual benchmark runs rather than generic teaching examples.

Reports should combine:

- Oracle configuration and hidden truth summary;
- Student model and identified parameters;
- scalar metrics;
- diagnostic plots;
- synchronized Oracle / nominal / identified rollouts;
- contact and gait visualization;
- prediction-horizon analysis;
- failure cases;
- downstream controller or RL evaluation.

This layer is described in more detail in `05_visualization_and_reporting.md`.

## 2. Explain -> Show -> Interact

Important knowledge pages should follow a simple teaching pattern whenever possible:

```text
Explain
   ↓
Show
   ↓
Interact
```

### Explain

Use the minimum theory needed to state the phenomenon precisely.

For example, command delay may be introduced as:

```text
u_applied(t) = u_command(t - tau)
```

The page should then immediately connect the equation to an observable consequence rather than adding several paragraphs of abstraction.

### Show

Provide a visual representation of the consequence:

- command and response over time;
- phase response;
- robot motion;
- force/velocity relationship;
- residual pattern;
- parameter landscape.

### Interact

Where the concept benefits from experimentation, allow the reader to change one or two meaningful quantities and observe the result.

The interaction should be intentionally constrained. A teaching widget with three carefully selected controls is usually more useful than exposing every simulator parameter.

## 3. Canonical visual teaching examples

### 3.1 Delay

A delay lesson should combine:

1. command and response time series;
2. a visible time offset;
3. frequency-domain phase response;
4. an interactive delay control.

The reader should be able to move from zero delay to a meaningful delay and see that delay is not merely a scalar trajectory-error term: it changes phase and therefore interacts strongly with feedback bandwidth.

### 3.2 Friction

A friction lesson should combine:

- actuator/joint schematic;
- friction torque versus velocity;
- Coulomb, viscous, Stribeck, and asymmetric variants;
- tracking trajectory;
- residual versus velocity;
- direction reversal.

A useful interaction is to select a Student friction model while the Oracle remains fixed. The page can then show how a simpler Student model may fit one operating region while leaving structured residuals elsewhere.

### 3.3 Saturation and velocity-dependent torque limits

The page should show both the requested command and the actually available actuator output.

Useful visuals include:

```text
requested torque vs applied torque
available torque vs joint velocity
trajectory error near saturation
```

This is particularly important for small servo robots where actuator limitations can dominate whole-robot behavior.

### 3.4 Identifiability

Identifiability should be taught visually rather than only through matrix terminology.

For two selected parameters, show a two-dimensional loss landscape:

```text
loss(theta_1, theta_2)
```

Then allow the reader to switch excitation:

```text
slow sine
chirp
multisine
reversal-rich motion
```

The loss landscape should visibly change from a broad valley to a better localized optimum when the experiment becomes more informative.

This gives a direct intuition for the distinction among:

```text
optimizer failure
model failure
uninformative experiment
```

Sensitivity matrices, singular values, or Fisher-information-like diagnostics can be introduced after this visual intuition exists.

### 3.5 Model mismatch

A model-mismatch page should keep one Oracle fixed and allow the Student hypothesis class to change.

Example:

```text
Oracle:
Stribeck + load dependence + delay + backlash

Students:
H1 viscous
H2 viscous + Coulomb
H3 richer friction + delay
H4 + backlash
```

For each Student, show:

- training fit;
- held-out fit;
- residual structure;
- fitted parameter movement;
- optionally a robot or actuator replay.

The goal is to make parameter compensation visible rather than merely stating that it occurs.

## 4. Knowledge pages should map to labs

The knowledge track and synthetic lab track should not evolve independently.

A useful mapping is:

| Knowledge topic | Primary visual/lab |
|---|---|
| inertia and acceleration | 1-DoF excitation comparison |
| damping | decay / frequency response |
| delay | time + phase visualization |
| friction | actuator force-velocity and reversal |
| saturation | requested vs applied actuator output |
| experiment design | excitation coverage + sensitivity |
| identifiability | loss landscape |
| model mismatch | Oracle / Student residual comparison |
| multibody coupling | fixed-base leg synchronized joint plots |
| contact | force vectors, CoP, slip and contact timeline |
| whole-system matching | Microduck Oracle / Student rollout |
| parameter hierarchy | Microban joint/group visualization |
| sim-to-sim | same-command cross-backend divergence |
| sim-to-real methodology | identified model -> policy -> Oracle transfer |

A major concept should ideally have both a readable explanation and at least one executable or recorded experiment demonstrating it.

## 5. Whole-robot pages should be visual stories

Microduck and Microban should not be introduced through large parameter tables or long prose sections.

A whole-robot benchmark page should tell a sequence.

### Step 1 — Show the Oracle

Present the robot and the hidden-world configuration at a high level:

```text
rich actuator
+ delay
+ friction
+ backlash/compliance where applicable
+ rigid-body truth
+ contact truth
```

Do not reveal every numeric truth parameter to the Student pipeline, but the teaching/report surface may reveal them when explaining results.

### Step 2 — Show the nominal Student failure

Use synchronized replay:

```text
Oracle                 nominal Student
[robot]                 [robot]
```

The reader should see the mismatch before seeing a table of metrics.

### Step 3 — Show fitting and diagnosis

Present selected information such as:

- objective improvement;
- fitted parameter movement;
- dominant residuals;
- prediction-horizon improvement.

Avoid implying that optimizer convergence alone proves model correctness.

### Step 4 — Show the identified Student

Prefer a three-way synchronized view where practical:

```text
Oracle        nominal        identified
```

The important visual question is:

> What behavior became more similar, and what mismatch remains?

### Step 5 — Explain the remaining error

Connect the remaining mismatch to:

- joint-level residual plots;
- contact timing;
- base orientation;
- foot trajectory;
- parameter confidence;
- known omitted physics.

This creates a complete visual narrative from model mismatch to diagnosis rather than reducing the experiment to one RMSE number.

## 6. Microduck learning experience

Microduck should be the first complete whole-robot visual benchmark because it has a relatively compact morphology and an existing mjlab/BAM/RL ecosystem.

Recommended visual stories include:

### Fixed-base motion

Show:

- robot animation;
- selected joint command and response;
- Oracle / Student overlays;
- joint residual heatmap;
- parameter group summary.

### Supported stance and load shift

Show:

- body pose;
- foot normal loads;
- CoM projection;
- joint tracking;
- actuator load dependence.

### Locomotion

Show:

- synchronized robot replay;
- base x/y trajectory;
- roll/pitch/yaw;
- foot height;
- gait/contact timeline;
- command tracking;
- prediction-horizon error.

### Cross-task validation

Where later tasks such as sit/stand or stand-up are used, show the motion as a held-out behavioral validation rather than only adding another scalar score.

## 7. Microban learning experience

Microban should extend the same visual language while emphasizing full-body coupling and parameter hierarchy.

Useful visualizations include:

### Robot skeleton / body heatmap

Map a selected metric onto joints or bodies:

```text
position RMSE
velocity RMSE
parameter deviation
parameter uncertainty
sensitivity
residual magnitude
```

Selecting a joint should reveal its detailed trajectory and parameter information.

### Parameter sharing comparison

Compare:

```text
all joints independent
vs
shared actuator base parameters + joint residuals
vs
compact whole-robot effective fit
```

The visualization should show both predictive error and how much parameter complexity each strategy uses.

### Full-body coupling

Use arm motion, squat/load shift, and locomotion examples to show how upper-body movement changes trunk dynamics and foot loading.

The point is not merely that Microban has more joints; it is that a more complete humanoid makes hierarchy, coupling, and shared parameter assumptions visible.

## 8. Diagrams should replace avoidable prose

Many architecture and methodology concepts should be represented by diagrams.

Examples:

### Teacher / Student flow

```text
                 hidden truth
                     |
                     v
command ------> [ ORACLE ]
                     |
                observations
                     |
                     v
                  DATASET
                     |
             +-------+-------+
             |               |
             v               v
        Student H1       Student H2
             |               |
             +-------+-------+
                     |
                     v
                 ESTIMATION
                     |
                     v
                 VALIDATION
```

### Hierarchical identification

```text
actuator
   -> fixed-base leg
      -> contact
         -> Microduck
            -> Microban
```

### RL evaluation protocol

```text
Oracle + collection policy
          |
          v
      frozen dataset
          |
          v
   identify Student
          |
          v
train new policy in Student
          |
          v
     test in Oracle
```

Mermaid can be useful for maintainable diagrams, while carefully designed SVG or generated figures should be used where the visual encoding matters more than easy source editing.

## 9. Video and animation are first-class artifacts

Dynamic robot behavior should normally be shown dynamically.

For whole-robot results, prefer an immediate visual comparison such as:

```text
Before SysID                 After SysID

[Oracle vs nominal]          [Oracle vs identified]
```

Short loops are useful for documentation landing pages. Full synchronized videos belong in benchmark reports.

Videos should be accompanied by quantitative plots so visual similarity is not mistaken for rigorous validation.

Recommended dynamic artifacts include:

- side-by-side synchronized replay;
- Oracle / nominal / identified three-way replay;
- ghost overlay where technically practical;
- contact-vector overlay;
- dynamic residual annotations;
- failure-case replay.

## 10. Interactive controls should answer a question

Interactive pages should not expose controls simply because parameters exist.

A good interaction asks a concrete question:

```text
What happens to phase as delay increases?
Which excitation separates inertia from damping?
What residual appears when backlash is omitted?
How long does prediction remain accurate after identification?
```

Then expose only the controls needed to explore that question.

This avoids building simulator configuration panels that are powerful but poor teaching tools.

## 11. Markdown remains the source of truth

The project should retain Markdown for durable knowledge content because it is:

- easy to review in pull requests;
- readable directly on GitHub;
- portable across documentation tools;
- easy for engineers to edit;
- friendly to version control.

The intended relationship is:

```text
Markdown source
    -> documentation build
       -> diagrams / plots / media
          -> optional embedded interaction
```

The rendered site is the primary consumption surface, while Markdown remains a robust fallback and authoring format.

## 12. Recommended initial technology path

### Documentation site

Initial recommendation:

```text
MkDocs Material
+ Markdown
+ math rendering
+ Mermaid/SVG
+ generated PNG/SVG plots
+ embedded image/video assets
```

Why this is attractive:

- minimal migration from the current repository;
- GitHub-friendly source;
- good navigation and search;
- supports a gradual transition from static content to richer pages;
- avoids introducing a full custom frontend before the experiments exist.

This should be treated as a pragmatic starting point rather than a permanent architectural constraint.

### Interactive labs

Initial candidates:

```text
Marimo
or
Jupyter
```

Marimo is particularly attractive for parameter-slider -> simulation -> plot workflows and source-code-friendly review. Jupyter remains useful for interoperability and exploratory analysis.

The project should select one after the first executable lab clarifies the actual requirements.

### Robot visualization

Prefer reusing MuJoCo/mjlab rendering and viewer capabilities before building custom 3D rendering infrastructure.

The first whole-robot reporting milestone should prioritize:

```text
synchronized rendered video
+ synchronized plots
+ timeline controls in the report
```

A custom browser 3D renderer is not required to make the benchmark visually useful.

## 13. Progressive delivery plan

The learning experience should grow with the benchmark rather than becoming a separate website project.

### UX V0 — Markdown specification

Current stage.

Deliver:

- knowledge structure;
- lab roadmap;
- experiment protocols;
- visualization/reporting specification.

### UX V1 — documentation site

Add:

- MkDocs-style navigation;
- math;
- diagrams;
- canonical generated figures;
- images and short videos.

At this stage the content is still mostly static, but it should already be substantially easier to consume than raw Markdown files.

### UX V2 — interactive 1-DoF and actuator labs

Introduce the first executable teaching pages.

Prioritize:

- delay;
- friction;
- excitation;
- identifiability;
- model mismatch.

These labs should establish the interaction design language before whole-robot interactive work begins.

### UX V3 — Microduck and Microban reports

Add:

- synchronized rollout comparison;
- robot videos;
- gait/contact visualization;
- joint/body heatmaps;
- prediction-horizon exploration;
- experiment-run navigation.

### UX V4 — integrated Robot SysID Lab portal

Only after the content and experiments justify it, consider a more integrated portal combining:

```text
Learn
Labs
Benchmarks
Reports
```

A custom frontend should be introduced only if the documentation + interactive-lab architecture becomes a real limitation.

## 14. Suggested top-level information architecture

A rendered site could eventually expose:

```text
Robot SysID Lab
|
+-- Learn
|   +-- Why SysID?
|   +-- SysID fundamentals
|   +-- Robot dynamics
|   +-- Actuator models
|   +-- Experiment design
|   +-- Identifiability
|   +-- Estimation
|  