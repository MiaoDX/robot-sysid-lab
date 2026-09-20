"""Offline ManimGL teaching clips for the Robot SysID Lab.

The scenes intentionally consume the same completed numerical runs as the
reports and Marimo lessons. Install the optional ``manimgl`` package before
rendering; the core repository does not depend on a graphics stack.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from manimlib import *


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from synthetic.l0_inertia_damping import Params, run_l0, score, simulate
from synthetic.l1_servo_loaded_pendulum import run_l1


# ManimGL's default frame is 14.22 x 8.0, so x stays inside about +/-7.1 and y
# inside +/-4.0. Geometry placed outside that box renders off-screen and
# silently disappears from the clip, so every pivot is chosen to keep its swept
# circle (|pivot| + arm length) inside those limits.
ROLE_COLORS = {"oracle": WHITE, "initial": ORANGE, "identified": BLUE}
ROLE_LABELS = {
    "oracle": "True system (Oracle)",
    "initial": "Initial model",
    "identified": "Identified model",
}
L0_ARM_LENGTH = 1.9
L1_ARM_LENGTH = 1.5


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
    scale: tuple[float, float] | None = None,
):
    """Create a simple polyline without depending on a charting extension.

    Pass the same ``scale=(lo, hi)`` to several curves to draw them on one
    shared vertical axis, which is what makes their amplitudes comparable. With
    ``scale=None`` each curve is stretched to fill the box on its own, which
    flatters a badly mismatched model by hiding how far it actually travels.
    """
    times = _subsample(np.asarray(times, dtype=float))
    values = _subsample(np.asarray(values, dtype=float))
    if scale is None:
        lo, hi = float(np.min(values)), float(np.max(values))
        pad = 0.08 * max(hi - lo, 1e-9)
        lo, hi = lo - pad, hi + pad
    else:
        lo, hi = float(scale[0]), float(scale[1])
    x = left + (times - times[0]) / max(times[-1] - times[0], 1e-9) * (right - left)
    y = bottom + (values - lo) / max(hi - lo, 1e-9) * (top - bottom)
    curve = VMobject(color=color, stroke_width=width)
    curve.set_points_as_corners([np.array([px, py, 0.0]) for px, py in zip(x, y)])
    curve._sysid_x = x
    curve._sysid_y = y
    return curve


def _driven_arm(pivot_point: np.ndarray, length: float, values: np.ndarray, tracker, color, width: float = 8.0):
    """A link that rotates to the angle recorded in ``values``."""
    arm = Line(pivot_point, pivot_point + RIGHT * length, color=color, stroke_width=width)
    grid = np.linspace(0.0, 1.0, len(values))

    def update(line):
        angle = float(np.interp(tracker.get_value(), grid, values))
        line.put_start_and_end_on(
            pivot_point,
            pivot_point + length * np.array([np.cos(angle), np.sin(angle), 0.0]),
        )

    arm.add_updater(update)
    return arm


def _joint_torque(pivot_point: np.ndarray, radius: float = 0.74, color=YELLOW):
    """A curved arrow wrapping the pivot.

    A straight arrow reads as a force pushing on a point, which leaves it open
    whether the torque acts at the joint axis or at the arm tip. Torque acts
    about the axis, so it is drawn curling around it.
    """

    # Counter-clockwise, matching the sign convention of `q`.
    start = pivot_point + radius * np.array([np.cos(0.59), np.sin(0.59), 0.0])
    end = pivot_point + radius * np.array([np.cos(2.55), np.sin(2.55), 0.0])
    return CurvedArrow(start, end, angle=2.0, color=color, stroke_width=5)


def _velocity_meter(pivot_point: np.ndarray, values: np.ndarray, tracker, color, max_value: float,
                    half: float = 1.7, drop: float = -2.45, thickness: float = 10):
    """A bipolar level meter for joint velocity.

    A swept-path trace is the wrong instrument here: both joints turn more than
    a full revolution, so their traces both close into a circle and hide the
    very difference they were meant to show. Velocity does not have that
    problem -- the well-damped joint falls to rest while the under-damped one
    keeps ringing, and the meter says so directly.
    """
    origin = pivot_point + np.array([0.0, drop, 0.0])
    grid = np.linspace(0.0, 1.0, len(values))
    rail = Line(origin - RIGHT * half, origin + RIGHT * half, color=GREY_D, stroke_width=2)
    bar = Line(origin, origin + RIGHT * 0.02, color=color, stroke_width=thickness)
    group = VGroup(rail, bar)
    for fraction, label in ((-1, f"-{max_value:.1f}"), (0, "0"), (1, f"+{max_value:.1f}")):
        position = origin + RIGHT * (fraction * half)
        group.add(Line(position + DOWN * 0.06, position + UP * 0.06, color=GREY_B))
        group.add(Text(label, font_size=18, color=GREY_B).move_to(position + DOWN * 0.25))

    def update(mob):
        frac = float(np.clip(np.interp(tracker.get_value(), grid, values) / max_value, -1.0, 1.0))
        end = origin + RIGHT * (frac * half)
        if np.linalg.norm(end - origin) < 2e-3:
            end = origin + RIGHT * 2e-3
        mob[1].put_start_and_end_on(origin, end)

    group.add_updater(update)
    return group


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


def _role_legend(roles):
    origin, spacing = np.array([-3.4, -3.45, 0.0]), 3.5
    legend = VGroup()
    for index, role in enumerate(roles):
        mark = Line(ORIGIN, RIGHT * 0.35, color=ROLE_COLORS[role], stroke_width=4)
        text = Text(ROLE_LABELS[role], font_size=20, color=ROLE_COLORS[role])
        row = VGroup(mark, text).arrange(RIGHT, buff=0.12)
        row.move_to(origin + RIGHT * index * spacing)
        legend.add(row)
    return legend


def _compact_iterates(iterates: list[dict], tolerance: float = 1e-9) -> list[tuple[float, float]]:
    """Drop consecutive iterates that are numerically identical.

    The optimizer reports a few duplicate steps while it satisfies its stopping
    conditions. They carry no motion, so they are not worth a beat on screen.
    """

    compact: list[tuple[float, float]] = []
    for entry in iterates:
        point = (float(entry["inertia"]), float(entry["damping"]))
        if compact and abs(point[0] - compact[-1][0]) < tolerance and abs(point[1] - compact[-1][1]) < tolerance:
            continue
        compact.append(point)
    return compact


def _l0_lesson_data() -> SimpleNamespace:
    """The L0 trajectories plus the one vertical scale they are drawn on.

    Shared by the L0 blocks so the two of them cannot drift apart on data or on
    the axis they compare amplitudes on.
    """

    run = run_l0()
    fit = run.data.fit
    t = fit.t
    truth_q = np.asarray(fit.q, dtype=float)  # the recorded True-system motion
    initial_q, _ = simulate(run.config.nominal, t, fit.u, q0=run.config.q0, qd0=run.config.qd0)
    identified_q, _ = simulate(run.fit.params, t, fit.u, q0=run.config.q0, qd0=run.config.qd0)
    low = float(min(truth_q.min(), initial_q.min(), identified_q.min()))
    high = float(max(truth_q.max(), initial_q.max(), identified_q.max()))
    pad = 0.06 * max(high - low, 1e-9)
    return SimpleNamespace(
        run=run,
        fit=fit,
        t=t,
        truth_q=truth_q,
        initial_q=initial_q,
        identified_q=identified_q,
        shared=(low - pad, high + pad),  # one axis for all three, as the report does
    )


class L0MismatchDemo(Scene):
    """Block question: what does the mismatch actually look like?

    The same recorded torque drives the true machine and the assumed one side by
    side, with persistent model labels and a shared velocity scale.
    """

    def construct(self):
        data = _l0_lesson_data()
        run, fit, t = data.run, data.fit, data.t
        truth_q, initial_q = data.truth_q, data.initial_q

        # The tip traces a circle of radius L0_ARM_LENGTH, so each pivot must
        # satisfy |x| + L <= 7.1 and |y| + L <= 4.0 to stay inside the frame.
        left_pivot = np.array([-3.3, -0.35, 0.0])
        right_pivot = np.array([3.3, -0.35, 0.0])
        length = L0_ARM_LENGTH

        title = Text("L0 · the mismatch, side by side", font_size=38)
        equation = Tex(R"J\ddot q + b\dot q = u", font_size=46)
        title.to_edge(UP, buff=0.3)
        equation.next_to(title, DOWN, buff=0.16)
        self.play(Write(title), Write(equation))

        # --- one machine, under torque --------------------------------------
        left_dot = Dot(left_pivot, color=GREEN)
        left_torque = _joint_torque(left_pivot)
        torque_label = Text("applied joint torque u", font_size=19, color=YELLOW)
        # Above the sweep circle (radius L0_ARM_LENGTH), so the arm never
        # crosses the label as it turns.
        torque_label.move_to([0.0, 2.35, 0.0])
        truth_label = Text("True system", font_size=24, color=ROLE_COLORS["oracle"]).move_to([-3.3, 1.9, 0])
        assumed_label = Text("Initial model", font_size=24, color=ROLE_COLORS["initial"]).move_to([3.3, 1.9, 0])
        self.play(FadeIn(left_dot), ShowCreation(left_torque), FadeIn(torque_label), FadeIn(truth_label))

        # --- the same torque, two machines ----------------------------------
        right_dot = Dot(right_pivot, color=GREEN)
        tracker = ValueTracker(0.0)
        truth_arm = _driven_arm(left_pivot, length, truth_q, tracker, ROLE_COLORS["oracle"], width=9)
        initial_arm = _driven_arm(right_pivot, length, initial_q, tracker, ROLE_COLORS["initial"], width=7)
        truth_qd = np.asarray(fit.qd, dtype=float)  # recorded True-system velocity
        _, initial_qd = simulate(run.config.nominal, t, fit.u, q0=run.config.q0, qd0=run.config.qd0)
        shared_qd = float(max(np.abs(truth_qd).max(), np.abs(initial_qd).max()))
        truth_meter = _velocity_meter(left_pivot, truth_qd, tracker, ROLE_COLORS["oracle"], shared_qd)
        initial_meter = _velocity_meter(right_pivot, initial_qd, tracker, ROLE_COLORS["initial"], shared_qd)
        same_push = Text("the same recorded torque u(t) drives both", font_size=20, color=GREY_B)
        same_push.move_to([0.0, -3.7, 0])
        meter_note = Text("joint velocity qd (rad/s) · shared scale", font_size=20, color=GREY_B).move_to([0.0, -3.35, 0])

        # The right joint gets its own torque marker: the caption claims the same
        # torque drives both, so both have to show one.
        right_torque = _joint_torque(right_pivot)
        self.play(
            FadeIn(right_dot), ShowCreation(right_torque),
            ShowCreation(truth_arm), ShowCreation(initial_arm),
            FadeIn(truth_meter), FadeIn(initial_meter), FadeIn(same_push), FadeIn(meter_note),
            FadeIn(assumed_label),
        )
        self.play(tracker.animate.set_value(1.0), run_time=9, rate_func=linear)
        for mob in (truth_arm, initial_arm, truth_meter, initial_meter):
            mob.clear_updaters()

        self.wait(2.0)


class L0FitLandsDemo(Scene):
    """Block question: did fitting actually fix it?

    The recorded fit motion drawn on one shared vertical axis, so the Initial
    model's excursion is not flattered away, and the Identified model visibly
    lands on the True system.
    """

    def construct(self):
        data = _l0_lesson_data()

        title = Text("L0 · does the fit land on the truth?", font_size=38)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        metrics = Text(
            f"Fit q RMSE (rad): Initial {data.run.nominal_fit_metrics.q_rmse:.3f}"
            f"  →  Identified {data.run.identified_fit_metrics.q_rmse:.2e}",
            font_size=23,
        ).move_to([0.0, 2.4, 0.0])
        self.play(FadeIn(metrics))

        left, right, bottom, top = -6.4, 6.4, -2.5, 1.5
        curves = {
            role: _plot_curve(
                data.t, values, left=left, right=right, bottom=bottom, top=top,
                color=ROLE_COLORS[role], width=4 if role == "oracle" else 2.6, scale=data.shared,
            )
            for role, values in (
                ("oracle", data.truth_q), ("initial", data.initial_q), ("identified", data.identified_q),
            )
        }
        self.play(ShowCreation(_plot_frame("fit position q(t)", left, right, bottom, top)))
        for role in ("oracle", "initial", "identified"):
            self.play(ShowCreation(curves[role]), run_time=0.7)
        self.play(FadeIn(_role_legend(("oracle", "initial", "identified"))))
        # Oracle and Identified are the same trace to machine precision, so the
        # blue line covers the white one. Say that out loud instead of letting
        # the viewer wonder where the third curve went.
        overlap = Text(
            "Identified lands on the True system: the fit recovered it",
            font_size=18, color=GREY_B,
        ).move_to([0.0, -2.95, 0])
        self.play(FadeIn(overlap))

        # Mark where the Initial model first departs. The block used to sweep an
        # unexplained dot along a curve; a marker with a stated meaning answers
        # the block's own question instead.
        def chart_x(seconds):
            return left + (float(seconds) - data.t[0]) / (data.t[-1] - data.t[0]) * (right - left)

        gap = np.abs(data.initial_q - data.truth_q)
        departure = int(np.argmax(gap > 0.05 * gap.max()))
        marker_line = Line(
            np.array([chart_x(data.t[departure]), bottom, 0.0]),
            np.array([chart_x(data.t[departure]), top, 0.0]),
            color=GREY_B, stroke_width=2,
        )
        marker_note = Text(
            "from here the Initial model runs away", font_size=17, color=GREY_B,
        ).move_to([chart_x(data.t[departure]) + 2.6, top - 0.3, 0.0])
        self.play(ShowCreation(marker_line), FadeIn(marker_note))
        self.wait(3.0)


def _l1_delay_data() -> SimpleNamespace:
    """The L1 run plus the geometry both delay blocks draw on.

    Shared so the boundary block and the phase block cannot disagree about the
    panel boxes, the shared amplitude scale, or the time axis.
    """

    run = run_l1()
    config = run.config
    control = run.trajectories["fit"]["oracle"]
    validation = run.trajectories["validation"]
    low = float(min(validation[role].q.min() for role in ("oracle", "initial", "identified")))
    high = float(max(validation[role].q.max() for role in ("oracle", "initial", "identified")))
    margin = 0.08 * (high - low)
    return SimpleNamespace(
        run=run,
        config=config,
        control=control,
        validation=validation,
        truth_delay=float(config.truth.delay_s),
        initial_delay=float(config.initial.delay_s),
        identified_delay=float(run.fit.params.delay_s),
        duration=float(control.t[-1] - control.t[0]),
        amplitude=max(float(np.abs(control.command_torque).max()), 1e-9),
        q_scale=(low - margin, high + margin),
    )


def _delay_panels(data, window: tuple[float, float] | None = None) -> SimpleNamespace:
    """The stacked c / τ panels: the PD torque command and what leaves the buffer.

    ``window`` selects which slice of recorded time fills the panel width. Over
    the full 8 s chirp the 0.080 s readback is about 1% of the axis and the
    connector degenerates into a vertical line, so a block that wants to *show*
    the readback must zoom in.
    """

    left, right = -6.4, 6.4
    c_low, c_high = 0.35, 1.72
    x_low, x_high = -1.5, -0.13
    shared = (-1.15 * data.amplitude, 1.15 * data.amplitude)
    start, end = window if window else (float(data.control.t[0]), float(data.control.t[-1]))
    shown = (data.control.t >= start) & (data.control.t <= end)

    def to_x(seconds):
        return left + (float(seconds) - start) / max(end - start, 1e-9) * (right - left)

    return SimpleNamespace(
        left=left, right=right, c_low=c_low, c_high=c_high, x_low=x_low, x_high=x_high,
        shared=shared, start=start, end=end,
        to_x=to_x,
        command=_plot_curve(
            data.control.t[shown], data.control.command_torque[shown], left=left, right=right,
            bottom=c_low, top=c_high, color=YELLOW, width=2.4, scale=shared,
        ),
        torque=_plot_curve(
            data.control.t[shown], data.control.torque[shown], left=left, right=right,
            bottom=x_low, top=x_high, color=ORANGE, width=2.4, scale=shared,
        ),
        notes=VGroup(
            Text("torque command c from the PD law", font_size=17, color=YELLOW).move_to([left + 2.1, c_high + 0.24, 0.0]),
            Text(
                f"actuator input τ, read back {data.truth_delay:.3f} s later",
                font_size=17, color=ORANGE,
            ).move_to([left + 3.0, x_high + 0.24, 0.0]),
        ),
    )


def _readback_heads(panels, data, playhead):
    """Two playheads plus the connector that spans exactly the delay."""

    bottom_head = Line(np.array([panels.left, panels.x_low, 0.0]), np.array([panels.left, panels.x_high, 0.0]), color=WHITE, stroke_width=2)
    top_head = Line(np.array([panels.left, panels.c_low, 0.0]), np.array([panels.left, panels.c_high, 0.0]), color=WHITE, stroke_width=2)
    connector = Line(np.array([panels.left, panels.x_high, 0.0]), np.array([panels.left, panels.c_low, 0.0]), color=WHITE, stroke_width=2)
    heads = VGroup(bottom_head, top_head, connector)

    def track(group):
        now = float(playhead.get_value())
        back = max(now - data.truth_delay, float(data.control.t[0]))
        x_bottom, x_top = panels.to_x(now), panels.to_x(back)
        group[0].put_start_and_end_on(np.array([x_bottom, panels.x_low, 0.0]), np.array([x_bottom, panels.x_high, 0.0]))
        group[1].put_start_and_end_on(np.array([x_top, panels.c_low, 0.0]), np.array([x_top, panels.c_high, 0.0]))
        group[2].put_start_and_end_on(
            np.array([x_bottom, panels.x_high + 0.04, 0.0]), np.array([x_top, panels.c_low - 0.04, 0.0])
        )

    heads.add_updater(track)
    return heads


class L1BoundaryDemo(Scene):
    """Block question: where does the delay actually hide?

    The lesson's own checkpoint says the static schematic cannot show the
    command buffer, so this block opens it: the torque command goes in, and the
    connector shows the same sample leaving one delay later.
    """

    def construct(self):
        data = _l1_delay_data()
        # A narrow, late slice of time. Across the whole 8 s chirp the 0.080 s
        # readback is about 1% of the axis and collapses to a vertical line; this
        # window is late enough that the chirp is fast, so the offset shows in
        # the waveforms as well as in the connector.
        panels = _delay_panels(data, window=(6.0, 7.6))

        title = Text("L1 · where the delay hides", font_size=38)
        subtitle = Text("the buffer holds the torque command c, not the position target", font_size=20, color=GREY_B)
        title.to_edge(UP, buff=0.28)
        subtitle.next_to(title, DOWN, buff=0.14)
        self.play(Write(title), FadeIn(subtitle))

        # The machine appears once, to say which machine this is — and then it
        # leaves. That exit is the argument, not a transition: the lesson's own
        # checkpoint is that a static schematic is a snapshot and cannot show the
        # command buffer, so the clip does not send the eye hunting in the arm.
        base = Rectangle(width=1.7, height=0.26, color=GREY_B).move_to([-3.1, 0.95, 0.0])
        joint = Dot(np.array([-3.1, 0.8, 0.0]), color=GREEN)
        link = Line(np.array([-3.1, 0.8, 0.0]), np.array([-3.1, -0.8, 0.0]), color=BLUE, stroke_width=7)
        payload = Dot(np.array([-3.1, -0.8, 0.0]), color=ORANGE, radius=0.13)
        gravity = Arrow(np.array([-3.1, -1.05, 0.0]), np.array([-3.1, -1.7, 0.0]), color=GREY_B, buff=0)
        machine = VGroup(
            base, joint, link, payload, gravity,
            Text("fixed base", font_size=16, color=GREY_B).move_to([-3.1, 1.35, 0.0]),
            Text("payload", font_size=16, color=ORANGE).move_to([-1.75, -0.8, 0.0]),
            Text("q", font_size=17, color=GREY_B).move_to([-3.35, -0.35, 0.0]),
        )
        question = Text(
            "where is the delay in this picture?",
            font_size=23, color=GREY_B,
        ).move_to([2.2, -0.2, 0.0])
        self.play(FadeIn(machine))
        self.play(FadeIn(question))
        self.wait(1.6)
        self.play(FadeOut(VGroup(machine, question)))

        nodes = []
        for label, color in (("q_des", GREEN), ("fixed PD", WHITE), (f"delay {data.truth_delay:.3f} s", YELLOW), ("pendulum", BLUE)):
            box = RoundedRectangle(width=1.9, height=0.72, corner_radius=0.08, color=color)
            nodes.append(VGroup(box, Text(label, font_size=19, color=color).move_to(box)))
        VGroup(*nodes).arrange(RIGHT, buff=0.4).move_to([0.0, 2.5, 0.0])
        arrows = VGroup(*[
            Arrow(first.get_right(), second.get_left(), buff=0.08, color=GREY_B)
            for first, second in zip(nodes[:-1], nodes[1:])
        ])
        boundary_marks = VGroup(
            Text("c", font_size=19, color=YELLOW).next_to(arrows[1], UP, buff=0.06),
            Text("τ", font_size=19, color=YELLOW).next_to(arrows[2], UP, buff=0.06),
        )
        self.play(LaggedStart(*[FadeIn(node) for node in nodes], lag_ratio=0.12), ShowCreation(arrows))
        self.play(FadeIn(boundary_marks))
        self.wait(0.4)

        self.play(
            # ManimGL's FadeOut takes ONE mobject: a second argument binds to
            # `shift`, not to another mobject, so everything goes in one VGroup.
            FadeOut(VGroup(*nodes, arrows, boundary_marks)),
            ShowCreation(panels.command), ShowCreation(panels.torque), FadeIn(panels.notes),
        )

        playhead = ValueTracker(panels.start + data.truth_delay)
        heads = _readback_heads(panels, data, playhead)
        self.add(heads)
        self.play(playhead.animate.set_value(panels.end), run_time=5, rate_func=linear)
        heads.clear_updaters()

        caption = Text(
            f"the same torque command leaves the buffer {data.truth_delay:.3f} s later",
            font_size=19, color=GREY_B,
        ).move_to([0.0, -2.55, 0.0])
        self.play(FadeIn(caption))
        self.wait(1.4)


class L1PhaseDemo(Scene):
    """Block question: why does a chirp make the delay visible?

    A delay of 0.080 s is fixed in *time*, but what shows up in the response is
    a share of a *cycle*, and cycles get shorter as the chirp rises. So the two
    are put side by side: the signals above, and the phase lag they imply below,
    growing from 2 degrees to 29 while the delay itself never changes.
    """

    def construct(self):
        data = _l1_delay_data()
        control, t = data.control, data.control.t
        left, right = -6.4, 6.4
        sig_low, sig_high = 0.5, 1.95
        lag_low, lag_high = -1.8, -0.15
        shared = (-1.15 * data.amplitude, 1.15 * data.amplitude)
        span = max(float(t[-1] - t[0]), 1e-9)

        def to_x(seconds):
            return left + (float(seconds) - float(t[0])) / span * (right - left)

        title = Text("L1 · why a chirp reveals it", font_size=38)
        title.to_edge(UP, buff=0.28)
        self.play(Write(title))

        command = _plot_curve(
            t, control.command_torque, left=left, right=right,
            bottom=sig_low, top=sig_high, color=YELLOW, width=2.2, scale=shared,
        )
        torque = _plot_curve(
            t, control.torque, left=left, right=right,
            bottom=sig_low, top=sig_high, color=ORANGE, width=2.2, scale=shared,
        )
        signal_note = Text(
            "the same torque command c, and the input τ that leaves the buffer",
            font_size=16, color=GREY_B,
        ).move_to([0.0, sig_high + 0.24, 0.0])
        self.play(ShowCreation(command), ShowCreation(torque), FadeIn(signal_note))

        f_low, f_high = float(data.config.fit_f0), float(data.config.fit_f1)
        lag = np.degrees(
            2 * np.pi * (f_low + (f_high - f_low) * (t - t[0]) / span) * data.truth_delay
        )
        top_lag = float(np.ceil(lag.max() / 5.0) * 5.0)
        lag_curve = _plot_curve(
            t, lag, left=left, right=right, bottom=lag_low, top=lag_high,
            color=BLUE, width=3.2, scale=(0.0, top_lag),
        )
        self.play(
            ShowCreation(_plot_frame("that delay expressed as a share of a cycle", left, right, lag_low, lag_high)),
            ShowCreation(lag_curve),
        )
        tick = lambda value: Text(f"{value:.0f}°", font_size=15, color=GREY_B).move_to(
            [left - 0.34, lag_low + (value / top_lag) * (lag_high - lag_low), 0.0]
        )
        self.play(FadeIn(tick(0.0)), FadeIn(tick(top_lag)))

        # Both panels sweep together, so the growth is tied to the signals above.
        markers = VGroup(
            Line(np.array([left, sig_low, 0.0]), np.array([left, sig_high, 0.0]), color=WHITE, stroke_width=2),
            Line(np.array([left, lag_low, 0.0]), np.array([left, lag_high, 0.0]), color=WHITE, stroke_width=2),
        )
        playhead = ValueTracker(float(t[0]))
        frequency = DecimalNumber(f_low, num_decimal_places=2, font_size=25)
        phase = DecimalNumber(float(lag[0]), num_decimal_places=1, font_size=25, color=BLUE)
        readout = VGroup(
            Text(f"delay = {data.truth_delay:.3f} s", font_size=23),
            Text("f =", font_size=23), frequency, Text("Hz", font_size=23),
            Text("phase ≈", font_size=23), phase, Text("deg", font_size=23),
        ).arrange(RIGHT, buff=0.18).move_to([0.0, -2.45, 0.0])
        explanation = Text("360 × chirp frequency × delay; a local phase estimate", font_size=20, color=GREY_B)
        explanation.move_to([0.0, -2.95, 0.0])
        self.play(FadeIn(readout), FadeIn(explanation))

        def track(group):
            now = float(playhead.get_value())
            x = to_x(now)
            current_frequency = f_low + (f_high - f_low) * (now - t[0]) / span
            frequency.set_value(current_frequency)
            phase.set_value(360.0 * current_frequency * data.truth_delay)
            group[0].put_start_and_end_on(np.array([x, sig_low, 0.0]), np.array([x, sig_high, 0.0]))
            group[1].put_start_and_end_on(np.array([x, lag_low, 0.0]), np.array([x, lag_high, 0.0]))

        markers.add_updater(track)
        self.add(markers)
        self.play(playhead.animate.set_value(float(t[-1])), run_time=7, rate_func=linear)
        markers.clear_updaters()

        caption = Text(
            f"the delay stays {data.truth_delay:.3f} s the whole time — it is the cycle that shortens",
            font_size=19, color=GREY_B,
        ).move_to([0.0, -3.5, 0.0])
        self.play(FadeIn(caption))
        self.wait(3.0)
class L1HeldOutDemo(Scene):
    """Block question: did fitting the delay predict motion it never saw?

    Held-out validation only, with the axes and the role key stated on screen so
    the block explains its own chart. There is deliberately no machine view
    here: the lesson's point is that the answer lives in the response, not in
    the arm geometry, so an arm would send the eye the wrong way.
    """

    def construct(self):
        data = _l1_delay_data()
        validation = data.validation
        left, right, bottom, top = -5.8, 6.5, -2.0, 1.7

        title = Text("L1 · did the fit predict the held-out motion?", font_size=36)
        title.to_edge(UP, buff=0.28)
        self.play(Write(title))

        verdict = Text(
            f"Delay (s): Initial {data.initial_delay:.3f}   ·   Identified {data.identified_delay:.3f}   ·   True {data.truth_delay:.3f}",
            font_size=19, color=GREY_B,
        ).move_to([0.0, 2.65, 0.0])
        self.play(FadeIn(verdict))
        metrics = Text(
            f"Held-out q RMSE (rad): {data.run.initial_validation.q_rmse:.4f}"
            f"  →  {data.run.identified_validation.q_rmse:.2e}",
            font_size=22,
        ).move_to([0.0, 2.2, 0.0])
        self.play(FadeIn(metrics))

        curves = {
            role: _plot_curve(
                validation[role].t, validation[role].q,
                left=left, right=right, bottom=bottom, top=top,
                color=ROLE_COLORS[role], width=3.6 if role == "oracle" else 2.4, scale=data.q_scale,
            )
            for role in ("oracle", "initial", "identified")
        }
        self.play(ShowCreation(_plot_frame("held-out validation: position q(t)", left, right, bottom, top)))
        for role in ("oracle", "initial", "identified"):
            self.play(ShowCreation(curves[role]), run_time=0.7)
        self.play(FadeIn(_role_legend(("oracle", "initial", "identified"))))

        # Axes: without them the viewer cannot tell how big the motion is or
        # over what window, which was the main complaint about this block.
        lo, hi = data.q_scale
        ticks = VGroup()
        for value in (-0.2, 0.0, 0.2):
            y = bottom + (value - lo) / (hi - lo) * (top - bottom)
            ticks.add(Line(np.array([left, y, 0.0]), np.array([left + 0.2, y, 0.0]), color=GREY_D, stroke_width=2))
            ticks.add(Text(f"{value:.1f}", font_size=15, color=GREY_B).move_to([left - 0.34, y, 0.0]))
        times = validation["oracle"].t
        for seconds in (0.0, 2.0, 4.0, 6.0, 8.0):
            x = left + (seconds - times[0]) / (times[-1] - times[0]) * (right - left)
            ticks.add(Line(np.array([x, bottom, 0.0]), np.array([x, bottom - 0.14, 0.0]), color=GREY_D, stroke_width=2))
            ticks.add(Text(f"{seconds:.0f}", font_size=15, color=GREY_B).move_to([x, bottom - 0.38, 0.0]))
        ticks.add(Text("q (rad)", font_size=16, color=GREY_B).move_to([left - 0.34, top - 0.3, 0.0]))
        ticks.add(Text("time (s)", font_size=16, color=GREY_B).move_to([(left + right) / 2, bottom - 0.72, 0.0]))
        self.play(FadeIn(ticks))

        # Oracle and Identified are the same trace to machine precision, so the
        # blue line covers the white one. Say it rather than leave it a puzzle.
        overlapping = Text(
            "Identified lands on the True system — the white line is underneath the blue one",
            font_size=17, color=GREY_B,
        ).move_to([0.6, -3.05, 0.0])
        self.play(FadeIn(overlapping))
        self.wait(3.0)

def _l0_journey_data() -> SimpleNamespace:
    """The fitting-journey artifact plus the mappings both journey blocks need.

    Shared so the walk block and the robustness block cannot disagree about the
    plane mapping, the shared curve axis, or which iterates to draw.
    """

    artifact = REPO_ROOT / "reports" / "l0_inertia_damping" / "fitting_paths.json"
    shading = REPO_ROOT / "reports" / "l0_inertia_damping" / "fitting_landscape.png"
    journey = json.loads(artifact.read_text(encoding="utf-8"))
    run = run_l0()
    observed = run.data.fit
    t = observed.t

    plane = (-6.8, -1.0, -2.6, 1.4)
    chart = (0.5, 6.8, -2.6, 1.4)

    def axis_map(axis, low, high):
        first, last = float(axis[0]), float(axis[-1])
        span = max(last - first, 1e-12)
        return lambda value: low + (float(value) - first) / span * (high - low)

    initial_q, _ = simulate(
        run.config.nominal, t, observed.u, q0=run.config.q0, qd0=run.config.qd0
    )
    low = float(min(observed.q.min(), initial_q.min()))
    high = float(max(observed.q.max(), initial_q.max()))
    margin = 0.06 * (high - low)

    return SimpleNamespace(
        journey=journey,
        shading=shading,
        run=run,
        observed=observed,
        t=t,
        plane=plane,
        chart=chart,
        to_x=axis_map(journey["grid"]["inertia"], plane[0], plane[1]),
        to_y=axis_map(journey["grid"]["damping"], plane[2], plane[3]),
        truth=journey["truth"],
        shared_q=(low - margin, high + margin),
        walk=_compact_iterates(journey["paths"][0]["iterates"]),
        all_paths=[_compact_iterates(path["iterates"]) for path in journey["paths"]],
    )


def _journey_backdrop(data, plane_frame_width: float = 0.0):
    """The shaded (J, b) plane, stretched to the panel it belongs to."""

    plane = data.plane
    backdrop = ImageMobject(str(data.shading))
    # Stretch, not scale: the shading is square but the panel is not, and
    # set_width/set_height would each preserve the image's own aspect.
    backdrop.stretch_to_fit_width(plane[1] - plane[0])
    backdrop.stretch_to_fit_height(plane[3] - plane[2])
    backdrop.move_to(np.array([(plane[0] + plane[1]) / 2, (plane[2] + plane[3]) / 2, 0.0]))
    return backdrop


def _journey_legend(data):
    """Use the landscape's own viridis palette to explain its log-cost scale."""
    from matplotlib import colormaps
    from matplotlib.colors import to_hex

    ramp = VGroup(*[
        Rectangle(width=0.16, height=0.18, stroke_width=0,
                  fill_color=to_hex(colormaps["viridis"](value)), fill_opacity=1)
        for value in np.linspace(0, 1, 16)
    ]).arrange(RIGHT, buff=0)
    legend = VGroup(
        Text("low", font_size=20), ramp, Text("high cost", font_size=20),
    ).arrange(RIGHT, buff=0.14)
    legend.move_to([(data.plane[0] + data.plane[1]) / 2, -3.35, 0])
    note = Text("log scale · arrows follow accepted steps", font_size=17, color=GREY_B)
    note.next_to(legend, DOWN, buff=0.12)
    return VGroup(legend, note)


