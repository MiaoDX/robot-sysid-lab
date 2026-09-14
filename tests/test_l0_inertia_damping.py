import json
from pathlib import Path

import numpy as np
import pytest

from synthetic.l0_inertia_damping import (
    Params,
    analytical_constant_input,
    build_benchmark,
    fit_student,
    load_config,
    local_sensitivity,
    run_l0,
    simulate,
    write_report,
)


def test_simulation_matches_independent_constant_input_reference():
    params = Params(inertia=0.065, damping=0.055)
    t = np.arange(0.0, 2.0, 0.01)
    u = np.full_like(t, 0.2)

    simulated_q, simulated_qd = simulate(params, t, u, q0=0.3, qd0=-0.1)
    reference_q, reference_qd = analytical_constant_input(
        params, t, 0.2, q0=0.3, qd0=-0.1
    )

    np.testing.assert_allclose(simulated_q, reference_q, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(simulated_qd, reference_qd, rtol=1e-12, atol=1e-12)


def test_zero_input_dissipates_velocity_energy():
    params = Params(inertia=0.065, damping=0.055)
    t = np.arange(0.0, 2.0, 0.01)
    q, qd = simulate(params, t, np.zeros_like(t), qd0=2.0)

    assert np.all(np.isfinite(q))
    assert np.all(np.diff(0.5 * params.inertia * qd**2) <= 1e-12)
    assert abs(qd[-1]) < abs(qd[0])


@pytest.mark.parametrize(
    "params,t,u,error",
    [
        (Params(inertia=0.0, damping=0.1), np.array([0.0, 0.1]), np.zeros(2), "inertia"),
        (Params(inertia=0.1, damping=-0.1), np.array([0.0, 0.1]), np.zeros(2), "damping"),
        (Params(inertia=0.1, damping=0.1), np.array([0.0]), np.zeros(1), "at least two"),
        (Params(inertia=0.1, damping=0.1), np.array([0.0, 0.1]), np.zeros(3), "same shape"),
        (Params(inertia=0.1, damping=0.1), np.array([0.0, 0.2, 0.3]), np.zeros(3), "uniformly"),
    ],
)
def test_invalid_simulation_inputs_fail_explicitly(params, t, u, error):
    with pytest.raises(ValueError, match=error):
        simulate(params, t, u)


def test_l0_recovers_truth_and_improves_held_out_prediction():
    run = run_l0()

    assert run.fit.success
    assert run.fit.params.inertia == pytest.approx(run.config.truth.inertia, rel=1e-8)
    assert run.fit.params.damping == pytest.approx(run.config.truth.damping, rel=1e-8)
    assert run.identified_validation_metrics.q_mae < run.nominal_validation_metrics.q_mae
    assert run.identified_validation_metrics.qd_mae < run.nominal_validation_metrics.qd_mae
    assert run.sensitivity.singular_values[-1] > 0.0


def test_fit_api_accepts_observations_only():
    config = load_config()
    data = build_benchmark(config)
    fitted = fit_student(
        data.fit,
        initial_guess=config.nominal,
        lower_bounds=config.lower_bounds,
        upper_bounds=config.upper_bounds,
    )

    assert fitted.params.inertia == pytest.approx(config.truth.inertia)
    assert fitted.params.damping == pytest.approx(config.truth.damping)


def test_report_contains_one_run_metadata_and_visual(tmp_path):
    report_path = write_report(run_l0(), tmp_path)

    assert report_path.name == "report.md"
    assert (tmp_path / "report.png").stat().st_size > 0
    metrics = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["config_version"] == "l0-inertia-damping-v1"
    assert metrics["metadata"]["observations"] == ["t", "u", "q", "qd"]
    report = report_path.read_text(encoding="utf-8")
    assert "Oracle" in report
    assert "pre-identification" in report
    assert "held-out multisine" in report
    assert "How to read this report" in report


def test_l0_lesson_set_and_pipeline_contract_exist():
    lesson_root = Path("docs/lessons/l0")
    assert (lesson_root / "README.md").is_file()
    assert len(list(lesson_root.glob("*.md"))) == 5
    pipeline = Path("docs/lesson_pipeline.md").read_text(encoding="utf-8")
    assert "The shared flow" in pipeline
    assert "Artifact contract" in pipeline


def test_sensitivity_is_finite_for_default_fit():
    config = load_config()
    data = build_benchmark(config)
    sensitivity = local_sensitivity(data.fit, config.truth)

    assert np.all(np.isfinite(sensitivity.singular_values))
    assert np.isfinite(sensitivity.condition_number)


def test_notebook_is_valid_and_uses_shared_l0_runner():
    notebook = json.loads(
        Path("notebooks/l0_inertia_damping.ipynb").read_text(encoding="utf-8")
    )
    code = "\n".join(
        "".join(cell["source"])
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )

    assert notebook["nbformat"] == 4
    assert "run_l0" in code
    assert "plot_run" in code
    assert "l0_config.json" in code
