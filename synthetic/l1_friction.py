"""L1 friction-versus-viscous-damping identification benchmark.

The experiment is deliberately smaller than the loaded-pendulum lesson.  A
known-inertia rotary load receives a known applied torque and obeys

    J*qdd + b*qd + tau_c*tanh(qd/v_eps) = u.

The Oracle uses both resistance terms.  A viscous-only Student fits ``b``
with ``tau_c`` fixed at zero; the friction Student fits both terms.  The
fitter receives only public observations and a public model, never the Oracle
configuration or the validation split.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

DEFAULT_CONFIG_PATH = Path(__file__).with_name("l1_friction_config.json")
Structure = Literal["viscous", "friction"]


@dataclass(frozen=True)
class Params:
    damping: float
    coulomb: float = 0.0


@dataclass(frozen=True)
class PublicModel:
    dt: float
    duration_s: float
    inertia: float
    v_eps: float
    q0: float = 0.0
    qd0: float = 0.0


@dataclass(frozen=True)
class Config:
    version: str
    model: PublicModel
    truth: Params
    viscous_initial: Params
    friction_initial: Params
    lower: Params
    upper: Params
    fit_amplitude: float
    fit_frequency_hz: float
    fit_harmonic: float
    fit_harmonic_phase_rad: float
    validation_amplitude: float
    validation_frequency_hz: float
    validation_harmonic: float
    validation_harmonic_phase_rad: float
    validation_error_ratio_max: float = 0.25
    reversal_ratio_max: float = 0.4
    parameter_abs_tolerance: float = 0.002
    seed: int = 7
    timestamp_utc: str = "2026-01-01T00:00:00Z"


@dataclass(frozen=True)
class Observations:
    t: np.ndarray
    u: np.ndarray
    q: np.ndarray
    qd: np.ndarray


@dataclass(frozen=True)
class Trajectory:
    t: np.ndarray
    u: np.ndarray
    q: np.ndarray
    qd: np.ndarray
    role: str


@dataclass(frozen=True)
class BenchmarkData:
    fit: Observations
    validation: Observations
    metadata: dict[str, Any]
    oracle_trajectories: dict[str, Trajectory]


@dataclass(frozen=True)
class Metrics:
    q_rmse: float
    qd_rmse: float
    q_mae: float
    qd_mae: float


@dataclass(frozen=True)
class FitResult:
    structure: Structure
    params: Params
    success: bool
    message: str
    cost: float
    nfev: int


@dataclass(frozen=True)
class Run:
    config: Config
    data: BenchmarkData
    viscous_fit: FitResult
    friction_fit: FitResult
    metrics: dict[str, dict[str, Metrics]]
    trajectories: dict[str, dict[str, Trajectory]]
    reversal_metrics: dict[str, dict[str, float]]
    sensitivity: dict[str, float]


def _params(raw: dict[str, Any]) -> Params:
    return Params(float(raw["damping"]), float(raw.get("coulomb", 0.0)))


def load_config(path: str | Path | None = None) -> Config:
    config_path = Path(path) if path else DEFAULT_CONFIG_PATH
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    model_raw = raw["model"]
    model = PublicModel(
        dt=float(raw["dt"]),
        duration_s=float(raw["duration_s"]),
        inertia=float(model_raw["inertia"]),
        v_eps=float(model_raw["v_eps"]),
        q0=float(raw["initial_state"]["q"]),
        qd0=float(raw["initial_state"]["qd"]),
    )
    metadata = raw.get("metadata", {})
    fit = raw["fit_excitation"]
    validation = raw["validation_excitation"]
    return Config(
        version=str(raw["version"]),
        model=model,
        truth=_params(raw["truth"]),
        viscous_initial=_params(raw["viscous_initial"]),
        friction_initial=_params(raw["friction_initial"]),
        lower=_params(raw["bounds"]["lower"]),
        upper=_params(raw["bounds"]["upper"]),
        fit_amplitude=float(fit["amplitude_nm"]),
        fit_frequency_hz=float(fit["frequency_hz"]),
        fit_harmonic=float(fit["harmonic"]),
        fit_harmonic_phase_rad=float(fit["harmonic_phase_rad"]),
        validation_amplitude=float(validation["amplitude_nm"]),
        validation_frequency_hz=float(validation["frequency_hz"]),
        validation_harmonic=float(validation["harmonic"]),
        validation_harmonic_phase_rad=float(validation["harmonic_phase_rad"]),
        validation_error_ratio_max=float(raw.get("acceptance", {}).get("validation_error_ratio_max", 0.25)),
        reversal_ratio_max=float(raw.get("acceptance", {}).get("reversal_ratio_max", 0.4)),
        parameter_abs_tolerance=float(raw.get("acceptance", {}).get("parameter_abs_tolerance", 0.002)),
        seed=int(metadata.get("seed", 7)),
        timestamp_utc=str(metadata.get("timestamp_utc", "2026-01-01T00:00:00Z")),
    )


def _validate_model(model: PublicModel) -> None:
    values = (model.dt, model.duration_s, model.inertia, model.v_eps, model.q0, model.qd0)
    if not all(np.isfinite(values)) or model.dt <= 0 or model.duration_s <= model.dt:
        raise ValueError("invalid model timing or state")
    if model.inertia <= 0 or model.v_eps <= 0:
        raise ValueError("inertia and v_eps must be positive")


def _validate_params(params: Params) -> None:
    if not all(np.isfinite((params.damping, params.coulomb))):
        raise ValueError("parameters must be finite")
    if params.damping < 0 or params.coulomb < 0:
        raise ValueError("damping and coulomb terms must be non-negative")


def make_time(model: PublicModel) -> np.ndarray:
    _validate_model(model)
    count = int(round(model.duration_s / model.dt))
    return np.arange(count + 1, dtype=float) * model.dt


def excitation(
    t: np.ndarray,
    *,
    amplitude: float,
    frequency_hz: float,
    harmonic: float,
    harmonic_phase_rad: float,
) -> np.ndarray:
    t = np.asarray(t, dtype=float)
    if t.ndim != 1 or not np.all(np.isfinite(t)):
        raise ValueError("t must be a finite one-dimensional array")
    if amplitude < 0 or frequency_hz <= 0 or harmonic < 0:
        raise ValueError("invalid excitation parameters")
    elapsed = t - t[0]
    base = 2 * np.pi * frequency_hz * elapsed
    return amplitude * (
        np.sin(base) + harmonic * np.sin(2 * base + harmonic_phase_rad)
    )


def _readonly(values: np.ndarray) -> np.ndarray:
    out = np.asarray(values, dtype=float).copy()
    out.setflags(write=False)
    return out


def _acceleration(model: PublicModel, params: Params, qd: float, torque: float) -> float:
    resistance = params.damping * qd + params.coulomb * np.tanh(qd / model.v_eps)
    return (torque - resistance) / model.inertia


def simulate(
    model: PublicModel,
    t: np.ndarray,
    u: np.ndarray,
    params: Params,
    *,
    role: str = "simulation",
) -> Trajectory:
    _validate_model(model)
    _validate_params(params)
    t = np.asarray(t, dtype=float)
    u = np.asarray(u, dtype=float)
    if t.ndim != 1 or t.size < 2 or u.shape != t.shape:
        raise ValueError("t and u must be one-dimensional arrays with equal length")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(u)):
        raise ValueError("t and u must be finite")
    dt = np.diff(t)
    if np.any(dt <= 0) or not np.allclose(dt, model.dt, rtol=0, atol=1e-12):
        raise ValueError("t must be uniformly sampled at model.dt")
    q = np.empty_like(t)
    qd = np.empty_like(t)
    q[0], qd[0] = model.q0, model.qd0
    for i in range(t.size - 1):
        torque = float(u[i])

        def f(xv: float) -> tuple[float, float]:
            return xv, _acceleration(model, params, xv, torque)

        xq, xv = q[i], qd[i]
        k1q, k1v = f(xv)
        k2q, k2v = f(xv + 0.5 * model.dt * k1v)
        k3q, k3v = f(xv + 0.5 * model.dt * k2v)
        k4q, k4v = f(xv + model.dt * k3v)
        q[i + 1] = xq + model.dt * (k1q + 2 * k2q + 2 * k3q + k4q) / 6
        qd[i + 1] = xv + model.dt * (k1v + 2 * k2v + 2 * k3v + k4v) / 6
    return Trajectory(t=_readonly(t), u=_readonly(u), q=_readonly(q), qd=_readonly(qd), role=role)


def build_benchmark(config: Config | None = None) -> BenchmarkData:
    config = config or load_config()
    model = config.model
    t = make_time(model)
    fit_u = excitation(
        t,
        amplitude=config.fit_amplitude,
        frequency_hz=config.fit_frequency_hz,
        harmonic=config.fit_harmonic,
        harmonic_phase_rad=config.fit_harmonic_phase_rad,
    )
    validation_u = excitation(
        t,
        amplitude=config.validation_amplitude,
        frequency_hz=config.validation_frequency_hz,
        harmonic=config.validation_harmonic,
        harmonic_phase_rad=config.validation_harmonic_phase_rad,
    )
    fit_tr = simulate(model, t, fit_u, config.truth, role="oracle")
    validation_tr = simulate(model, t, validation_u, config.truth, role="oracle")
    metadata = {
        "config_version": config.version,
        "config_hash": hashlib.sha256(
            json.dumps(asdict(config), sort_keys=True, default=str).encode()
        ).hexdigest()[:16],
        "seed": config.seed,
        "timestamp_utc": config.timestamp_utc,
        "units": {"t": "s", "u": "N m", "q": "rad", "qd": "rad/s"},
        "observations": ["t", "u", "q", "qd"],
        "public_observations": ["t", "u", "q", "qd"],
        "oracle_only": ["truth parameters", "true resistance decomposition"],
        "model_boundary": "known applied torque -> rotary load; no delay, gravity, or saturation",
        "friction_model": "b*qd + tau_c*tanh(qd/v_eps)",
        "velocity_coverage": {
            "fit_abs_max": float(np.max(np.abs(fit_tr.qd))),
            "validation_abs_max": float(np.max(np.abs(validation_tr.qd))),
            "fit_abs_p95": float(np.percentile(np.abs(fit_tr.qd), 95)),
            "validation_abs_p95": float(np.percentile(np.abs(validation_tr.qd), 95)),
        },
    }

    def observations(tr: Trajectory) -> Observations:
        return Observations(tr.t, tr.u, tr.q, tr.qd)

    return BenchmarkData(
        fit=observations(fit_tr),
        validation=observations(validation_tr),
        metadata=metadata,
        oracle_trajectories={"fit": fit_tr, "validation": validation_tr},
    )


def _validate_observations(observations: Observations, model: PublicModel) -> None:
    arrays = [observations.t, observations.u, observations.q, observations.qd]
    if any(a.ndim != 1 or a.size < 2 or not np.all(np.isfinite(a)) for a in arrays):
        raise ValueError("observations must be finite one-dimensional arrays")
    if any(a.shape != arrays[0].shape for a in arrays):
        raise ValueError("observation arrays must have equal shape")
    if not np.allclose(observations.t, np.arange(observations.t.size) * model.dt, rtol=0, atol=1e-10):
        raise ValueError("observation t must start at zero at model.dt spacing")


def fit_student(
    observations: Observations,
    model: PublicModel,
    *,
    structure: Structure,
    optimizer_start: Params,
    lower: Params,
    upper: Params,
) -> FitResult:
    """Fit a declared Student structure from public observations only."""
    if structure not in ("viscous", "friction"):
        raise ValueError("structure must be 'viscous' or 'friction'")
    _validate_observations(observations, model)
    _validate_params(optimizer_start)
    _validate_params(lower)
    _validate_params(upper)
    if lower.damping > upper.damping or lower.coulomb > upper.coulomb:
        raise ValueError("invalid parameter bounds")
    if structure == "viscous":
        if lower.coulomb != 0 or upper.coulomb != 0:
            raise ValueError("viscous-only structure must fix coulomb at zero")
        start = np.array([optimizer_start.damping], dtype=float)
        lo = np.array([lower.damping], dtype=float)
        hi = np.array([upper.damping], dtype=float)
    else:
        start = np.array([optimizer_start.damping, optimizer_start.coulomb], dtype=float)
        lo = np.array([lower.damping, lower.coulomb], dtype=float)
        hi = np.array([upper.damping, upper.coulomb], dtype=float)
    if np.any(start < lo) or np.any(start > hi) or np.any(hi <= lo):
        raise ValueError("optimizer start must lie inside bounds")

    q_scale = max(float(np.std(observations.q)), 1e-6)
    qd_scale = max(float(np.std(observations.qd)), 1e-6)

    def residual(x: np.ndarray) -> np.ndarray:
        params = Params(float(x[0]), float(x[1]) if structure == "friction" else 0.0)
        tr = simulate(model, observations.t, observations.u, params)
        return np.r_[(tr.q - observations.q) / q_scale, (tr.qd - observations.qd) / qd_scale]

    result = least_squares(
        residual, start, bounds=(lo, hi), max_nfev=250, ftol=1e-12, xtol=1e-12, gtol=1e-12
    )
    params = Params(float(result.x[0]), float(result.x[1]) if structure == "friction" else 0.0)
    return FitResult(structure, params, bool(result.success), str(result.message), float(result.cost), int(result.nfev))


def score(observations: Observations, trajectory: Trajectory) -> Metrics:
    dq = trajectory.q - observations.q
    dv = trajectory.qd - observations.qd
    return Metrics(
        q_rmse=float(np.sqrt(np.mean(dq * dq))),
        qd_rmse=float(np.sqrt(np.mean(dv * dv))),
        q_mae=float(np.mean(np.abs(dq))),
        qd_mae=float(np.mean(np.abs(dv))),
    )


def reversal_indices(qd: np.ndarray) -> np.ndarray:
    qd = np.asarray(qd, dtype=float)
    signs = np.sign(qd)
    changes = np.flatnonzero(signs[1:] * signs[:-1] < 0) + 1
    return changes


def reversal_residual_rmse(observations: Observations, trajectory: Trajectory, *, window: int = 8) -> float:
    indices = reversal_indices(observations.qd)
    if indices.size == 0:
        return float("nan")
    residual = trajectory.q - observations.q
    selected = np.concatenate(
        [np.arange(max(0, i - window), min(residual.size, i + window + 1)) for i in indices]
    )
    return float(np.sqrt(np.mean(residual[np.unique(selected)] ** 2)))


def sensitivity(config: Config, data: BenchmarkData) -> dict[str, float]:
    """Finite-difference local sensitivity of the friction Student on fit data."""
    base = config.truth
    steps = (max(base.damping * 1e-3, 1e-5), max(base.coulomb * 1e-3, 1e-5))
    columns = []
    for index, step in enumerate(steps):
        plus = [base.damping, base.coulomb]
        minus = [base.damping, base.coulomb]
        plus[index] += step
        minus[index] -= step
        columns.append(
            (
                simulate(config.model, data.fit.t, data.fit.u, Params(*plus)).q
                - simulate(config.model, data.fit.t, data.fit.u, Params(*minus)).q
            )
            / (2 * step)
        )
    singular = np.linalg.svd(np.column_stack(columns), compute_uv=False)
    return {"smallest_singular_value": float(singular[-1]), "condition_number": float(singular[0] / singular[-1])}


def run_l1_f(config: Config | None = None) -> Run:
    config = config or load_config()
    data = build_benchmark(config)
    viscous = fit_student(
        data.fit, config.model, structure="viscous", optimizer_start=config.viscous_initial,
        lower=Params(config.lower.damping, 0.0), upper=Params(config.upper.damping, 0.0),
    )
    friction = fit_student(
        data.fit, config.model, structure="friction", optimizer_start=config.friction_initial,
        lower=config.lower, upper=config.upper,
    )
    fitted = {"viscous": viscous, "friction": friction}
    trajectories: dict[str, dict[str, Trajectory]] = {}
    metrics: dict[str, dict[str, Metrics]] = {}
    reversal: dict[str, dict[str, float]] = {}
    for split, obs in (("fit", data.fit), ("validation", data.validation)):
        trajectories[split] = {"oracle": data.oracle_trajectories[split]}
        metrics[split] = {"oracle": Metrics(0.0, 0.0, 0.0, 0.0)}
        reversal[split] = {}
        for name, result in fitted.items():
            tr = simulate(config.model, obs.t, obs.u, result.params, role=name)
            trajectories[split][name] = tr
            metrics[split][name] = score(obs, tr)
            reversal[split][name] = reversal_residual_rmse(obs, tr)
    return Run(config, data, viscous, friction, metrics, trajectories, reversal, sensitivity(config, data))


def run_summary(run: Run) -> dict[str, Any]:
    viscous_validation = run.metrics["validation"]["viscous"]
    friction_validation = run.metrics["validation"]["friction"]
    reversal_ratio = run.reversal_metrics["validation"]["friction"] / max(
        run.reversal_metrics["validation"]["viscous"], 1e-30
    )
    return {
        "config_version": run.config.version,
        "metadata": run.data.metadata,
        "truth": asdict(run.config.truth),
        "viscous_fit": asdict(run.viscous_fit),
        "friction_fit": asdict(run.friction_fit),
        "metrics": {split: {role: asdict(value) for role, value in values.items()} for split, values in run.metrics.items()},
        "reversal_residual_rmse": run.reversal_metrics,
        "sensitivity": run.sensitivity,
        "thresholds": {
            "validation_error_ratio_max": run.config.validation_error_ratio_max,
            "reversal_ratio_max": run.config.reversal_ratio_max,
            "parameter_abs_tolerance": run.config.parameter_abs_tolerance,
        },
        "gates": {
            "validation_q_ratio": friction_validation.q_rmse / max(viscous_validation.q_rmse, 1e-30),
            "validation_qd_ratio": friction_validation.qd_rmse / max(viscous_validation.qd_rmse, 1e-30),
            "reversal_ratio": reversal_ratio,
            "friction_parameters_within_tolerance": (
                abs(run.friction_fit.params.damping - run.config.truth.damping)
                <= run.config.parameter_abs_tolerance
                and abs(run.friction_fit.params.coulomb - run.config.truth.coulomb)
                <= run.config.parameter_abs_tolerance
            ),
        },
        "acceptance": {
            "fit_observations": ["t", "u", "q", "qd"],
            "validation_hidden_from_fitter": True,
            "model_mismatch": "viscous-only omits smooth Coulomb-like resistance",
        },
    }


def plot_run(run: Run, path: str | Path) -> Path:
    """Write the compact static evidence figure for the frozen run."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
    for column, (split, title) in enumerate((("fit", "Fit"), ("validation", "Held-out validation"))):
        obs = getattr(run.data, split)
        ax = axes[0, column]
        ax.plot(obs.t, obs.q, "k", label="Oracle")
        for role, style in (("viscous", "--"), ("friction", "-")):
            ax.plot(obs.t, run.trajectories[split][role].q, style, label=role.title())
        ax.set_title(f"{title}: position")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("q (rad)")
        ax.legend()
        ax = axes[1, column]
        for role, style in (("viscous", "--"), ("friction", "-")):
            ax.plot(obs.t, run.trajectories[split][role].q - obs.q, style, label=role.title())
        ax.axhline(0, color="k", linewidth=0.6)
        ax.set_title(f"{title}: position residual")
        ax.set_xlabel("time (s)")
        ax.set_ylabel("prediction - Oracle (rad)")
        ax.legend()
    oracle = run.data.oracle_trajectories["fit"]
    resistance = run.config.truth.damping * oracle.qd + run.config.truth.coulomb * np.tanh(
        oracle.qd / run.config.model.v_eps
    )
    axes[0, 2].plot(oracle.qd, resistance, "k", label="Oracle resistance")
    axes[0, 2].set_title("Resistance versus velocity")
    axes[0, 2].set_xlabel("qd (rad/s)")
    axes[0, 2].set_ylabel("resistance (N m)")
    axes[0, 2].legend()
    axes[1, 2].bar(
        ["viscous", "friction"],
        [run.reversal_metrics["validation"]["viscous"], run.reversal_metrics["validation"]["friction"]],
    )
    axes[1, 2].set_title("Held-out reversal residual")
    axes[1, 2].set_ylabel("q RMSE (rad)")
    figure.savefig(path, dpi=140)
    plt.close(figure)
    return path


