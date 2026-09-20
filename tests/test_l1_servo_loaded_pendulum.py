"""Focused numerical and leakage contract tests for L1."""

import inspect
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from synthetic.l1_servo_loaded_pendulum import (
    Observations,
    Params,
    PublicModel,
    build_benchmark,
    derive_velocity,
    fit_student,
    load_config,
    machine_frame,
    machine_svg,
    plot_run,
    run_l1,
    run_summary,
    simulate_trajectory,
    write_report,
)
import synthetic.l1_servo_loaded_pendulum as l1


def test_delay_recovery_and_validation_thresholds():
    r = run_l1()
    assert r.fit.success
    assert abs(r.fit.params.delay_s - r.config.truth.delay_s) <= 1e-3
    assert (1 - r.identified_validation.q_rmse / r.initial_validation.q_rmse) >= 0.9
    assert (1 - r.identified_validation.qd_rmse / r.initial_validation.qd_rmse) >= 0.9


def test_public_fitter_has_no_oracle_or_validation_arguments():
    sig = inspect.signature(fit_student)
    assert list(sig.parameters) == [
        "observations",
        "model",
        "optimizer_start",
        "lower",
        "upper",
    ]
    assert "config" not in sig.parameters and "validation" not in sig.parameters
    r = run_l1()
    poison = Observations(
        r.data.fit.t, r.data.fit.q_des, r.data.fit.q + 10, r.data.fit.qd + 10
    )
    fit = fit_student(poison, r.config.model, optimizer_start=Params(0.03))
    assert fit.params.delay_s != pytest.approx(r.fit.params.delay_s, abs=1e-3)


def test_full_pd_delay_differs_from_input_only_delay():
    r = run_l1()
    m = r.config.model
    qdes = r.data.fit.q_des
    delayed = simulate_trajectory(m, qdes, delay_s=0.08)
    shifted = np.r_[np.zeros(16), qdes[:-16]]
    input_only = simulate_trajectory(m, shifted, delay_s=0)
    assert np.max(abs(delayed.q - input_only.q)) > 1e-3


def test_l1_learner_path_does_not_carry_operator_material():
    """The lesson README is the learner path; verification material lives elsewhere."""

    lesson = Path("docs/lessons/l1/README.md").read_text(encoding="utf-8")
    verification = Path("reports/l1_servo_loaded_pendulum/verification.md").read_text(encoding="utf-8")

    assert "verification.md" in lesson
    assert "Learner acceptance walkthrough" not in lesson
    assert "PYTHONPATH" not in lesson
    assert "Learner acceptance walkthrough" in verification


def test_delayed_torque_is_a_pure_shift_of_the_command():
    """The delay clip draws the buffer as an exact readback, so guard that.

    `L1BoundaryDemo` overlays `command_torque` with `torque` and marks the
    horizontal offset with a 0.080 s arrow. That reading is only honest while
    the actuator input really is the command delayed by whole samples, and while
    the zero-delay Initial model really does show no offset at all.
    """

    r = run_l1()
    truth_delay = r.config.truth.delay_s
    dt = float(r.data.fit.t[1] - r.data.fit.t[0])
    steps = int(round(truth_delay / dt))
    assert steps * dt == pytest.approx(truth_delay)

    for split in ("fit", "validation"):
        oracle = r.trajectories[split]["oracle"]
        shifted = np.r_[np.zeros(steps), oracle.command_torque[:-steps]]
        assert np.max(np.abs(oracle.torque - shifted)) < 1e-12

        initial = r.trajectories[split]["initial"]
        assert np.max(np.abs(initial.torque - initial.command_torque)) < 1e-12


def test_fractional_delay_zero_prehistory_and_no_future_read():
    h = np.array([1.0, 3.0, 7.0])
    assert l1._delayed(h, 0, 0.5, 1.0) == pytest.approx(0.5)
    assert l1._delayed(h, 1, 0.5, 1.0) == pytest.approx(2.0)
    assert l1._delayed(h, 2, 0.0, 1.0) == pytest.approx(7.0)


def test_derive_velocity_definition_and_known_reset():
    q = np.array([0.0, 1.0, 3.0, 6.0])
    assert np.allclose(derive_velocity(q, 1.0), [1.0, 1.5, 2.5, 3.0])
    r = run_l1()
    tr = r.trajectories["fit"]["initial"]
    assert tr.qd_raw[0] == pytest.approx(r.config.model.qd0)


def test_gravity_dynamics_matches_independent_solve_ivp():
    m = PublicModel(0.002, 0.2, 0.3, -0.2, 1.2, 0.35, 0.6, 9.81, 0.0, 0.0, 2)
    qdes = np.zeros(101)
    tr = simulate_trajectory(m, qdes, delay_s=0.0)
    sol = solve_ivp(
        lambda t, x: (x[1], -m.gravity_moment * np.sin(x[0]) / m.inertia),
        [0, 0.2],
        [m.q0, m.qd0],
        t_eval=tr.t,
        rtol=1e-10,
        atol=1e-12,
    )
    assert np.max(abs(tr.q - sol.y[0])) < 2e-7
    assert np.max(abs(tr.qd_raw - sol.y[1])) < 2e-6


