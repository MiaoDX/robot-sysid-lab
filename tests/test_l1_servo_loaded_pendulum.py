"""Focused numerical and leakage contract tests for L1."""
import inspect, json
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from synthetic.l1_servo_loaded_pendulum import *
import synthetic.l1_servo_loaded_pendulum as l1


def test_delay_recovery_and_validation_thresholds():
    r = run_l1()
    assert r.fit.success
    assert abs(r.fit.params.delay_s - r.config.truth.delay_s) <= 1e-3
    assert (1 - r.identified_validation.q_rmse / r.initial_validation.q_rmse) >= .9
    assert (1 - r.identified_validation.qd_rmse / r.initial_validation.qd_rmse) >= .9


def test_public_fitter_has_no_oracle_or_validation_arguments():
    sig = inspect.signature(fit_student)
    assert list(sig.parameters) == ["observations", "model", "optimizer_start", "lower", "upper"]
    assert "config" not in sig.parameters and "validation" not in sig.parameters
    r = run_l1()
    poison = Observations(r.data.fit.t, r.data.fit.q_des, r.data.fit.q + 10, r.data.fit.qd + 10)
    fit = fit_student(poison, r.config.model, optimizer_start=Params(.03))
    assert fit.params.delay_s != pytest.approx(r.fit.params.delay_s, abs=1e-3)


def test_full_pd_delay_differs_from_input_only_delay():
    r = run_l1(); m = r.config.model; qdes = r.data.fit.q_des
    delayed = simulate_trajectory(m, qdes, delay_s=.08)
    shifted = np.r_[np.zeros(16), qdes[:-16]]
    input_only = simulate_trajectory(m, shifted, delay_s=0)
    assert np.max(abs(delayed.q - input_only.q)) > 1e-3


def test_fractional_delay_zero_prehistory_and_no_future_read():
    h = np.array([1., 3., 7.])
    assert l1._delayed(h, 0, .5, 1.) == pytest.approx(.5)
    assert l1._delayed(h, 1, .5, 1.) == pytest.approx(2.)
    assert l1._delayed(h, 2, 0., 1.) == pytest.approx(7.)


def test_derive_velocity_definition_and_known_reset():
    q = np.array([0., 1., 3., 6.]); assert np.allclose(derive_velocity(q, 1.), [1., 1.5, 2.5, 3.])
    r = run_l1(); tr = r.trajectories['fit']['initial']; assert tr.qd_raw[0] == pytest.approx(r.config.model.qd0)


def test_gravity_dynamics_matches_independent_solve_ivp():
    m = PublicModel(.002, .2, .3, -.2, 1.2, .35, .6, 9.81, 0., 0., 2)
    qdes = np.zeros(101); tr = simulate_trajectory(m, qdes, delay_s=0.)
    sol = solve_ivp(lambda t, x: (x[1], -m.gravity_moment*np.sin(x[0])/m.inertia), [0, .2], [m.q0, m.qd0], t_eval=tr.t, rtol=1e-10, atol=1e-12)
    assert np.max(abs(tr.q - sol.y[0])) < 2e-7
    assert np.max(abs(tr.qd_raw - sol.y[1])) < 2e-6


def test_invalid_models_and_observations_rejected():
    c = load_config(); bad = PublicModel(c.dt, c.duration_s, c.q0, c.qd0, 0., 0., c.arm_length, c.gravity, c.kp, c.kd)
    with pytest.raises(ValueError): simulate_trajectory(bad, np.zeros(3), delay_s=0)
    with pytest.raises(ValueError): simulate_trajectory(PublicModel(c.dt,c.duration_s,c.q0,c.qd0,c.arm_mass,c.payload_mass,c.arm_length,c.gravity,c.kp,c.kd,0), np.zeros(3), delay_s=0)
    d = build_benchmark(c); badobs = Observations(d.fit.t + .1, d.fit.q_des, d.fit.q, d.fit.qd)
    with pytest.raises(ValueError): fit_student(badobs, c.model)
    with pytest.raises(ValueError): simulate_trajectory(c.model, np.array([0., np.nan]), delay_s=0)


def test_varied_optimizer_starts_and_replay_geometry():
    r = run_l1()
    for start in (0., .03, .12, .2):
        f = fit_student(r.data.fit, r.config.model, optimizer_start=Params(start), lower=r.config.lower, upper=r.config.upper)
        assert abs(f.params.delay_s - r.config.truth.delay_s) <= 1e-3
    frame = machine_frame(r, 'validation', len(r.data.validation.t)//2, 'oracle'); q = frame['q']; L = r.config.arm_length
    assert np.allclose(frame['tip'], [L*np.sin(q), -L*np.cos(q)])
    assert 'gravity' in machine_svg(r) and 'identified' in machine_svg(r)


def test_outputs_immutable_and_deterministic_report(tmp_path):
    r = run_l1();
    with pytest.raises(ValueError): r.trajectories['fit']['oracle'].q[0] = 1
    p = write_report(r, tmp_path); first = (tmp_path/'metrics.json').read_bytes(); write_report(r, tmp_path); assert first == (tmp_path/'metrics.json').read_bytes(); assert p.exists()
    metrics = json.loads(first); assert len(metrics['local_loss_slice']) == 9