def write_report(run: Run, output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plot_run(run, output / "report.png")
    write_metrics(run, output)
    summary = run_summary(run)
    q_ratio = summary["gates"]["validation_q_ratio"]
    qd_ratio = summary["gates"]["validation_qd_ratio"]
    reversal_ratio = summary["gates"]["reversal_ratio"]
    report = f"""# L1 friction extension: viscous damping versus smooth Coulomb-like resistance

This frozen CPU run compares a viscous-only Student with a Student that can
represent smooth Coulomb-like resistance. The known-inertia plant is
`J*qdd + b*qd + tau_c*tanh(qd/v_eps) = u`; delay, gravity, saturation and
measurement noise are absent by design.

![Fit, validation, resistance and reversal residuals](report.png)

## Boundary and observations

The Oracle uses `b={run.config.truth.damping:g}` and `tau_c={run.config.truth.coulomb:g}` with
fixed `J={run.config.model.inertia:g}` and `v_eps={run.config.model.v_eps:g}`. The estimator sees
only `t`, applied torque `u`, position `q`, and velocity `qd`. Oracle parameters,
the resistance decomposition, and held-out observations stay outside the fit API.

## Results

The viscous-only fit returned `b={run.viscous_fit.params.damping:.6f}`. The friction fit returned
`b={run.friction_fit.params.damping:.6f}`, `tau_c={run.friction_fit.params.coulomb:.6f}`.
Held-out q RMSE ratio (friction / viscous) is `{q_ratio:.4g}` and qd RMSE ratio is
`{qd_ratio:.4g}`. The held-out reversal-window q RMSE ratio is `{reversal_ratio:.4g}`.
The local fit sensitivity condition number is `{run.sensitivity['condition_number']:.4g}`.

## Interpretation and limits

The omitted friction term produces structured residuals around changes of
velocity. A velocity-correlated residual is evidence for a missing effect, not
proof that the effect is friction: delay, filtering, or an incorrect torque
boundary can create similar patterns. This lesson uses smooth `tanh` friction;
it does not establish static sticking, Stribeck behavior, backlash, asymmetric
friction, sensor noise, or hardware transfer.

Thresholds were frozen after the pilot: both validation error ratios must be
at most `{run.config.validation_error_ratio_max:g}`, reversal ratio at most
`{run.config.reversal_ratio_max:g}`, and parameter recovery is reported within
`{run.config.parameter_abs_tolerance:g}` only when sensitivity supports it.
"""
    path = output / "report.md"
    path.write_text(report, encoding="utf-8")
    return path


def write_metrics(run: Run, output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / "metrics.json"
    path.write_text(json.dumps(run_summary(run), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("reports/l1_friction"))
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args()
    run = run_l1_f(load_config(args.config))
    path = write_report(run, args.output_dir)
    print(json.dumps(run_summary(run), indent=2, sort_keys=True))
    print(f"wrote {path}")


if __name__ == "__main__":
    _main()