def _journey_directions(path, on_plane):
    """Mark visible steps; tiny converged steps need no overlapping arrowheads."""
    arrows = VGroup()
    for first, second in zip(path[:-1], path[1:]):
        start, end = on_plane(first), on_plane(second)
        if np.linalg.norm(end - start) > 0.25:
            arrows.add(Arrow(start, end, buff=0.05, color=WHITE, stroke_width=2))
    return arrows


class L0FitWalkDemo(Scene):
    """Block question: how does the fit get from the Initial model to the truth?

    Left: the cost the fitter minimises over (J, b), with the route it took.
    Right: the model's own q(t) at each recorded iterate on one shared axis, so
    the runaway is watched collapsing onto the True system.
    """

    def construct(self):
        data = _l0_journey_data()
        chart, truth, walk = data.chart, data.truth, data.walk
        observed, t = data.observed, data.t

        def on_plane(point):
            return np.array([data.to_x(point[0]), data.to_y(point[1]), 0.0])

        def model_curve(point, color, width=4.0):
            values, _ = simulate(
                Params(inertia=point[0], damping=point[1]),
                t, observed.u, q0=data.run.config.q0, qd0=data.run.config.qd0,
            )
            return _plot_curve(
                t, values, left=chart[0], right=chart[1], bottom=chart[2], top=chart[3],
                color=color, width=width, scale=data.shared_q,
            )

        title = Text("L0 · how the fit gets there", font_size=38)
        title.to_edge(UP, buff=0.28)
        self.play(Write(title))

        backdrop = _journey_backdrop(data)
        plane_frame = Rectangle(
            width=data.plane[1] - data.plane[0], height=data.plane[3] - data.plane[2],
            stroke_color=GREY_B, stroke_width=1.5,
        ).move_to(backdrop.get_center())
        chart_frame = _plot_frame("model position q(t)", *chart)
        plane_caption = Text("how wrong the model is, over (J, b)", font_size=19, color=GREY_B)
        plane_caption.next_to(plane_frame, UP, buff=0.12)
        axis_j = Text("inertia J →", font_size=17, color=GREY_B).next_to(plane_frame, DOWN, buff=0.1)
        axis_b = Text("damping b →", font_size=17, color=GREY_B)
        axis_b.rotate(PI / 2).next_to(plane_frame, LEFT, buff=0.1)
        self.play(
            FadeIn(backdrop), ShowCreation(plane_frame), ShowCreation(chart_frame),
            FadeIn(plane_caption), FadeIn(axis_j), FadeIn(axis_b),
            FadeIn(_journey_legend(data)),
        )

        truth_ring = Dot(on_plane((truth["inertia"], truth["damping"])), radius=0.15, color=BLACK)
        truth_dot = Dot(on_plane((truth["inertia"], truth["damping"])), radius=0.1, color=ROLE_COLORS["oracle"])
        truth_label = Text("True system", font_size=18, color=ROLE_COLORS["oracle"])
        truth_label.next_to(truth_dot, UP, buff=0.12)
        start_ring = Dot(on_plane(walk[0]), radius=0.15, color=BLACK)
        start_dot = Dot(on_plane(walk[0]), radius=0.1, color=ROLE_COLORS["initial"])
        start_label = Text("Initial model", font_size=18, color=ROLE_COLORS["initial"])
        start_label.next_to(start_dot, RIGHT, buff=0.15)
        reference = _plot_curve(
            t, observed.q, left=chart[0], right=chart[1], bottom=chart[2], top=chart[3],
            color=GREY_B, width=2.4, scale=data.shared_q,
        )
        self.play(
            FadeIn(truth_ring), FadeIn(truth_dot), FadeIn(truth_label),
            FadeIn(start_ring), FadeIn(start_dot), FadeIn(start_label), ShowCreation(reference),
        )

        def readout(step, point):
            metrics = score(Params(inertia=point[0], damping=point[1]), observed)
            return VGroup(
                Text(f"step {step} / {len(walk) - 1}", font_size=19, color=GREY_B),
                Text(f"J = {point[0]:.4f}   b = {point[1]:.4f}", font_size=19, color=WHITE),
                Text(f"q RMSE = {metrics.q_rmse:,.3f} rad", font_size=19, color=GREY_B),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)

        readout_box = readout(0, walk[0]).move_to([(chart[0] + chart[1]) / 2, -3.35, 0])
        current = model_curve(walk[0], ROLE_COLORS["initial"], width=4.0)
        key_row = lambda text, color: Text(text, font_size=17, color=color).move_to([chart[0] + 1.05, chart[3] - 0.3, 0.0])
        current_label = key_row("current model", ROLE_COLORS["initial"])
        reference_label = key_row("True system (recorded)", GREY_B).shift(DOWN * 0.32)
        walker_ring = Dot(on_plane(walk[0]), radius=0.15, color=BLACK)
        walker = Dot(on_plane(walk[0]), radius=0.1, color=ROLE_COLORS["initial"])
        self.play(
            ShowCreation(current), FadeIn(current_label),
            FadeIn(reference_label), FadeIn(readout_box),
        )
        self.play(FadeIn(walker_ring), FadeIn(walker), run_time=0.6)

        trail = [on_plane(walk[0])]
        for step in range(1, len(walk)):
            fraction = step / max(len(walk) - 1, 1)
            tint = interpolate_color(ROLE_COLORS["initial"], ROLE_COLORS["identified"], fraction)
            trail.append(on_plane(walk[step]))
            segment = VGroup(
                Line(trail[-2], trail[-1], color=WHITE, stroke_width=3),
                _journey_directions(walk[step - 1:step + 1], on_plane),
            )
            next_readout = readout(step, walk[step]).move_to([(chart[0] + chart[1]) / 2, -3.35, 0])
            self.play(
                ShowCreation(segment),
                Transform(current, model_curve(walk[step], tint, width=4.0)),
                Transform(current_label, key_row("current model", tint)),
                Transform(readout_box, next_readout),
                walker.animate.move_to(on_plane(walk[step])),
                walker_ring.animate.move_to(on_plane(walk[step])),
                run_time=1.5,
            )
            self.wait(0.35)

        self.play(Transform(current_label, key_row("Identified model", ROLE_COLORS["identified"])))
        self.wait(3.0)


