# Manim teaching demos

These are optional, offline clips for the course. They read the existing L0
and L1 numerical runs; they do not replace Marimo's interactive controls or
the checked-in reports.

The scenes target [ManimGL from `3b1b/manim`](https://github.com/3b1b/manim).
The package is intentionally not part of the core requirements because it
needs a graphics stack (FFmpeg/OpenGL/Pango and a LaTeX distribution).

The rendered clips are checked in under [`rendered/`](rendered) and embedded in
the [course map](../../docs/course/index.html#clips), so you only need this
setup if you want to change a scene and re-render.

## Environment

ManimGL is rendered here through `uv`, which keeps it out of the CPU-only
course environment:

```bash
uv venv .venv-manim --python 3.11
uv pip install --python .venv-manim/bin/python manimgl "setuptools<81"
```

`setuptools<81` is required: ManimGL imports `pkg_resources`, which
setuptools 81 removed.

System packages. ManimGL needs OpenGL and Pango, and the L0 scene typesets one
equation with `Tex`, so a LaTeX distribution is required as well:

```bash
sudo apt-get install --no-install-recommends \
  ffmpeg \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-recommended texlive-fonts-extra tipa texlive-science dvisvgm
```

`texlive-fonts-extra` is large (about 1.3 GB installed) and is only needed
because ManimGL's stock preamble loads `dsfont`. Dropping `Tex` from the L0
scene in favour of `Text` would remove the entire LaTeX requirement.

There is no display on a headless machine, and ManimGL opens a GL context at
import time, so render under `xvfb-run`:

```bash
xvfb-run -a -s "-screen 0 1280x720x24" \
  .venv-manim/bin/manimgl demos/manim/sysid_demos.py L0MismatchDemo \
  -w -m --video_dir demos/manim/rendered
```

Use `-m` for 720p or `-l` for 480p; `-s` writes a single final frame instead of
a movie. Rendering the seven clips takes a few minutes on CPU at 720p; invoke
each scene by name as shown in the table below.

## Scenes

Each clip answers exactly one question and carries its own title, so it stands
alone wherever it is embedded. Blocks that share data share a loader
(`_l0_lesson_data`, `_l0_journey_data`, `_l1_delay_data`), so two viewings of
the same run cannot disagree about the numbers or the axis.

| Scene | Clip | Question it answers |
|---|---|---|
| `L0MismatchDemo` | `rendered/l0-mismatch.mp4` | What does the mismatch look like? |
| `L0FitLandsDemo` | `rendered/l0-fit-lands.mp4` | Did fitting actually fix it? |
| `L0FitWalkDemo` | `rendered/l0-fit-walk.mp4` | How does the fit get there? |
| `L0FitRobustDemo` | `rendered/l0-fit-robust.mp4` | Was that one lucky starting guess? |
| `L1BoundaryDemo` | `rendered/l1-boundary.mp4` | Where does the delay hide? |
| `L1PhaseDemo` | `rendered/l1-phase.mp4` | Why does a chirp make it visible? |
| `L1HeldOutDemo` | `rendered/l1-heldout.mp4` | Did the fit predict held-out motion? |

`L0FitWalkDemo` reads `reports/l0_inertia_damping/fitting_paths.json` and
`fitting_landscape.png` rather than re-running the optimizer, so the route it
draws is the recorded one. Regenerate both with the normal L0 report command:

```bash
python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping
```

That writes the cost landscape (scored with the same normalized residual the
fitter uses) plus the iterate path from each start in `DEFAULT_JOURNEY_STARTS`.
Consecutive duplicate iterates are collapsed for display; nothing between
recorded iterates is interpolated.

Both scenes call `run_l0()` / `run_l1()` and reuse the lesson's `simulate()`
helper for the per-model traces, so the numbers come from the same code path as
the reports. Two things are worth knowing before editing them:

- **Oracle and Identified are the same trace to machine precision** in both labs,
  so the Identified line covers the Oracle one. The clips say this out loud
  rather than drawing a third, invisible curve.
- **Curves in a panel share one vertical axis** (`_plot_curve(..., scale=...)`),
  which is what makes their amplitudes comparable. Stretching each curve to its
  own box instead makes a badly mismatched model look like a mild lag — in L0 it
  hides an Initial-model excursion of 17.6 rad against the Oracle's 7.6 rad.

The role colours follow the reports, except that the Oracle line is ManimGL's
`WHITE` rather than the report's `#17211b`. Neither scene exposes a fitter or
changes configuration.

ManimGL's default frame is 14.22 x 8.0, so geometry must stay inside roughly
`x` in +/-7.1 and `y` in +/-4.0. Anything outside that box renders off-screen and
disappears silently.

## Checks

`tests/test_manim_demos.py` validates the scene source without importing
ManimGL, so the core suite still runs without a graphics stack. It also asserts
that the rendered clips and their course-map embed are present.
