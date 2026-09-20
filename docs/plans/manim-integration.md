# Manim integration plan

## Goal

Add a small, reproducible animation layer for the course. Manim will explain
the physical and signal-flow intuition behind a lesson with short pre-rendered
clips. The existing Marimo apps remain the interactive surfaces, and the
numerical modules remain the only source of experiment data.

## Scope for the first slice

The first slice contains two scenes in `demos/manim/sysid_demos.py`:

- `L0MismatchDemo`, `L0FitLandsDemo`, `L0FitWalkDemo`, and
  `L0FitRobustDemo`: load the L0 run and introduce
  `J*qdd + b*qd = u`, animates a one-joint arm, and reveals the fit trajectory
  with the existing Oracle / Initial / Identified color convention.
- `L1BoundaryDemo`, `L1PhaseDemo`, and `L1HeldOutDemo`: load the L1 run and animate the
  `q_des -> PD -> delay -> pendulum` boundary, and compares Oracle, zero-delay
  Initial, and Identified validation motion.

Both scenes are offline media generators. They do not expose sliders or fit in
response to playback. Their deterministic scene setup calls the existing lesson
run builders to obtain the same recorded trajectories used by the reports.

## Architecture

```text
synthetic/l0_inertia_damping.py  ─┐
synthetic/l1_servo_loaded_pendulum.py ─┼─> Manim scene ─> MP4 / still frame
                                      └─> Marimo / report / notebook
```

The Manim package is optional. It belongs in the demo instructions, not in
`requirements.txt`, because course computation and CI must continue to work in
a CPU-only environment without OpenGL, FFmpeg, or LaTeX.

The first implementation targets ManimGL from
[`3b1b/manim`](https://github.com/3b1b/manim), whose package name is
`manimgl`. The scene code should avoid version-specific interactive embeds and
use the stable primitives needed for this media slice: `Scene`, `Text`/`Tex`,
`Line`, `VMobject`, `Dot`, `ValueTracker`, and file rendering.

## Delivery steps

1. Add the two scenes and a short README with installation, render commands,
   expected outputs, and the optional dependency boundary.
2. Make the scenes read only completed run objects from the existing numerical
   modules. Keep the three role colors and clearly label L1 delay as an
   effective boundary parameter.
3. Add static source checks that do not import Manim: Python compilation,
   scene-name checks, and verification that both scenes reference the shared
   numerical modules.
4. Render a low-resolution smoke clip in an environment with `manimgl`, when
   available. The repository-level acceptance gate remains source validation
   plus the existing numerical test suite; rendering is an optional media
   gate because the package needs system graphics dependencies.
5. Link the demo instructions from the synthetic lab README and use the clips
   in lessons only after a maintainer has reviewed the visual timing and text.

## Acceptance criteria

- `python -m py_compile demos/manim/sysid_demos.py` passes without installing
  Manim.
- The source contains both named scenes and imports `run_l0` and `run_l1` from
  the checked-in numerical implementations.
- With `manimgl` installed, both scenes render with the documented commands and
  produce a video plus a final-frame image.
- L0 shows the equation, a moving one-joint body, and the three existing model
  roles over recorded fit data.
- L1 shows the command boundary, the hidden command buffer made visible, an
  explicit delay marker, and the three existing model roles over held-out
  validation data. The machine view appears **once, at the start**, to say which
  machine the lesson is about, and then leaves the frame. That departure is the
  argument, not a transition: the lesson's own checkpoint is that the static
  schematic is a snapshot and does not show the command buffer, so the clip
  deliberately does not send the viewer looking for the answer in the arm
  geometry. A machine view is used elsewhere only where the machine *is* the
  evidence, as in L0's side-by-side mismatch.
- No scene exposes a fitter, changes configuration, or claims that the clip is
  an interactive simulation.

## Non-goals and follow-up

This slice does not build a browser renderer, a generic animation framework, a
timeline scrubber, a Manim-backed Marimo widget, or whole-robot rendering.
L1's recorded-state playback remains the responsibility of the existing lesson
surface. If the clips prove useful, later work can add a loss-landscape scene
for identifiability and a friction scene, each backed by a concrete lesson
question and stored benchmark output.

## Verification commands

```bash
python -m py_compile demos/manim/sysid_demos.py
python -m pytest -q

# Optional media environment (requires FFmpeg/OpenGL/Pango; LaTeX is optional)
python -m pip install manimgl
manimgl demos/manim/sysid_demos.py L0MismatchDemo -w -ql
manimgl demos/manim/sysid_demos.py L1BoundaryDemo -w -ql
```