class L0FitRobustDemo(Scene):
    """Block question: was that one lucky starting guess?

    Every recorded start is drawn on the same cost plane. They all arrive at the
    same parameters, which is a statement about the problem, not about luck.
    """

    def construct(self):
        data = _l0_journey_data()
        truth = data.truth

        def on_plane(point):
            return np.array([data.to_x(point[0]), data.to_y(point[1]), 0.0])

        title = Text("L0 · was that one lucky start?", font_size=38)
        title.to_edge(UP, buff=0.28)
        self.play(Write(title))

        backdrop = _journey_backdrop(data)
        plane_frame = Rectangle(
            width=data.plane[1] - data.plane[0], height=data.plane[3] - data.plane[2],
            stroke_color=GREY_B, stroke_width=1.5,
        ).move_to(backdrop.get_center())
        axis_j = Text("inertia J →", font_size=17, color=GREY_B).next_to(plane_frame, DOWN, buff=0.1)
        axis_b = Text("damping b →", font_size=17, color=GREY_B)
        axis_b.rotate(PI / 2).next_to(plane_frame, LEFT, buff=0.1)
        start_dot = Dot(on_plane(data.walk[0]), radius=0.1, color=ROLE_COLORS["initial"])
        start_label = Text("Initial model", font_size=18, color=ROLE_COLORS["initial"])
        start_label.next_to(start_dot, RIGHT, buff=0.15)
        self.play(FadeIn(backdrop), ShowCreation(plane_frame), FadeIn(axis_j), FadeIn(axis_b),
                  FadeIn(start_dot), FadeIn(start_label), FadeIn(_journey_legend(data)))

        truth_ring = Dot(on_plane((truth["inertia"], truth["damping"])), radius=0.15, color=BLACK)
        truth_dot = Dot(on_plane((truth["inertia"], truth["damping"])), radius=0.1, color=ROLE_COLORS["oracle"])
        truth_label = Text("True system", font_size=18, color=ROLE_COLORS["oracle"])
        truth_label.next_to(truth_dot, UP, buff=0.12)
        self.play(FadeIn(truth_ring), FadeIn(truth_dot), FadeIn(truth_label))

        # Tie the plane to the curves: as each route is drawn, the behaviour its
        # starting parameters produce appears alongside it. Agreeing on (J, b)
        # only means something once you can see it is agreeing on motion.
        chart = data.chart
        clip = (-2.0, 20.0)
        self.play(ShowCreation(_plot_frame("model q(t) from each start", *chart)))

        def start_curve(point):
            values, _ = simulate(
                Params(inertia=point[0], damping=point[1]),
                data.t, data.observed.u, q0=data.run.config.q0, qd0=data.run.config.qd0,
            )
            return _plot_curve(
                data.t, np.clip(values, clip[0], clip[1]),
                left=chart[0], right=chart[1], bottom=chart[2], top=chart[3],
                color=ROLE_COLORS["initial"], width=1.8, scale=clip,
            )

        for path in data.all_paths:
            dots = VGroup(*[Dot(on_plane(point), radius=0.055, color=GREY_B) for point in path])
            route = VMobject(color=WHITE, stroke_width=2)
            route.set_points_as_corners([on_plane(point) for point in path])
            self.play(FadeIn(dots), ShowCreation(route), FadeIn(_journey_directions(path, on_plane)),
                      ShowCreation(start_curve(path[0])), run_time=0.6)

        truth_curve = _plot_curve(
            data.t, data.observed.q, left=chart[0], right=chart[1],
            bottom=chart[2], top=chart[3], color=ROLE_COLORS["oracle"], width=3.4, scale=clip,
        )
        landed = Text(
            "every start ends on this one curve",
            font_size=17, color=ROLE_COLORS["oracle"],
        ).move_to([(chart[0] + chart[1]) / 2, chart[2] - 0.32, 0.0])
        clipped = Text(
            "two starts run past the top of this scale",
            font_size=15, color=GREY_B,
        ).move_to([(chart[0] + chart[1]) / 2, chart[2] - 0.68, 0.0])
        self.play(ShowCreation(truth_curve), FadeIn(landed), FadeIn(clipped))

        verdict = Text(
            f"all {len(data.all_paths)} tested starts reach the same J and b",
            font_size=21, color=ROLE_COLORS["identified"],
        ).next_to(plane_frame, UP, buff=0.12)
        self.play(Write(verdict))
        self.wait(3.0)