def test_invalid_models_and_observations_rejected():
    c = load_config()
    bad = PublicModel(
        c.dt, c.duration_s, c.q0, c.qd0, 0.0, 0.0, c.arm_length, c.gravity, c.kp, c.kd
    )
    with pytest.raises(ValueError):
        simulate_trajectory(bad, np.zeros(3), delay_s=0)
    with pytest.raises(ValueError):
        simulate_trajectory(
            PublicModel(
                c.dt,
                c.duration_s,
                c.q0,
                c.qd0,
                c.arm_mass,
                c.payload_mass,
                c.arm_length,
                c.gravity,
                c.kp,
                c.kd,
                0,
            ),
            np.zeros(3),
            delay_s=0,
        )
    d = build_benchmark(c)
    badobs = Observations(d.fit.t + 0.1, d.fit.q_des, d.fit.q, d.fit.qd)
    with pytest.raises(ValueError):
        fit_student(badobs, c.model)
    with pytest.raises(ValueError):
        simulate_trajectory(c.model, np.array([0.0, np.nan]), delay_s=0)


def test_varied_optimizer_starts_and_replay_geometry():
    r = run_l1()
    for start in (0.0, 0.03, 0.12, 0.2):
        f = fit_student(
            r.data.fit,
            r.config.model,
            optimizer_start=Params(start),
            lower=r.config.lower,
            upper=r.config.upper,
        )
        assert abs(f.params.delay_s - r.config.truth.delay_s) <= 1e-3
    frame = machine_frame(r, "validation", len(r.data.validation.t) // 2, "oracle")
    q = frame["q"]
    L = r.config.arm_length
    assert np.allclose(frame["tip"], [L * np.sin(q), -L * np.cos(q)])
    assert "gravity" in machine_svg(r) and "identified" in machine_svg(r)


def test_outputs_immutable_and_deterministic_report(tmp_path):
    r = run_l1()
    with pytest.raises(ValueError):
        r.trajectories["fit"]["oracle"].q[0] = 1
    p = write_report(r, tmp_path)
    first = (tmp_path / "metrics.json").read_bytes()
    write_report(r, tmp_path)
    assert first == (tmp_path / "metrics.json").read_bytes()
    assert p.exists()
    metrics = json.loads(first)
    assert len(metrics["local_loss_slice"]) == 9


def test_replay_views_use_all_recorded_roles_without_running_models(
    monkeypatch, tmp_path
):
    import xml.etree.ElementTree as ET

    r = run_l1()

    def forbidden(*args, **kwargs):
        raise AssertionError("Replay attempted fitting or simulation")

    monkeypatch.setattr(l1, "simulate_trajectory", forbidden)
    monkeypatch.setattr(l1, "fit_student", forbidden)
    for split in ("fit", "validation"):
        for index in (0, 217, 800, 1600):
            svg = ET.fromstring(machine_svg(r, split, index))
            lines = {
                e.attrib["data-role"]: e.attrib
                for e in svg.iter()
                if "data-role" in e.attrib
            }
            for role in ("oracle", "initial", "identified"):
                tr = r.trajectories[split][role]
                frame = machine_frame(r, split, index, role)
                assert frame["q"] == tr.q[index]
                assert frame["qd"] == tr.qd[index]
                np.testing.assert_allclose(
                    frame["tip_velocity"],
                    [
                        r.config.arm_length * np.cos(tr.q[index]) * tr.qd[index],
                        r.config.arm_length * np.sin(tr.q[index]) * tr.qd[index],
                    ],
                )
                assert float(lines[role]["x2"]) == pytest.approx(
                    250 + 150 * np.sin(tr.q[index]), abs=1e-6
                )
                assert float(lines[role]["y2"]) == pytest.approx(
                    95 + 150 * np.cos(tr.q[index]), abs=1e-6
                )
    run_summary(r)
    plot_run(r, tmp_path / "replay.png")


def test_fitter_cannot_use_poisoned_oracle_or_validation(monkeypatch):
    from dataclasses import fields

    c = load_config()
    observations = build_benchmark(c).fit
    assert {f.name for f in fields(Observations)} == {"t", "q_des", "q", "qd"}
    assert "truth" not in {f.name for f in fields(PublicModel)}

    def forbidden(*args, **kwargs):
        raise AssertionError("Fitter reached generator, evaluator, or config")

    for name in ("load_config", "build_benchmark", "score", "run_summary"):
        monkeypatch.setattr(l1, name, forbidden)
    fitted = fit_student(
        observations,
        c.model,
        optimizer_start=c.optimizer_start,
        lower=c.lower,
        upper=c.upper,
    )
    assert fitted.params.delay_s == pytest.approx(0.08, abs=0.001)
    with pytest.raises(TypeError, match="PublicModel"):
        fit_student(observations, c)


def test_app_graph_separates_submission_from_replay():
    pytest.importorskip("marimo")
    from apps.l1_servo_loaded_pendulum import app

    cells = [cell._cell for cell in app._cell_manager.cells()]
    fit_cell = next(cell for cell in cells if "completed_run" in cell.defs)
    assert "run_identification" in fit_cell.refs
    assert {"initial_delay", "timeline", "signal_view", "machine_split"}.isdisjoint(
        fit_cell.refs
    )
    replay = next(
        cell
        for cell in cells
        if {"machine_svg", "completed_run", "timeline"} <= cell.refs
    )
    assert {
        "run_l1",
        "fit_student",
        "simulate_trajectory",
        "build_benchmark",
    }.isdisjoint(replay.refs)
