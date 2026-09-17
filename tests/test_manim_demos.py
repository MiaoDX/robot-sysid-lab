"""Static checks for the optional Manim teaching demos.

These checks deliberately do not import Manim: the core numerical test suite
must remain runnable without a graphics stack.
"""

from __future__ import annotations

import ast
from pathlib import Path


DEMO = Path(__file__).parents[1] / "demos" / "manim" / "sysid_demos.py"


def _source() -> str:
    return DEMO.read_text(encoding="utf-8")


def test_manim_demo_is_syntax_valid_without_optional_dependency():
    tree = ast.parse(_source(), filename=str(DEMO))
    classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    assert {"L0InertiaDampingDemo", "L1CommandDelayDemo"} <= classes


def test_manim_demo_reuses_numerical_lesson_modules():
    source = _source()
    assert "from synthetic.l0_inertia_damping import run_l0" in source
    assert "from synthetic.l1_servo_loaded_pendulum import run_l1" in source
    assert "run_l0()" in source
    assert "run_l1()" in source


def test_manim_is_not_a_core_runtime_dependency():
    requirements = (DEMO.parents[2] / "requirements.txt").read_text(encoding="utf-8")
    assert "manim" not in requirements.lower()
    assert "manimgl" not in requirements.lower()

