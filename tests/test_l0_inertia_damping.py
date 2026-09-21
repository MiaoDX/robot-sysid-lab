import ast
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from synthetic.l0_inertia_damping import (
    Params,
    analytical_constant_input,
    build_benchmark,
    fit_l0,
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


def test_prepared_oracle_data_can_be_reused_for_another_student_start():
    config = load_config()
    prepared_data = build_benchmark(config)
    changed_config = replace(
        config,
        nominal=Params(inertia=0.12, damping=0.08),
    )

    run = fit_l0(changed_config, prepared_data)

    assert run.data is prepared_data
    assert run.config.nominal == changed_config.nominal
    assert run.fit.params.inertia == pytest.approx(config.truth.inertia)
    assert run.fit.params.damping == pytest.approx(config.truth.damping)


def test_prepared_data_rejects_a_different_oracle_contract():
    config = load_config()
    prepared_data = build_benchmark(config)

    with pytest.raises(ValueError, match="Oracle truth"):
        fit_l0(
            replace(config, truth=Params(inertia=0.07, damping=0.055)),
            prepared_data,
        )


def test_report_contains_one_run_metadata_and_visual(tmp_path):
    report_path = write_report(run_l0(), tmp_path)

    assert report_path.name == "report.md"
    assert (tmp_path / "report.png").stat().st_size > 0
    metrics = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["config_version"] == "l0-inertia-damping-v1"
    assert metrics["metadata"]["observations"] == ["t", "u", "q", "qd"]
    report = report_path.read_text(encoding="utf-8")
    assert "True system (Oracle)" in report
    assert "Initial model" in report
    assert "Identified model" in report
    assert "held-out multisine" in report
    assert "frequency sweeps from low to high" in report
    assert "How to read this report" in report
    assert "`nominal` for compatibility" in report
    assert "Curve key" in report


def test_l0_learner_path_does_not_carry_operator_material():
    """The lesson README is the learner path; verification material lives elsewhere.

    Reproduction commands, the privileged-signal contract, and the acceptance
    checklist serve the verifier, not the learner, and used to sit in the entry
    point where they were the first thing a reader met.
    """

    lesson = Path("docs/lessons/l0/README.md").read_text(encoding="utf-8")
    verification_path = Path("reports/l0_inertia_damping/verification.md")
    verification = verification_path.read_text(encoding="utf-8")

    assert "verification.md" in lesson
    assert "Learner acceptance walkthrough" not in lesson
    assert "pytest" not in lesson
    assert "Learner acceptance walkthrough" in verification


def test_l0_lesson_set_and_pipeline_contract_exist():
    lesson_root = Path("docs/lessons/l0")
    assert (lesson_root / "README.md").is_file()
    english_notes = [p for p in lesson_root.glob("*.md") if ".zh-CN." not in p.name]
    assert {"index.md", "README.md", "00-orientation.md", "01-physics-to-data.md", "02-fit-to-validation.md", "03-assumptions-and-next-step.md"} <= {p.name for p in english_notes}
    assert all(p.with_name(p.stem + ".zh-CN.md").is_file() for p in english_notes)
    pipeline = Path("docs/lesson_pipeline.md").read_text(encoding="utf-8")
    assert "The shared flow" in pipeline
    assert "Artifact contract" in pipeline


def test_rendered_course_map_defines_canonical_tracks_and_l0_entry():
    course_map = Path("docs/course/index.html").read_text(encoding="utf-8")

    assert "K0-K8" in course_map
    assert "L0-L6" in course_map
    assert "H0-H2" in course_map
    assert 'id="hero-k0-link"' in course_map
    assert 'href="../lessons/k0/index.html"' in course_map
    assert 'href="../lessons/k1/index.html"' in course_map
    assert 'href="../lessons/l0/index.html"' in course_map
    assert "site/language.js" in course_map


def test_marimo_preview_reuses_shared_l0_runner():
    preview = Path("apps/l0_inertia_damping.py").read_text(encoding="utf-8")
    assert "from synthetic.l0_inertia_damping import" in preview
    assert "fit_l0(fitted_config, prepared_data)" in preview
    assert "Completed at" in preview
    assert 'fit_state = "succeeded"' in preview
    assert "Run identification" in preview
    assert "Fit and validation side by side" in preview
    assert "Known observations:" in preview
    assert "Unknown parameters:" in preview
    assert "Initial model" in preview
    assert "Nominal Student" not in preview
    assert "3, 2, figsize" in preview
    assert "mo.ui.tabs" not in preview
    assert 'id="why"' in preview
    assert 'id="boundary"' in preview
    assert 'id="experiment"' in preview
    assert 'id="evidence"' in preview
    assert 'id="limits"' in preview
    assert r"J\ddot{q} + b\dot{q} = u" in preview
    assert "J * qdd + b * qd = u" not in preview
    assert "WHAT SYSID GIVES US" in preview
    assert "THE REPEATED LOOP" in preview
    assert "fit_student" not in preview
    assert "dashed + markers" in preview
    assert "True system (Oracle), evaluation only" in preview
    assert "Fit / chirp" in preview
    assert "held-out multisine" in preview
    assert 'href="#experiment"' not in preview
    assert '<span>Experiment</span>' in preview


def test_marimo_slider_changes_do_not_trigger_refit():
    preview_source = Path("apps/l0_inertia_damping.py").read_text(encoding="utf-8")
    tree = ast.parse(preview_source)
    cells = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    fit_cell = next(
        cell
        for cell in cells
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "fit_l0"
            for node in ast.walk(cell)
        )
    )
    dependencies = {argument.arg for argument in fit_cell.args.args}

    assert "split_control" not in preview_source
    assert {"inertia_control", "damping_control"}.isdisjoint(dependencies)
    assert "run_identification" in dependencies


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
