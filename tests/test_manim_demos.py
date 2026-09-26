"""Static checks for the optional Manim teaching demos.

These checks deliberately do not import Manim: the core numerical test suite
must remain runnable without a graphics stack.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path


DEMO = Path(__file__).parents[1] / "demos" / "manim" / "sysid_demos.py"


def _source() -> str:
    return DEMO.read_text(encoding="utf-8")


def test_manim_demo_is_syntax_valid_without_optional_dependency():
    tree = ast.parse(_source(), filename=str(DEMO))
    classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    assert {
        "L0MismatchDemo",
        "L0FitLandsDemo",
        "L0FitWalkDemo",
        "L0FitRobustDemo",
        "L1BoundaryDemo",
        "L1PhaseDemo",
        "L1HeldOutDemo",
        "L0HeldOutDemo",
        "L1FrictionDemo",
        "L0ExcitationDemo",
    } <= classes


def test_manim_scenes_only_call_helpers_the_module_defines():
    """Guard against a helper being deleted while every scene still calls it.

    A line-range edit once removed two shared loaders and ``py_compile`` still
    passed: a module-level call resolves at call time, so the loss only surfaced
    when those scenes were rendered, minutes later.
    """

    source = _source()
    called = set(re.findall(r"\b(_[a-z0-9_]+)\s*\(", source))
    defined = set(re.findall(r"^def (_[a-z0-9_]+)", source, flags=re.M))
    assert not (called - defined), f"undefined helpers referenced: {sorted(called - defined)}"


def test_manim_demo_reuses_numerical_lesson_modules():
    source = _source()
    assert "from synthetic.l0_inertia_damping import" in source
    assert "from synthetic.l1_servo_loaded_pendulum import run_l1" in source
    assert "run_l0()" in source
    assert "run_l1()" in source


CLIP_STEMS = (
    "l0-mismatch",
    "l0-fit-lands",
    "l0-fit-walk",
    "l0-fit-robust",
    "l1-boundary",
    "l1-phase",
    "l1-heldout",
    "l0-heldout",
    "l1-friction",
    "l0-excitation",
)


def test_rendered_clips_are_present_and_embedded_in_their_lesson_pages():
    repo = DEMO.parents[2]
    rendered = repo / "demos" / "manim" / "rendered"

    for stem in CLIP_STEMS:
        assert (rendered / f"{stem}.mp4").is_file(), f"missing clip {stem}.mp4"
        assert (rendered / f"{stem}.png").is_file(), f"missing poster {stem}.png"
        assert (rendered / f"{stem}.mp4").stat().st_size > 0

    course_map = (repo / "docs" / "course" / "index.html").read_text(encoding="utf-8")
    assert 'id="lessons"' in course_map
    assert "<video" not in course_map
    for stem in CLIP_STEMS:
        lesson_id = "l0-e" if stem == "l0-excitation" else "l0" if stem.startswith("l0") else "l1"
        lesson = (repo / "docs" / "lessons" / lesson_id / "index.html").read_text(encoding="utf-8")
        assert f"rendered/{stem}.mp4" in lesson
        assert f"rendered/{stem}.png" in lesson


def test_fitting_journey_artifact_backs_the_fitting_clip():
    """The fitting clip draws from a checked-in artifact, so guard both halves."""

    repo = DEMO.parents[2]
    artifact = repo / "reports" / "l0_inertia_damping" / "fitting_paths.json"
    assert artifact.is_file(), "missing fitting_paths.json"
    assert (repo / "reports" / "l0_inertia_damping" / "fitting_landscape.png").is_file()

    journey = json.loads(artifact.read_text(encoding="utf-8"))
    assert journey["paths"], "artifact records no optimizer paths"
    # Every recorded path must end on the Oracle, which is the clip's claim.
    for path in journey["paths"]:
        assert path["converged"], f"path from {path['start']} did not reach the truth"
    assert "fitting_paths.json" in (DEMO.parent / "README.md").read_text(encoding="utf-8")


def test_manim_is_not_a_core_runtime_dependency():
    requirements = (DEMO.parents[2] / "requirements.txt").read_text(encoding="utf-8")
    assert "manim" not in requirements.lower()
    assert "manimgl" not in requirements.lower()
