"""L0 analytical inertia/damping system-identification lesson.

The benchmark identifies the two parameters in ``J*qdd + b*qd = u`` from
position and velocity observations. Oracle truth stays in the benchmark
generator and evaluation result; ``fit_student`` only accepts observations,
public bounds, and a non-truth initial guess.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares


DEFAULT_CONFIG_PATH = Path(__file__).with_name("l0_config.json")


@dataclass(frozen=True)
class Params:
    """Physical parameters for the L0 rotational plant."""

    inertia: float
    damping: float


@dataclass(frozen=True)
class L0Config:
    """Versioned public and hidden configuration for one benchmark run."""

    version: str
    dt: float
    duration_s: float
    q0: float
    qd0: float
    truth: Params
    nominal: Params
    lower_bounds: Params
    upper_bounds: Params
    chirp_f0_hz: float
    chirp_f1_hz: float
    chirp_amplitude_nm: float
    validation_frequencies_hz: tuple[float, ...]
    validation_amplitudes_nm: tuple[float, ...]
    validation_phases_rad: tuple[float, ...]


@dataclass(frozen=True)
class Observations:
    """Signals visible to the estimator for one trajectory."""

    t: np.ndarray
    u: np.ndarray
    q: np.ndarray
    qd: np.ndarray


@dataclass(frozen=True)
class BenchmarkData:
    fit: Observations
    validation: Observations
    metadata: Mapping[str, Any]
    truth: Params


@dataclass(frozen=True)
class Metrics:
    q_mae: float
    qd_mae: float
    q_rmse: float
    qd_rmse: float


@dataclass(frozen=True)
class Sensitivity:
    singular_values: tuple[float, ...]
    condition_number: float


@dataclass(frozen=True)
class FitResult:
    params: Params
    success: bool
    message: str
    cost: float
    nfev: int
    njev: int
    scales: tuple[float, float]


@dataclass(frozen=True)
class L0Run:
    config: L0Config
    data: BenchmarkData
    fit: FitResult
    nominal_fit_metrics: Metrics
    identified_fit_metrics: Metrics
    nominal_validation_metrics: Metrics
    identified_validation_metrics: Metrics
    sensitivity: Sensitivity


def _params_from_mapping(value: Mapping[str, Any]) -> Params:
    return Params(inertia=float(value["inertia"]), damping=float(value["damping"]))


def load_config(path: str | Path | None = None) -> L0Config:
    """Load the versioned example configuration."""

    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    with config_path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    return L0Config(
        version=str(raw["version"]),
        dt=float(raw["dt"]),
        duration_s=float(raw["duration_s"]),
        q0=float(raw["initial_state"]["q"]),
        qd0=float(raw["initial_state"]["qd"]),
        truth=_params_from_mapping(raw["truth"]),
        nominal=_params_from_mapping(raw["nominal"]),
        lower_bounds=_params_from_mapping(raw["bounds"]["lower"]),
        upper_bounds=_params_from_mapping(raw["bounds"]["upper"]),
        chirp_f0_hz=float(raw["fit_excitation"]["f0_hz"]),
        chirp_f1_hz=float(raw["fit_excitation"]["f1_hz"]),
        chirp_amplitude_nm=float(raw["fit_excitation"]["amplitude_nm"]),
        validation_frequencies_hz=tuple(
            float(value) for value in raw["validation_excitation"]["frequencies_hz"]
        ),
        validation_amplitudes_nm=tuple(
            float(value) for value in raw["validation_excitation"]["amplitudes_nm"]
        ),
        validation_phases_rad=tuple(
            float(value) for value in raw["validation_excitation"]["phases_rad"]
        ),
    )


def _validate_params(params: Params) -> None:
    if not np.isfinite(params.inertia) or params.inertia <= 0.0:
        raise ValueError("inertia must be finite and greater than zero")
    if not np.isfinite(params.damping) or params.damping < 0.0:
        raise ValueError("damping must be finite and non-negative")


def _validate_samples(t: np.ndarray, u: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    t_array = np.asarray(t, dtype=float)
    u_array = np.asarray(u, dtype=float)
    if t_array.ndim != 1 or t_array.size < 2:
        raise ValueError("t must be a one-dimensional array with at least two samples")
    if u_array.shape != t_array.shape:
        raise ValueError("u must have the same shape as t")
    if not np.all(np.isfinite(t_array)) or not np.all(np.isfinite(u_array)):
        raise ValueError("t and u must contain only finite values")
    steps = np.diff(t_array)
    if np.any(steps <= 0.0):
        raise ValueError("t must be strictly increasing")
    dt = float(steps[0])
    if not np.allclose(steps, dt, rtol=1e-9, atol=1e-12):
        raise ValueError("t must be uniformly sampled")
    return t_array, u_array, dt


def simulate(
    params: Params,
    t: np.ndarray,
    u: np.ndarray,
    *,
    q0: float = 0.0,
    qd0: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Simulate with zero-order-held input over each sample interval."""

    _validate_params(params)
    t_array, u_array, dt = _validate_samples(t, u)
    if not np.isfinite(q0) or not np.isfinite(qd0):
        raise ValueError("initial state must be finite")

    q = np.empty_like(t_array)
    qd = np.empty_like(t_array)
    q[0] = float(q0)
    qd[0] = float(qd0)

    for index in range(t_array.size - 1):
        torque = u_array[index]
        if params.damping > 1e-14:
            v_inf = torque / params.damping
            decay = np.exp(-params.damping * dt / params.inertia)
            qd[index + 1] = v_inf + (qd[index] - v_inf) * decay
            q[index + 1] = (
                q[index]
                + v_inf * dt
                + (qd[index] - v_inf)
                * (params.inertia / params.damping)
                * (1.0 - decay)
            )
        else:
            acceleration = torque / params.inertia
            qd[index + 1] = qd[index] + acceleration * dt
            q[index + 1] = q[index] + qd[index] * dt + 0.5 * acceleration * dt**2
    return q, qd


