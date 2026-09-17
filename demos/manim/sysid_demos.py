"""Offline ManimGL teaching clips for the Robot SysID Lab.

The scenes intentionally consume the same completed numerical runs as the
reports and Marimo lessons. Install the optional ``manimgl`` package before
rendering; the core repository does not depend on a graphics stack.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manimlib import *


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synthetic.l0_inertia_damping import run_l0
from synthetic.l1_servo_loaded_pendulum import run_l1


ROLE_COLORS = {"oracle": WHITE, "initial": ORANGE, "identified": BLUE}
ROLE_LABELS = {
    "oracle": "True system (Oracle)",
    "initial": "Initial model",
    "identified": "Identified model",
}


def _subsample(values: np.ndarray, limit: int = 260) -> np.ndarray:
    if values.size <= limit:
        return values
    return values[np.linspace(0, values.size - 1, limit).astype(int)]


def _plot_curve(
    times: np.ndarray,
    values: np.ndarray,
    *,
    left: float,
    right: float,
    bottom: float,
    top: float,
    color=WHITE,
    width: float = 3.0,
):
    """Create a simple polyline without depending on a charting extension."""
    times = _subsample(np.asarray(times, dtype=float))
    values = _subsample(np.asarray(values, dtype=float))
    lo, hi = float(np.min(values)), float(np.max(values))
    span = max(hi - lo, 1e-9)
    lo -= 0.08 * span
    hi += 0.08 * span
    x = left + (times - times[0]) / max(times[-1] - times[0], 1e-9) * (right - left)
    y = bottom + (values - lo) / (hi - lo) * (top - bottom)
    curve = VMobject(color=color, stroke_width=width)
    curve.set_points_as_corners([np.array([px, py, 0.0]) for px, py in zip(x, y)])
    curve._sysid_x = x
    curve._sysid_y = y
    return curve


def _curve_point(curve, alpha: float) -> np.ndarray:
    x = np.asarray(curve._sysid_x)
    y = np.asarray(curve._sysid_y)
    position = np.clip(alpha, 0.0, 1.0) * (len(x) - 1)
    index = min(int(position), len(x) - 2)
    frac = position - index
    return np.array(
        [x[index] * (1 - frac) + x[index + 1] * frac,
         y[index] * (1 - frac) + y[index + 1] * frac,
         0.0]
    )


def _plot_frame(title: str, left: float, right: float, bottom: float, top: float):
    frame = Rectangle(
        width=right - left,
        height=top - bottom,
        stroke_color=GREY_B,
        stroke_width=1.5,
    )
    frame.move_to(np.array([(left + right) / 2, (bottom + top) / 2, 0.0]))
    label = Text(title, font_size=25, color=GREY_B)
    label.next_to(frame, UP, buff=0.12)
    return VGroup(frame, label)


def _role_legend(roles, origin=np.array([-6.0, -3.3, 0.0])):
    legend = VGroup()
    for index, role in enumerate(roles):
        mark = Line(ORIGIN, RIGHT * 0.35, color=ROLE_COLORS[role], stroke_width=4)
        text = Text(ROLE_LABELS[role], font_size=20, color=ROLE_COLORS[role])
        row = VGroup(mark, text).arrange(RIGHT, buff=0.12)
        row.move_to(origin + RIGHT * index * 2.7)
        legend.add(row)
    return legend


class L0InertiaDampingDemo(Scene):
    """Explain how inertia and damping shape the recorded L0 motion."""

    def construct(self):
        run = run_l0()
        fit = run.data.fit
        left, right, bottom, top = -5.7, 5.7, -1.55, 2.25
        curves = {
            "oracle": _plot_curve(
                fit.t, fit.q, left=left, right=right, bottom=bottom, top=top,
                color=ROLE_COLORS["oracle"], width=4,
            ),
        }
        # Use the already-defined report contract for the initial and identified traces.
        from synthetic.l0_inertia_damping import simulate
        initial_q, _ = simulate(run.config.nominal, fit.t, fit.u, q0=run.config.q0, qd0=run.config.qd0)
        identified_q, _ = simulate(run.fit.params, fit.t, fit.u, q0=run.config.q0, qd0=run.config.qd0)
        curves["initial"] = _plot_curve(fit.t, initial_q, left=left, right=right, bottom=bottom, top=top, color=ROLE_COLORS["initial"], width=2.3)
        curves["identified"] = _plot_curve(fit.t, identified_q, left=left, right=right, bottom=bottom, top=top, color=ROLE_COLORS["identified"], width=2.7)

        title = Text("L0 · inertia and damping", font_size=40)
        equation = Tex(R"J\ddot q + b\dot q = u", font_size=46)
        subtitle = Text("A short visual bridge from physics to the fit curves", font_size=22, color=GREY_B)
        title.to_edge(UP, buff=0.35)
        equation.next_to(title, DOWN, buff=0.18)
        subtitle.next_to(equation, DOWN, buff=0.12)
        self.play(Write(title), Write(equation), FadeIn(subtitle))

        pivot = Dot(np.array([-8.0, -0.1, 0.0]), color=GREEN)
        arm = Line(pivot.get_center(), pivot.get_center() + RIGHT * 1.6, color=BLUE, stroke_width=8)
        torque = Arrow(pivot.get_center() + UP * 0.75, pivot.get_center() + RIGHT * 0.75, color=YELLOW, buff=0)
        labels = VGroup(
            Text("joint", font_size=20).next_to(pivot, DOWN, buff=0.15),
            Text("applied torque u", font_size=20, color=YELLOW).next_to(torque, UP, buff=0.12),
            Text("larger J → slower acceleration", font_size=21).move_to([-7.4, -1.55, 0]),
            Text("larger b → more velocity loss", font_size=21).move_to([-7.35, -1.95, 0]),
        )
        self.play(FadeIn(pivot), ShowCreation(arm), ShowCreation(torque), FadeIn(labels))

        self.play(Create(_plot_frame("fit position q(t)", left, right, bottom, top)))
        for role in ("oracle", "initial", "identified"):
            self.play(ShowCreation(curves[role]), run_time=0.8)
        self.play(FadeIn(_role_legend(("oracle", "initial", "identified"))))

        tracker = ValueTracker(0.0)
        marker = Dot(color=BLUE, radius=0.07)
        marker.add_updater(lambda dot: dot.move_to(_curve_point(curves["identified"], tracker.get_value())))
        arm.add_updater(
            lambda line: line.put_start_and_end_on(
                pivot.get_center(),
                pivot.get_center() + 1.6 * np.array([
                    np.cos(np.interp(tracker.get_value(), np.linspace(0, 1, fit.q.size), fit.q)),
                    np.sin(np.interp(tracker.get_value(), np.linspace(0, 1, fit.q.size), fit.q)),
                    0.0,
                ]),
            )
        )
        self.add(marker)
        self.play(tracker.animate.set_value(1.0), run_time=6, rate_func=linear)
        marker.clear_updaters()
        arm.clear_updaters()
        self.wait(1)


class L1CommandDelayDemo(Scene):
    """Explain where L1's effective command delay enters the model boundary."""

    def construct(self):
        run = run_l1()
        trajectory = run.trajectories["validation"]
        left, right, bottom, top = -5.7, 5.7, -1.55, 1.65
        curves = {
            role: _plot_curve(
                trajectory[role].t,
                trajectory[role].q,
                left=left,
                right=right,
                bottom=bottom,
                top=top,
                color=ROLE_COLORS[role],
                width=4 if role == "oracle" else 2.5,
            )
            for role in ("oracle", "initial", "identified")
        }
        title = Text("L1 · command delay", font_size=40)
        subtitle = Text("The delay is introduced after the fixed PD law", font_size=22, color=GREY_B)
        title.to_edge(UP, buff=0.35)
        subtitle.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(subtitle))

        nodes = []
        for text, color in (("q_des", GREEN), ("fixed PD", WHITE), ("delay τ", YELLOW), ("pendulum", BLUE)):
            box = RoundedRectangle(width=1.65, height=0.72, corner_radius=0.08, color=color)
            label = Text(text, font_size=22, color=color).move_to(box)
            nodes.append(VGroup(box, label))
        VGroup(*nodes).arrange(RIGHT, buff=0.48).move_to([0.0, 2.25, 0.0])
        arrows = VGroup()
        for first, second in zip(nodes[:-1], nodes[1:]):
            arrows.add(Arrow(first.get_right(), second.get_left(), buff=0.1, color=GREY_B))
        delay_note = Text(
            f"Oracle τ = {run.config.truth.delay_s:.3f} s · Initial τ = {run.config.initial.delay_s:.3f} s",
            font_size=21,
            color=YELLOW,
        ).next_to(nodes[2], DOWN, buff=0.15)
        self.play(LaggedStart(*[FadeIn(node) for node in nodes], lag_ratio=0.15), ShowCreation(arrows), FadeIn(delay_note))

        self.play(Create(_plot_frame("validation position q(t)", left, right, bottom, top)))
        for role in ("oracle", "initial", "identified"):
            self.play(ShowCreation(curves[role]), run_time=0.8)
        self.play(FadeIn(_role_legend(("oracle", "initial", "identified"))))

        pivot = Dot(np.array([-8.0, -0.3, 0.0]), color=GREEN)
        arms = {}
        for role in ("oracle", "initial", "identified"):
            arms[role] = Line(pivot.get_center(), pivot.get_center() + DOWN * 1.55, color=ROLE_COLORS[role], stroke_width=6 if role == "oracle" else 3)
            self.add(arms[role])
        tracker = ValueTracker(0.0)
        for role, arm in arms.items():
            tr = trajectory[role]
            arm.add_updater(
                lambda line, tr=tr: line.put_start_and_end_on(
                    pivot.get_center(),
                    pivot.get_center() + 1.55 * np.array([
                        np.sin(np.interp(tracker.get_value(), np.linspace(0, 1, tr.q.size), tr.q)),
                        -np.cos(np.interp(tracker.get_value(), np.linspace(0, 1, tr.q.size), tr.q)),
                        0.0,
                    ]),
                )
            )
        marker = Dot(color=BLUE, radius=0.07)
        marker.add_updater(lambda dot: dot.move_to(_curve_point(curves["identified"], tracker.get_value())))
        self.add(marker)
        self.play(tracker.animate.set_value(1.0), run_time=6, rate_func=linear)
        for arm in arms.values():
            arm.clear_updaters()
        marker.clear_updaters()
        self.wait(1)
