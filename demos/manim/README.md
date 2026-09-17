# Manim teaching demos

These are optional, offline clips for the course. They read the existing L0
and L1 numerical runs; they do not replace Marimo's interactive controls or
the checked-in reports.

The scenes target [ManimGL from `3b1b/manim`](https://github.com/3b1b/manim).
The package is intentionally not part of the core requirements because it
needs a graphics stack (FFmpeg/OpenGL/Pango, with LaTeX optional).

From the repository root, in an environment with those system dependencies:

```bash
python -m pip install manimgl
manimgl demos/manim/sysid_demos.py L0InertiaDampingDemo -w -ql
manimgl demos/manim/sysid_demos.py L1CommandDelayDemo -w -ql
```

Use `-qh` or omit `-q` for a larger output. `-s` writes a final-frame image.
The rendered files are placed in Manim's media directory; generated media is
not checked into the repository by default.

The L0 clip explains how inertia and damping shape the recorded fit motion.
The L1 clip makes the effective delay location explicit and compares the
recorded validation trajectories for Oracle, Initial, and Identified models.