def analytical_constant_input(
    params: Params,
    t: np.ndarray,
    torque: float,
    *,
    q0: float = 0.0,
    qd0: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Independent closed-form reference for one constant applied torque."""

    _validate_params(params)
    t_array, _, _ = _validate_samples(
        t, np.full_like(np.asarray(t, dtype=float), torque)
    )
    if not np.isfinite(torque) or not np.isfinite(q0) or not np.isfinite(qd0):
        raise ValueError("torque and initial state must be finite")
    elapsed = t_array - t_array[0]
    if params.damping > 1e-14:
        v_inf = torque / params.damping
        decay = np.exp(-params.damping * elapsed / params.inertia)
        qd = v_inf + (qd0 - v_inf) * decay
        q = q0 + v_inf * elapsed + (qd0 - v_inf) * (
            params.inertia / params.damping
        ) * (1.0 - decay)
    else:
        acceleration = torque / params.inertia
        qd = qd0 + acceleration * elapsed
        q = q0 + qd0 * elapsed + 0.5 * acceleration * elapsed**2
    return q, qd


def make_time(config: L0Config) -> np.ndarray:
    if config.dt <= 0.0 or config.duration_s <= config.dt:
        raise ValueError("duration_s must be greater than a positive dt")
    count = int(round(config.duration_s / config.dt))
    return np.arange(count, dtype=float) * config.dt


def chirp_command(
    t: np.ndarray,
    *,
    f0_hz: float,
    f1_hz: float,
    amplitude_nm: float,
    duration_s: float,
) -> np.ndarray:
    if duration_s <= 0.0 or f0_hz < 0.0 or f1_hz < f0_hz or amplitude_nm < 0.0:
        raise ValueError("invalid chirp configuration")
    elapsed = np.asarray(t, dtype=float) - float(np.asarray(t, dtype=float)[0])
    rate = (f1_hz - f0_hz) / duration_s
    phase = 2.0 * np.pi * (f0_hz * elapsed + 0.5 * rate * elapsed**2)
    return amplitude_nm * np.sin(phase)


def multisine_command(
    t: np.ndarray,
    *,
    frequencies_hz: Sequence[float],
    amplitudes_nm: Sequence[float],
    phases_rad: Sequence[float],
) -> np.ndarray:
    if not (
        len(frequencies_hz) == len(amplitudes_nm) == len(phases_rad)
    ) or not frequencies_hz:
        raise ValueError("multisine components must have equal non-zero lengths")
    elapsed = np.asarray(t, dtype=float) - float(np.asarray(t, dtype=float)[0])
    result = np.zeros_like(elapsed, dtype=float)
    for frequency, amplitude, phase in zip(
        frequencies_hz, amplitudes_nm, phases_rad
    ):
        if frequency < 0.0 or amplitude < 0.0:
            raise ValueError("multisine frequency and amplitude must be non-negative")
        result += amplitude * np.sin(2.0 * np.pi * frequency * elapsed + phase)
    return result


def build_benchmark(config: L0Config) -> BenchmarkData:
    """Generate separated fit/validation observations from the hidden Oracle."""

    time = make_time(config)
    fit_input = chirp_command(
        time,
        f0_hz=config.chirp_f0_hz,
        f1_hz=config.chirp_f1_hz,
        amplitude_nm=config.chirp_amplitude_nm,
        duration_s=config.duration_s,
    )
    validation_input = multisine_command(
        time,
        frequencies_hz=config.validation_frequencies_hz,
        amplitudes_nm=config.validation_amplitudes_nm,
        phases_rad=config.validation_phases_rad,
    )
    fit_q, fit_qd = simulate(config.truth, time, fit_input, q0=config.q0, qd0=config.qd0)
    validation_q, validation_qd = simulate(
        config.truth, time, validation_input, q0=config.q0, qd0=config.qd0
    )
    metadata = {
        "config_version": config.version,
        "model": "J*qdd + b*qd = u",
        "input_boundary": "known applied joint torque u in N m",
        "observations": ["t", "u", "q", "qd"],
        "initial_state": {"q": config.q0, "qd": config.qd0},
        "dt_s": config.dt,
        "duration_s": config.duration_s,
        "fit_excitation": "chirp",
        "validation_excitation": "multisine",
    }
    return BenchmarkData(
        fit=Observations(time, fit_input, fit_q, fit_qd),
        validation=Observations(time, validation_input, validation_q, validation_qd),
        metadata=metadata,
        truth=config.truth,
    )


def _validate_bounds(initial_guess: Params, lower: Params, upper: Params) -> None:
    _validate_params(initial_guess)
    _validate_params(lower)
    _validate_params(upper)
    if lower.inertia >= upper.inertia or lower.damping >= upper.damping:
        raise ValueError("each lower bound must be less than its upper bound")
    if not (
        lower.inertia <= initial_guess.inertia <= upper.inertia
        and lower.damping <= initial_guess.damping <= upper.damping
    ):
        raise ValueError("initial guess must lie inside the bounds")


def _vector_to_params(vector: np.ndarray) -> Params:
    return Params(inertia=float(vector[0]), damping=float(vector[1]))


def fit_student(
    observations: Observations,
    *,
    initial_guess: Params,
    lower_bounds: Params,
    upper_bounds: Params,
) -> FitResult:
    """Fit J and b using only observations and public bounds."""

    _validate_bounds(initial_guess, lower_bounds, upper_bounds)
    t, u, q, qd = observations.t, observations.u, observations.q, observations.qd
    if not (q.shape == qd.shape == np.asarray(t).shape):
        raise ValueError("observations must have matching t, q, and qd shapes")
    q_scale = max(float(np.std(q)), 1e-6)
    qd_scale = max(float(np.std(qd)), 1e-6)

    def residual(vector: np.ndarray) -> np.ndarray:
        params = _vector_to_params(vector)
        predicted_q, predicted_qd = simulate(
            params, t, u, q0=float(q[0]), qd0=float(qd[0])
        )
        return np.concatenate(
            ((predicted_q - q) / q_scale, (predicted_qd - qd) / qd_scale)
        )

    result = least_squares(
        residual,
        x0=np.array([initial_guess.inertia, initial_guess.damping], dtype=float),
        bounds=(
            np.array([lower_bounds.inertia, lower_bounds.damping], dtype=float),
            np.array([upper_bounds.inertia, upper_bounds.damping], dtype=float),
        ),
        method="trf",
        x_scale="jac",
        ftol=1e-12,
        xtol=1e-12,
        gtol=1e-12,
        max_nfev=500,
    )
    return FitResult(
        params=_vector_to_params(result.x),
        success=bool(result.success),
        message=str(result.message),
        cost=float(result.cost),
        nfev=int(result.nfev),
        njev=int(result.njev) if result.njev is not None else 0,
        scales=(q_scale, qd_scale),
    )


def score(params: Params, observations: Observations) -> Metrics:
    predicted_q, predicted_qd = simulate(
        params,
        observations.t,
        observations.u,
        q0=float(observations.q[0]),
        qd0=float(observations.qd[0]),
    )
    q_error = predicted_q - observations.q
    qd_error = predicted_qd - observations.qd
    return Metrics(
        q_mae=float(np.mean(np.abs(q_error))),
        qd_mae=float(np.mean(np.abs(qd_error))),
        q_rmse=float(np.sqrt(np.mean(q_error**2))),
        qd_rmse=float(np.sqrt(np.mean(qd_error**2))),
    )


def local_sensitivity(observations: Observations, params: Params) -> Sensitivity:
    """Return a lightweight finite-difference sensitivity diagnostic."""

    _validate_params(params)
    q_scale = max(float(np.std(observations.q)), 1e-6)
    qd_scale = max(float(np.std(observations.qd)), 1e-6)

    def output(vector: np.ndarray) -> np.ndarray:
        q, qd = simulate(
            _vector_to_params(vector),
            observations.t,
            observations.u,
            q0=float(observations.q[0]),
            qd0=float(observations.qd[0]),
        )
        return np.concatenate((q / q_scale, qd / qd_scale))

    vector = np.array([params.inertia, params.damping], dtype=float)
    columns = []
    for index in range(2):
        step = max(abs(vector[index]) * 1e-5, 1e-8)
        plus = vector.copy()
        minus = vector.copy()
        plus[index] += step
        minus[index] -= step
        if index == 0 and minus[index] <= 0.0:
            minus[index] = vector[index]
        columns.append((output(plus) - output(minus)) / (plus[index] - minus[index]))
    singular_values = np.linalg.svd(np.column_stack(columns), compute_uv=False)
    condition = (
        float(singular_values[0] / singular_values[-1])
        if singular_values[-1] > 0
        else float("inf")
    )
    return Sensitivity(tuple(float(value) for value in singular_values), condition)


def run_l0(config: L0Config | None = None) -> L0Run:
    config = config or load_config()
    data = build_benchmark(config)
    fit = fit_student(
        data.fit,
        initial_guess=config.nominal,
        lower_bounds=config.lower_bounds,
        upper_bounds=config.upper_bounds,
    )
    identified = fit.params
    return L0Run(
        config=config,
        data=data,
        fit=fit,
        nominal_fit_metrics=score(config.nominal, data.fit),
        identified_fit_metrics=score(identified, data.fit),
        nominal_validation_metrics=score(config.nominal, data.validation),
        identified_validation_metrics=score(identified, data.validation),
        sensitivity=local_sensitivity(data.fit, identified),
    )


def _metrics_dict(metrics: Metrics) -> dict[str, float]:
    return asdict(metrics)


def _params_dict(params: Params) -> dict[str, float]:
    return asdict(params)


def run_summary(run: L0Run) -> dict[str, Any]:
    truth = run.config.truth
    fitted = run.fit.params
    return {
        "config_version": run.config.version,
        "metadata": dict(run.data.metadata),
        "truth": _params_dict(truth),
        "nominal": _params_dict(run.config.nominal),
        "identified": _params_dict(fitted),
        "recovery_relative_error": {
            "inertia": abs(fitted.inertia - truth.inertia) / truth.inertia,
            "damping": abs(fitted.damping - truth.damping) / truth.damping,
        },
        "fit": {
            "nominal": _metrics_dict(run.nominal_fit_metrics),
            "identified": _metrics_dict(run.identified_fit_metrics),
        },
        "validation": {
            "nominal": _metrics_dict(run.nominal_validation_metrics),
            "identified": _metrics_dict(run.identified_validation_metrics),
        },
        "optimizer": {
            "success": run.fit.success,
            "message": run.fit.message,
            "cost": run.fit.cost,
            "nfev": run.fit.nfev,
            "njev": run.fit.njev,
            "scales": {"q": run.fit.scales[0], "qd": run.fit.scales[1]},
        },
        "sensitivity": asdict(run.sensitivity),
    }


def plot_run(run: L0Run, output_path: str | Path) -> Path:
    """Write the canonical static visual report for a run."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fit = run.data.fit
    validation = run.data.validation
    nominal_fit_q, nominal_fit_qd = simulate(
        run.config.nominal, fit.t, fit.u, q0=run.config.q0, qd0=run.config.qd0
    )
    identified_fit_q, identified_fit_qd = simulate(
        run.fit.params, fit.t, fit.u, q0=run.config.q0, qd0=run.config.qd0
    )
    nominal_val_q, nominal_val_qd = simulate(
        run.config.nominal,
        validation.t,
        validation.u,
        q0=run.config.q0,
        qd0=run.config.qd0,
    )
    identified_val_q, identified_val_qd = simulate(
        run.fit.params,
        validation.t,
        validation.u,
        q0=run.config.q0,
        qd0=run.config.qd0,
    )

    colors = {"oracle": "black", "nominal": "tab:orange", "identified": "tab:blue"}
    figure, axes = plt.subplots(5, 2, figsize=(14, 17), constrained_layout=True)
    plots = [
        (axes[0, 0], fit.t, fit.q, nominal_fit_q, identified_fit_q, "q (rad)", "Fit: position"),
        (axes[0, 1], validation.t, validation.q, nominal_val_q, identified_val_q, "q (rad)", "Validation: position"),
        (axes[1, 0], fit.t, fit.qd, nominal_fit_qd, identified_fit_qd, "qd (rad/s)", "Fit: velocity"),
        (axes[1, 1], validation.t, validation.qd, nominal_val_qd, identified_val_qd, "qd (rad/s)", "Validation: velocity"),
    ]
    for axis, time, oracle, nominal, identified, ylabel, title in plots:
        axis.plot(time, oracle, color=colors["oracle"], label="Oracle", linewidth=1.5)
        axis.plot(time, nominal, color=colors["nominal"], label="Nominal", linewidth=1.0)
        axis.plot(time, identified, color=colors["identified"], label="Identified", linewidth=1.0)
        axis.set(title=title, xlabel="time (s)", ylabel=ylabel)
        axis.grid(alpha=0.25)
        axis.legend()

    axes[2, 0].plot(fit.t, fit.u, color="tab:green")
    axes[2, 0].set(title="Fit: applied torque", xlabel="time (s)", ylabel="u (N m)")
    axes[2, 0].grid(alpha=0.25)
    axes[2, 1].plot(validation.t, validation.u, color="tab:green")
    axes[2, 1].set(title="Validation: applied torque", xlabel="time (s)", ylabel="u (N m)")
    axes[2, 1].grid(alpha=0.25)

    axes[3, 0].plot(fit.t, identified_fit_q - fit.q, color="tab:purple")
    axes[3, 0].set(title="Fit: position residual", xlabel="time (s)", ylabel="q error (rad)")
    axes[3, 0].grid(alpha=0.25)
    axes[3, 1].plot(fit.t, identified_fit_qd - fit.qd, color="tab:red")
    axes[3, 1].set(title="Fit: velocity residual", xlabel="time (s)", ylabel="qd error (rad/s)")
    axes[3, 1].grid(alpha=0.25)

    names = ["inertia J", "damping b"]
    truth = [run.config.truth.inertia, run.config.truth.damping]
    nominal = [run.config.nominal.inertia, run.config.nominal.damping]
    identified = [run.fit.params.inertia, run.fit.params.damping]
    x = np.arange(len(names))
    width = 0.24
    axes[4, 0].bar(x - width, truth, width, label="Oracle", color=colors["oracle"])
    axes[4, 0].bar(x, nominal, width, label="Nominal", color=colors["nominal"])
    axes[4, 0].bar(x + width, identified, width, label="Identified", color=colors["identified"])
    axes[4, 0].set(title="Parameter recovery", ylabel="value", xticks=x, xticklabels=names)
    axes[4, 0].grid(axis="y", alpha=0.25)
    axes[4, 0].legend()
    axes[4, 1].axis("off")
    axes[4, 1].text(
        0.02,
        0.95,
        "Sensitivity diagnostic\n"
        f"singular values: {run.sensitivity.singular_values[0]:.3g}, {run.sensitivity.singular_values[1]:.3g}\n"
        f"condition number: {run.sensitivity.condition_number:.3g}\n\n"
        "Fit and validation metrics are recorded\n"
        "in metrics.json alongside this figure.",
        va="top",
        fontsize=11,
    )
    figure.suptitle("L0: identify inertia and viscous damping", fontsize=16)
    figure.savefig(output, dpi=140)
    plt.close(figure)
    return output


def write_report(run: L0Run, output_dir: str | Path) -> Path:
    """Write JSON metadata, a static figure, and a readable Markdown report."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    plot_run(run, directory / "report.png")
    summary = run_summary(run)
    (directory / "metrics.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    fitted = run.fit.params
    truth = run.config.truth
    report = f"""# L0 inertia and damping identification

Configuration: `{run.config.version}`<br>
Plant boundary: known applied torque `u` in N m -> observed `q`, `qd`<br>
Fit excitation: chirp<br>
Validation excitation: held-out multisine

![Oracle, nominal, and identified trajectories](report.png)

| quantity | Oracle | Nominal | Identified |
|---|---:|---:|---:|
| inertia `J` (kg m^2) | {truth.inertia:.8f} | {run.config.nominal.inertia:.8f} | {fitted.inertia:.8f} |
| damping `b` (N m s/rad) | {truth.damping:.8f} | {run.config.nominal.damping:.8f} | {fitted.damping:.8f} |

| split/model | q MAE (rad) | qd MAE (rad/s) |
|---|---:|---:|
| fit / nominal | {run.nominal_fit_metrics.q_mae:.8g} | {run.nominal_fit_metrics.qd_mae:.8g} |
| fit / identified | {run.identified_fit_metrics.q_mae:.8g} | {run.identified_fit_metrics.qd_mae:.8g} |
| validation / nominal | {run.nominal_validation_metrics.q_mae:.8g} | {run.nominal_validation_metrics.qd_mae:.8g} |
| validation / identified | {run.identified_validation_metrics.q_mae:.8g} | {run.identified_validation_metrics.qd_mae:.8g} |

The estimator saw only fitting `t`, `u`, `q`, and `qd`, plus public bounds and
the non-truth nominal initialization. Oracle parameters are shown only in this
evaluation report. This matched, ideal-observation example demonstrates
recovery and held-out prediction; it does not establish model-mismatch or
real-robot transfer.
"""
    report_path = directory / "report.md"
    report_path.write_text(report, encoding="utf-8")
    return report_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/l0_inertia_damping"),
        help="directory for the generated report artifacts",
    )
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args(argv)
    run = run_l0(load_config(args.config) if args.config else None)
    report_path = write_report(run, args.output_dir)
    print(f"report: {report_path}")
    print(f"optimizer success: {run.fit.success} ({run.fit.message})")
    print(f"identified: {run.fit.params}")
    print(f"validation nominal: {run.nominal_validation_metrics}")
    print(f"validation identified: {run.identified_validation_metrics}")
    return 0 if run.fit.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
