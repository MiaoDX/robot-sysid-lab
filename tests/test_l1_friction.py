"""Focused contract tests for the L1 friction extension."""

import inspect
import json
from pathlib import Path

import numpy as np
import pytest

from synthetic.l1_friction import (
    Observations,
    Params,
    build_benchmark,
    fit_student,
    load_config,
    reversal_indices,
    run_l1_f,
)
import synthetic.l1_friction as l1f


def test_pilot_recovers_friction_and_improves_held_out_prediction():
    run = run_l1_f()
    assert run.viscous_fit.success and run.friction_fit.success
    assert run.friction_fit.params.damping == pytest.approx(run.config.truth.damping, abs=2e-3)
    assert run.friction_fit.params.coulomb == pytest.approx(run.config.truth.coulomb, abs=2e-3)
    viscous = run.metrics["validation"]["viscous"]
    friction = run.metrics["validation"]["friction"]
    assert friction.q_rmse <= run.config.validation_error_ratio_max * viscous.q_rmse
    assert friction.qd_rmse <= run.config.validation_error_ratio_max * viscous.qd_rmse


def test_fit_api_exposes_only_public_observations_and_model():
    signature = inspect.signature(fit_student)
    assert list(signature.parameters) == [
        "observations", "model", "structure", "optimizer_start", "lower", "upper"
    ]
    config = load_config()
    data = build_benchmark(config)
    assert {"t", "u", "q", "qd"} == set(Observations.__dataclass_fields__)
    assert "truth" not in config.model.__dataclass_fields__
    fit = fit_student(
        data.fit, config.model, structure="friction", optimizer_start=config.friction_initial,
        lower=config.lower, upper=config.upper,
    )
    poisoned = Observations(data.fit.t, data.fit.u, data.fit.q + 1.0, data.fit.qd)
    changed = fit_student(
        poisoned, config.model, structure="friction", optimizer_start=config.friction_initial,
        lower=config.lower, upper=config.upper,
    )
    assert changed.params.coulomb != pytest.approx(fit.params.coulomb, abs=1e-3)


def test_viscous_student_has_zero_coulomb_term_and_fitter_cannot_see_validation(monkeypatch):
    config = load_config()
    data = build_benchmark(config)

    def forbidden(*args, **kwargs):
        raise AssertionError("fitter reached benchmark/evaluator")

    monkeypatch.setattr(l1f, "build_benchmark", forbidden)
    fit = fit_student(
        data.fit, config.model, structure="viscous", optimizer_start=config.viscous_initial,
        lower=Params(config.lower.damping, 0.0), upper=Params(config.upper.damping, 0.0),
    )
    assert fit.params.coulomb == 0.0


def test_reversal_metric_has_bidirectional_fit_and_validation_data():
    run = run_l1_f()
    assert len(reversal_indices(run.data.fit.qd)) >= 3
    assert len(reversal_indices(run.data.validation.qd)) >= 3
    assert run.reversal_metrics["validation"]["friction"] < run.reversal_metrics["validation"]["viscous"]


def test_observation_arrays_are_finite_and_read_only():
    data = build_benchmark(load_config())
    assert all(np.all(np.isfinite(a)) for a in (data.fit.t, data.fit.u, data.fit.q, data.fit.qd))
    with pytest.raises(ValueError):
        data.fit.q[0] = 1.0


def test_report_contains_frozen_thresholds_and_visual(tmp_path):
    run = run_l1_f()
    report = l1f.write_report(run, tmp_path)
    assert report.is_file()
    assert (tmp_path / "report.png").stat().st_size > 0
    assert (tmp_path / "metrics.json").is_file()
    text = report.read_text(encoding="utf-8")
    assert "Thresholds were frozen after the pilot" in text
    assert "held-out reversal-window" in text


def test_notebook_and_embedded_lesson_contract_exist():
    notebook = json.loads(Path("notebooks/l1_friction.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    code = "\n".join("".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code")
    assert "run_l1_f" in code and "write_report" in code
    lesson = Path("docs/lessons/l1/index.md").read_text(encoding="utf-8")
    lesson_zh = Path("docs/lessons/l1/index.zh-CN.md").read_text(encoding="utf-8")
    assert "Extension: friction versus viscous damping" in lesson
    assert "扩展：摩擦与黏性阻尼" in lesson_zh
