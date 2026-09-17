"""Deterministic L1 servo-driven loaded pendulum identification lesson.

The model boundary is ``q_des -> fixed PD -> delayed torque -> rigid pendulum``.
Observations expose only ``t, q_des, q, qd``; torque and command histories are
retained on completed runs solely as Oracle diagnostics and replay data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

DEFAULT_CONFIG_PATH = Path(__file__).with_name("l1_config.json")


@dataclass(frozen=True)
class Params:
    delay_s: float


@dataclass(frozen=True)
class PublicModel:
    dt: float
    duration_s: float
    q0: float
    qd0: float
    arm_mass: float
    payload_mass: float
    arm_length: float
    gravity: float
    kp: float
    kd: float
    integration_substeps: int = 1

    @property
    def mass(self) -> float:
        """Compatibility alias for total point-plus-arm mass."""
        return self.arm_mass + self.payload_mass

    @property
    def inertia(self) -> float:
        return (
            self.arm_mass * self.arm_length**2 / 3.0
            + self.payload_mass * self.arm_length**2
        )

    @property
    def gravity_moment(self) -> float:
        return self.gravity * (
            self.arm_mass * self.arm_length / 2.0 + self.payload_mass * self.arm_length
        )


@dataclass(frozen=True)
class Config:
    version: str
    model: PublicModel
    truth: Params
    initial: Params
    optimizer_start: Params
    lower: Params
    upper: Params
    fit_amp: float
    fit_f0: float
    fit_f1: float
    validation_amp: float
    seed: int = 7
    timestamp_utc: str = "2026-01-01T00:00:00Z"
    validation_frequency_hz: float = 0.63
    validation_modulation_cycles: float = 0.11
    validation_modulation_hz: float = 0.17
    validation_phase_rad: float = 0.4
    validation_edge_gain: float = 3.0

    # Compatibility conveniences used by the first app/report implementation.
    @property
    def dt(self):
        return self.model.dt

    @property
    def duration_s(self):
        return self.model.duration_s

    @property
    def q0(self):
        return self.model.q0

    @property
    def qd0(self):
        return self.model.qd0

    @property
    def arm_mass(self):
        return self.model.arm_mass

    @property
    def payload_mass(self):
        return self.model.payload_mass

    @property
    def mass(self):
        return self.model.mass

    @property
    def arm_length(self):
        return self.model.arm_length

    @property
    def gravity(self):
        return self.model.gravity

    @property
    def kp(self):
        return self.model.kp

    @property
    def kd(self):
        return self.model.kd


@dataclass(frozen=True)
class Observations:
    t: np.ndarray
    q_des: np.ndarray
    q: np.ndarray
    qd: np.ndarray


@dataclass(frozen=True)
class Trajectory:
    t: np.ndarray
    q_des: np.ndarray
    q: np.ndarray
    qd: np.ndarray
    qd_raw: np.ndarray
    command_torque: np.ndarray
    torque: np.ndarray
    role: str


@dataclass(frozen=True)
class BenchmarkData:
    fit: Observations
    validation: Observations
    oracle_torque_fit: np.ndarray
    oracle_torque_validation: np.ndarray
    metadata: dict[str, Any]
    oracle_trajectories: Mapping[str, Trajectory] | None = None


@dataclass(frozen=True)
class Metrics:
    q_mae: float
    qd_mae: float
    q_rmse: float
    qd_rmse: float


@dataclass(frozen=True)
class FitResult:
    params: Params
    success: bool
    message: str
    cost: float
    nfev: int = 0


@dataclass(frozen=True)
class Run:
    config: Config
    data: BenchmarkData
    fit: FitResult
    initial_fit: Metrics
    identified_fit: Metrics
    initial_validation: Metrics
    identified_validation: Metrics
    trajectories: Mapping[str, Mapping[str, Trajectory]]
    local_loss_slice: tuple[dict[str, float], ...]


def load_config(path: str | Path | None = None) -> Config:
    pth = Path(path) if path else DEFAULT_CONFIG_PATH
    raw = json.loads(pth.read_text())
    pl = raw["plant"]
    model = PublicModel(
        dt=float(raw["dt"]),
        duration_s=float(raw["duration_s"]),
        q0=float(raw["initial_state"]["q"]),
        qd0=float(raw["initial_state"]["qd"]),
        arm_mass=float(pl["arm_mass"]),
        payload_mass=float(pl["payload_mass"]),
        arm_length=float(pl["arm_length"]),
        gravity=float(pl["gravity"]),
        kp=float(raw["controller"]["kp"]),
        kd=float(raw["controller"]["kd"]),
        integration_substeps=raw["integration_substeps"],
    )

    def p(x):
        return Params(float(x["delay_s"]))

    meta = raw.get("metadata", {})
    return Config(
        raw["version"],
        model,
        p(raw["truth"]),
        p(raw["initial_model"]),
        p(raw["optimizer_start"]),
        p(raw["bounds"]["lower"]),
        p(raw["bounds"]["upper"]),
        float(raw["fit_excitation"]["amplitude_rad"]),
        float(raw["fit_excitation"]["f0_hz"]),
        float(raw["fit_excitation"]["f1_hz"]),
        float(raw["validation_excitation"]["amplitude_rad"]),
        int(meta.get("seed", 7)),
        str(meta["timestamp_utc"]),
        float(raw["validation_excitation"]["frequency_hz"]),
        float(raw["validation_excitation"]["modulation_cycles"]),
        float(raw["validation_excitation"]["modulation_hz"]),
        float(raw["validation_excitation"]["phase_rad"]),
        float(raw["validation_excitation"]["edge_gain"]),
    )


def make_time(c: Config | PublicModel) -> np.ndarray:
    _validate_model(_model(c))
    n = int(round(c.duration_s / c.dt))
    return np.arange(n + 1, dtype=float) * c.dt


def excitation(
    t: np.ndarray, amp: float, f0: float, f1: float, duration: float
) -> np.ndarray:
    e = np.asarray(t, dtype=float) - float(t[0])
    return amp * np.sin(2 * np.pi * (f0 * e + 0.5 * (f1 - f0) / duration * e * e))


def derive_velocity(q: np.ndarray, dt: float) -> np.ndarray:
    """Finite-difference encoder velocity; initial sample uses forward difference."""
    q = np.asarray(q, dtype=float)
    if (
        q.ndim != 1
        or q.size < 2
        or not np.all(np.isfinite(q))
        or not np.isfinite(dt)
        or dt <= 0
    ):
        raise ValueError("q must be 1-D with >=2 samples and dt>0")
    out = np.empty_like(q)
    out[0] = (q[1] - q[0]) / dt
    out[1:-1] = (q[2:] - q[:-2]) / (2 * dt)
    out[-1] = (q[-1] - q[-2]) / dt
    return out


def _model(x: Config | PublicModel) -> PublicModel:
    return x.model if isinstance(x, Config) else x


def _delayed(history: np.ndarray, i: int, delay_s: float, dt: float) -> float:
    """Interpolate known torque samples; all negative sample indices are zero.

    An integer delay reads only one sample, including zero delay (no future
    uninitialized buffer read). Fractional startup interpolates zero prehistory
    into command[0], matching the same piecewise linear history everywhere.
    """
    z = i - delay_s / dt
    j = int(np.floor(z))
    w = z - j
    left = float(history[j]) if j >= 0 else 0.0
    if w == 0:
        return left
    right = float(history[j + 1]) if j + 1 >= 0 else 0.0
    return (1.0 - w) * left + w * right


def _validate_model(m: PublicModel) -> None:
    if not isinstance(m, PublicModel):
        raise TypeError("model must be PublicModel")
    vals = (
        m.dt,
        m.duration_s,
        m.q0,
        m.qd0,
        m.arm_mass,
        m.payload_mass,
        m.arm_length,
        m.gravity,
        m.kp,
        m.kd,
    )
    if (
        not all(np.isfinite(vals))
        or m.dt <= 0
        or m.duration_s < m.dt
        or m.arm_mass < 0
        or m.payload_mass < 0
        or m.inertia <= 0
        or m.arm_length <= 0
        or m.gravity < 0
        or m.kp < 0
        or m.kd < 0
        or not isinstance(m.integration_substeps, (int, np.integer))
        or isinstance(m.integration_substeps, bool)
        or m.integration_substeps < 1
    ):
        raise ValueError("invalid physical or numerical model parameters")


def _readonly(array: np.ndarray) -> np.ndarray:
    result = np.asarray(array, dtype=float).copy()
    result.setflags(write=False)
    return result


def _acc(m: PublicModel, q: float, torque: float) -> float:
    return (torque - m.gravity_moment * np.sin(q)) / m.inertia


def simulate(
    c: Config | PublicModel,
    q_des: np.ndarray,
    *,
    delay_s: float,
    q0: float | None = None,
    qd0: float | None = None,
    return_torque: bool = False,
    role: str = "simulation",
):
    """Integrate deterministic held-torque RK4 dynamics and return arrays.

    ``return_torque=True`` returns ``(q, qd_raw, delayed_torque)`` for legacy
    callers. Use :func:`simulate_trajectory` to retain all command signals.
    """
    tr = simulate_trajectory(c, q_des, delay_s=delay_s, q0=q0, qd0=qd0, role=role)
    return (tr.q, tr.qd_raw, tr.torque) if return_torque else (tr.q, tr.qd_raw)


def simulate_trajectory(
    c: Config | PublicModel,
    q_des: np.ndarray,
    *,
    delay_s: float,
    q0: float | None = None,
    qd0: float | None = None,
    role: str = "simulation",
) -> Trajectory:
    m = _model(c)
    q_des = np.asarray(q_des, dtype=float)
    _validate_model(m)
    if q_des.ndim != 1 or q_des.size < 2 or not np.all(np.isfinite(q_des)):
        raise ValueError("q_des must be a finite 1-D array with >=2 samples")
    if not np.isfinite(delay_s) or delay_s < 0:
        raise ValueError("delay_s must be finite and non-negative")
    if not all(
        np.isfinite(v)
        for v in (m.q0 if q0 is None else q0, m.qd0 if qd0 is None else qd0)
    ):
        raise ValueError("reset state must be finite")
    nsub = max(1, int(m.integration_substeps))
    dt = m.dt / nsub
    n = q_des.size
    q = np.empty(n)
    qd = np.empty(n)
    cmd = np.empty(n)
    torque = np.empty(n)
    q[0] = m.q0 if q0 is None else float(q0)
    qd[0] = m.qd0 if qd0 is None else float(qd0)
    for i in range(n):
        cmd[i] = m.kp * (q_des[i] - q[i]) - m.kd * qd[i]
        torque[i] = _delayed(cmd, i, delay_s, m.dt)
        if i == n - 1:
            break

        # Hold the delayed torque over the complete sample interval, with RK4 substeps.
        def f(xq, xv):
            return xv, _acc(m, xq, torque[i])

        xq, xv = q[i], qd[i]
        for _ in range(nsub):
            h = dt
            k1q, k1v = f(xq, xv)
            k2q, k2v = f(xq + 0.5 * h * k1q, xv + 0.5 * h * k1v)
            k3q, k3v = f(xq + 0.5 * h * k2q, xv + 0.5 * h * k2v)
            k4q, k4v = f(xq + h * k3q, xv + h * k3v)
            xq += h * (k1q + 2 * k2q + 2 * k3q + k4q) / 6
            xv += h * (k1v + 2 * k2v + 2 * k3v + k4v) / 6
        q[i + 1], qd[i + 1] = xq, xv
    qd_obs = derive_velocity(q, m.dt)
    return Trajectory(
        *(
            _readonly(a)
            for a in (np.arange(n) * m.dt, q_des, q, qd_obs, qd, cmd, torque)
        ),
        role,
    )


def _validation_excitation(t: np.ndarray, c: Config) -> np.ndarray:
    phase = (
        2
        * np.pi
        * (
            c.validation_frequency_hz * t
            + c.validation_modulation_cycles
            * np.sin(2 * np.pi * c.validation_modulation_hz * t)
        )
        + c.validation_phase_rad
    )
    return c.validation_amp * np.clip(c.validation_edge_gain * np.sin(phase), -1, 1)


def build_benchmark(c: Config) -> BenchmarkData:
    t = make_time(c)
    fd = excitation(t, c.fit_amp, c.fit_f0, c.fit_f1, c.duration_s)
    vd = _validation_excitation(t, c)
    ft = simulate_trajectory(c.model, fd, delay_s=c.truth.delay_s, role="oracle")
    vt = simulate_trajectory(c.model, vd, delay_s=c.truth.delay_s, role="oracle")
    metadata = {
        "config_version": c.version,
        "config_hash": hashlib.sha256(
            json.dumps(asdict(c), sort_keys=True, default=str).encode()
        ).hexdigest()[:16],
        "seed": c.seed,
        "timestamp_utc": c.timestamp_utc,
        "units": {"t": "s", "q": "rad", "qd": "rad/s", "torque": "N m"},
        "observations": ["t", "q_des", "q", "qd"],
        "public_observations": ["t", "q_des", "q", "qd"],
        "oracle_only": [
            "true_torque",
            "delayed_command_state",
            "raw_integration_velocity",
        ],
        "delay_semantics": "effective command delay after fixed PD law; fractional linear interpolation; zero prehistory",
        "sensor_velocity": "qd from q: forward difference at initial sample, centered interior, backward final sample",
        "fit_excitation": {
            "kind": "linear chirp",
            "amplitude_rad": c.fit_amp,
            "f0_hz": c.fit_f0,
            "f1_hz": c.fit_f1,
            "phase_rad": 0.0,
            "duration_s": c.duration_s,
        },
        "validation_excitation": {
            "kind": "phase-modulated clipped-sine reversal",
            "amplitude_rad": c.validation_amp,
            "frequency_hz": c.validation_frequency_hz,
            "modulation_cycles": c.validation_modulation_cycles,
            "modulation_hz": c.validation_modulation_hz,
            "phase_rad": c.validation_phase_rad,
            "edge_gain": c.validation_edge_gain,
        },
        "controller": {
            "kp": c.kp,
            "kd": c.kd,
            "sample_period_s": c.dt,
            "velocity_feedback": "fixed internal integration velocity",
            "filtering": "none",
            "rate_limits": "none",
        },
        "model": asdict(c.model),
        "reset_state": {"q": c.q0, "qd": c.qd0},
        "numerical": {
            "dt": c.dt,
            "integrator": "RK4 held torque",
            "substeps": c.model.integration_substeps,
        },
    }
    return BenchmarkData(
        Observations(ft.t, ft.q_des, ft.q, ft.qd),
        Observations(vt.t, vt.q_des, vt.q, vt.qd),
        ft.torque,
        vt.torque,
        metadata,
        {"fit": ft, "validation": vt},
    )


def fit_student(
    observations: Observations,
    model: PublicModel,
    *,
    optimizer_start: Params | None = None,
    lower: Params = Params(0.0),
    upper: Params = Params(0.2),
) -> FitResult:
    """Fit delay from public observations and a frozen public model only."""
    if not isinstance(observations, Observations):
        raise TypeError("observations required")
    if not isinstance(model, PublicModel):
        raise TypeError("model must be PublicModel")
    _validate_model(model)
    arrays = [
        np.asarray(getattr(observations, key), dtype=float)
        for key in ("t", "q_des", "q", "qd")
    ]
    if any(a.ndim != 1 or a.size < 2 or not np.all(np.isfinite(a)) for a in arrays):
        raise ValueError("observations must be finite 1-D arrays with >=2 samples")
    if any(a.shape != arrays[0].shape for a in arrays):
        raise ValueError("observation arrays must have equal shape")
    if not np.allclose(
        arrays[0], np.arange(arrays[0].size) * model.dt, rtol=0, atol=1e-10
    ):
        raise ValueError(
            "observation t must start at zero with uniform model.dt sampling"
        )
    start = optimizer_start or Params((lower.delay_s + upper.delay_s) / 2)
    if (
        not all(np.isfinite((lower.delay_s, upper.delay_s, start.delay_s)))
        or not (lower.delay_s <= start.delay_s <= upper.delay_s)
        or lower.delay_s < 0
        or upper.delay_s <= lower.delay_s
    ):
        raise ValueError("invalid optimizer bounds/start")

    def residual(x):
        tr = simulate_trajectory(
            model, observations.q_des, delay_s=float(x[0]), q0=model.q0, qd0=model.qd0
        )
        return np.r_[tr.q - observations.q, tr.qd - observations.qd]

    result = least_squares(
        residual,
        [start.delay_s],
        bounds=([lower.delay_s], [upper.delay_s]),
        max_nfev=100,
        ftol=1e-12,
        xtol=1e-12,
        gtol=1e-12,
    )
    if float(result.cost) > 1e-8:
        starts = np.linspace(lower.delay_s, upper.delay_s, 7)
        results = [
            least_squares(
                residual,
                [float(s)],
                bounds=([lower.delay_s], [upper.delay_s]),
                max_nfev=100,
                ftol=1e-12,
                xtol=1e-12,
                gtol=1e-12,
            )
            for s in starts
        ]
        result = min([result, *results], key=lambda r: float(r.cost))
    return FitResult(
        Params(float(result.x[0])),
        bool(result.success),
        str(result.message),
        float(result.cost),
        int(result.nfev),
    )


def score(
    observations: Observations,
    model_or_config: Config | PublicModel,
    delay_s: float,
    *,
    trajectory: Trajectory | None = None,
) -> Metrics:
    tr = trajectory or simulate_trajectory(
        model_or_config,
        observations.q_des,
        delay_s=delay_s,
        q0=(_model(model_or_config)).q0,
        qd0=(_model(model_or_config)).qd0,
        role="score",
    )
    dq, dv = tr.q - observations.q, tr.qd - observations.qd
    return Metrics(
        float(np.mean(abs(dq))),
        float(np.mean(abs(dv))),
        float(np.sqrt(np.mean(dq * dq))),
        float(np.sqrt(np.mean(dv * dv))),
    )


def run_l1(c: Config | None = None) -> Run:
    c = c or load_config()
    data = build_benchmark(c)
    fit = fit_student(
        data.fit,
        c.model,
        optimizer_start=c.optimizer_start,
        lower=c.lower,
        upper=c.upper,
    )
    trajectories: dict[str, dict[str, Trajectory]] = {}
    for split, obs in (("fit", data.fit), ("validation", data.validation)):
        trajectories[split] = {
            "oracle": data.oracle_trajectories[split],
            "initial": simulate_trajectory(
                c.model,
                obs.q_des,
                delay_s=c.initial.delay_s,
                q0=c.model.q0,
                qd0=c.model.qd0,
                role="initial",
            ),
            "identified": simulate_trajectory(
                c.model,
                obs.q_des,
                delay_s=fit.params.delay_s,
                q0=c.model.q0,
                qd0=c.model.qd0,
                role="identified",
            ),
        }
    loss_slice = tuple(
        {"delay_s": float(d), "fit_q_rmse": score(data.fit, c.model, float(d)).q_rmse}
        for d in np.linspace(
            max(c.lower.delay_s, fit.params.delay_s - 0.02),
            min(c.upper.delay_s, fit.params.delay_s + 0.02),
            9,
        )
    )
    return Run(
        c,
        data,
        fit,
        score(
            data.fit,
            c.model,
            c.initial.delay_s,
            trajectory=trajectories["fit"]["initial"],
        ),
        score(
            data.fit,
            c.model,
            fit.params.delay_s,
            trajectory=trajectories["fit"]["identified"],
        ),
        score(
            data.validation,
            c.model,
            c.initial.delay_s,
            trajectory=trajectories["validation"]["initial"],
        ),
        score(
            data.validation,
            c.model,
            fit.params.delay_s,
            trajectory=trajectories["validation"]["identified"],
        ),
        trajectories,
        loss_slice,
    )


def run_summary(r: Run) -> dict[str, Any]:
    return {
        "config_version": r.config.version,
        "metadata": r.data.metadata,
        "truth": asdict(r.config.truth),
        "initial": asdict(r.config.initial),
        "identified": asdict(r.fit.params),
        "fit_result": asdict(r.fit),
        "fit": {
            "initial": asdict(r.initial_fit),
            "identified": asdict(r.identified_fit),
        },
        "validation": {
            "initial": asdict(r.initial_validation),
            "identified": asdict(r.identified_validation),
        },
        "effective_delay_note": "identified delay is boundary and sampling dependent",
        "local_loss_slice": list(r.local_loss_slice),
        "acceptance": {
            "delay_tolerance_s": 0.001,
            "minimum_validation_rmse_improvement": 0.90,
            "delay_error_s": abs(r.fit.params.delay_s - r.config.truth.delay_s),
            "validation_q_improvement": 1
            - r.identified_validation.q_rmse / r.initial_validation.q_rmse
            if r.initial_validation.q_rmse
            else None,
            "validation_qd_improvement": 1
            - r.identified_validation.qd_rmse / r.initial_validation.qd_rmse
            if r.initial_validation.qd_rmse
            else None,
        },
    }


def machine_frame(
    r: Run, split: str = "validation", index: int = 0, role: str = "oracle"
) -> dict[str, Any]:
    tr = r.trajectories[split][role]
    i = int(np.clip(index, 0, tr.q.size - 1))
    q, qd, L = float(tr.q[i]), float(tr.qd[i]), r.config.arm_length
    return {
        "index": i,
        "t": float(tr.t[i]),
        "q": q,
        "qd": qd,
        "tip": (L * np.sin(q), -L * np.cos(q)),
        "tip_velocity": (L * np.cos(q) * qd, L * np.sin(q) * qd),
        "role": role,
        "split": split,
    }


def machine_svg(r: Run, split: str = "validation", index: int = 0) -> str:
    """Draw all recorded roles; convert physical +y-up coordinates to SVG +y-down."""
    cx, cy, scale = 250, 95, 150 / r.config.arm_length
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 330" role="img">',
        f"<title>{split} loaded pendulum at t={machine_frame(r, split, index)['t']:.3f} s</title>",
        '<defs><marker id="gravity-tip" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="#32664a"/></marker></defs>',
        '<rect x="202" y="36" width="96" height="26" fill="#ced8cf"/>',
        '<text x="310" y="54" font-size="13">Fixed base</text>',
        '<rect x="225" y="63" width="50" height="40" rx="4" fill="#edf3ee" stroke="#263b30"/>',
        '<text x="310" y="81" font-size="13">Servo body / axis</text>',
        '<path d="M250 95 V252" stroke="#929d95" stroke-dasharray="3 3"/>',
        '<text x="204" y="180" font-size="13">q from</text><text x="204" y="197" font-size="13">vertical</text>',
        '<path d="M440 117 V195" stroke="#32664a" stroke-width="3" marker-end="url(#gravity-tip)"/>',
        '<text x="453" y="155" font-size="13">Gravity</text>',
    ]
    for row, (role, color, width) in enumerate(
        (
            ("oracle", "#17211b", 8),
            ("initial", "#bb6b0d", 5),
            ("identified", "#1677a3", 3),
        )
    ):
        f = machine_frame(r, split, index, role)
        x, y = cx + scale * f["tip"][0], cy - scale * f["tip"][1]
        dash = ' stroke-dasharray="6 4"' if role == "identified" else ""
        parts.append(
            f'<line data-role="{role}" data-q="{f["q"]:.17g}" data-qd="{f["qd"]:.17g}" x1="{cx}" y1="{cy}" x2="{x:.6f}" y2="{y:.6f}" stroke="{color}" stroke-width="{width}"{dash}/>'
        )
        parts.append(
            f'<circle cx="{x:.6f}" cy="{y:.6f}" r="{10 - row * 2}" fill="white" stroke="{color}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="12" y="{284 + row * 18}" fill="{color}" font-size="13">{role.title()}: q={f["q"]:.4f} rad · qd={f["qd"]:.4f} rad/s</text>'
        )
        if role == "identified":
            for frac in (0.33, 0.66):
                parts.append(
                    f'<circle cx="{cx + (x - cx) * frac:.6f}" cy="{cy + (y - cy) * frac:.6f}" r="3" fill="white" stroke="{color}"/>'
                )
    parts.extend(
        [
            '<circle cx="250" cy="95" r="6" fill="#263b30"/>',
            '<text x="310" y="164" font-size="13">Rigid arm</text>',
            '<text x="310" y="245" font-size="13">Point payload</text>',
            "</svg>",
        ]
    )
    return "".join(parts)


def plot_run(r: Run, path: str | Path) -> Path:
    """Render all report views from recorded arrays, each on its own axes."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(6, 2, figsize=(14, 22), layout="constrained")
    colors = {"oracle": "#17211b", "initial": "#bb6b0d", "identified": "#1677a3"}
    for col, split in enumerate(("fit", "validation")):
        obs = getattr(r.data, split)
        ax[0, col].plot(
            obs.t, obs.q_des, color="#788879", linestyle=":", label="Target q_des"
        )
        for role in ("oracle", "initial", "identified"):
            tr = r.trajectories[split][role]
            style = dict(
                color=colors[role],
                linestyle="--" if role == "identified" else "-",
                marker="o" if role == "identified" else None,
                markerfacecolor="white",
                markersize=3,
                markevery=max(1, len(obs.t) // 18),
                linewidth=1.6,
            )
            ax[0, col].plot(obs.t, tr.q, label=role.title(), **style)
            ax[1, col].plot(obs.t, tr.qd, label=role.title(), **style)
            ax[2, col].plot(
                obs.t, tr.torque, label=f"{role.title()} applied torque", **style
            )
            if role != "oracle":
                ax[3, col].plot(
                    obs.t, tr.q - obs.q, label=f"{role.title()} residual", **style
                )
                ax[4, col].plot(
                    obs.qd, tr.q - obs.q, label=f"{role.title()} residual", **style
                )
        ax[2, col].plot(
            obs.t,
            r.trajectories[split]["oracle"].command_torque,
            ":",
            color=colors["oracle"],
            label="Oracle pre-delay command",
        )
        for row, title, ylabel in (
            (0, "angle", "q (rad)"),
            (1, "encoder velocity", "qd (rad/s)"),
            (2, "torque diagnostics: evaluation only", "N m"),
            (3, "residual vs time", "q prediction − Oracle (rad)"),
            (4, "residual vs Oracle velocity", "q prediction − Oracle (rad)"),
        ):
            ax[row, col].set(
                title=f"{split.title()}: {title}",
                xlabel="Oracle qd (rad/s)" if row == 4 else "time (s)",
                ylabel=ylabel,
            )
            ax[row, col].legend(fontsize=8)
            ax[row, col].grid(alpha=0.2)
    a = ax[5, 0]
    a.add_patch(plt.Rectangle((-0.13, 0.04), 0.26, 0.07, color="#ced8cf"))
    a.add_patch(plt.Rectangle((-0.07, -0.035), 0.14, 0.075, color="#53635a"))
    for role in ("oracle", "initial", "identified"):
        f = machine_frame(r, "validation", len(r.data.validation.t) // 2, role)
        x, y = f["tip"]
        a.plot(
            [0, x],
            [0, y],
            color=colors[role],
            linestyle="--" if role == "identified" else "-",
            linewidth=2 if role == "identified" else 5,
            label=role.title(),
        )
        a.scatter([x], [y], s=80, facecolors="white", edgecolors=colors[role], zorder=4)
    a.scatter([0], [0], s=45, color=colors["oracle"], zorder=5)
    a.annotate(
        "gravity", xy=(0.3, -0.35), xytext=(0.3, -0.1), arrowprops=dict(arrowstyle="->")
    )
    a.text(-0.42, 0.09, "Fixed base")
    a.text(0.11, 0.01, "Servo / axis")
    a.text(0.1, -0.26, "Rigid arm")
    a.text(0.1, -0.59, "Point payload")
    a.set(
        xlim=(-0.45, 0.65),
        ylim=(-0.72, 0.16),
        title="Recorded machine at validation t=4 s",
        xlabel="x (m)",
        ylabel="y (m)",
    )
    a.set_aspect("equal")
    a.legend(fontsize=8, loc="lower left")
    loss = r.local_loss_slice
    ax[5, 1].plot(
        [v["delay_s"] for v in loss],
        [v["fit_q_rmse"] for v in loss],
        "o-",
        color=colors["identified"],
    )
    ax[5, 1].axvline(
        r.fit.params.delay_s,
        linestyle="--",
        color=colors["oracle"],
        label="Fitted delay",
    )
    ax[5, 1].set(
        title="Fit-only local loss slice (held-out data unused)",
        xlabel="candidate effective delay (s)",
        ylabel="fit q RMSE (rad)",
    )
    ax[5, 1].grid(alpha=0.2)
    ax[5, 1].legend(fontsize=8)
    fig.savefig(p, dpi=140)
    plt.close(fig)
    return p


def write_report(r: Run, out: str | Path) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    plot_run(r, out / "report.png")
    summary = run_summary(r)
    (out / "metrics.json").write_text(json.dumps(summary, indent=2) + "\n")
    m = r.config.model
    table = "\n".join(
        f"| {split} | {before.q_rmse:.6g} | {after.q_rmse:.6g} | {before.qd_rmse:.6g} | {after.qd_rmse:.6g} |"
        for split, before, after in (
            ("Fit chirp", r.initial_fit, r.identified_fit),
            ("Held-out reversals", r.initial_validation, r.identified_validation),
        )
    )
    text = f"""# L1: Servo-driven loaded pendulum

This fixed run comes from `{r.config.version}`. For the guided explanation and exercise,
start with the [L1 lesson](../../docs/lessons/l1/README.md).

## The machine and its boundary

A fixed base holds one rotary servo, a uniform rigid arm ({m.arm_mass:g} kg,
{m.arm_length:g} m), and a known point payload ({m.payload_mass:g} kg). Gravity is
{m.gravity:g} m/s². Angle zero points down; positive angle moves the payload right.
The known inertia is {m.inertia:g} kg m², including both arm and payload.

`q_des + joint state -> fixed PD controller -> command delay -> torque -> pendulum`

The fixed controller computes `kp * (q_des - q) - kd * internal velocity` with
kp={m.kp:g} N m/rad and kd={m.kd:g} N m s/rad. Delay shifts the **entire torque
command history after PD**, including feedback. Fractional delays use linear
interpolation of sampled torque history; pre-reset commands are zero. Torque is
held over each {m.dt:g} s interval while RK4 integrates gravity dynamics.
Filtering and rate limits are fixed to none.

The estimator receives only `t`, `q_des`, ideal encoder `q`, and `qd` derived by
centered position differences (one-sided at the endpoints). Internal velocity,
Oracle torque, and the delayed command buffer are privileged diagnostics.
Namespace lists, full excitation parameters, units, seed, synthetic timestamp
epoch, reset state and configuration hash are recorded in [metrics.json](metrics.json).
The timestamp is a frozen synthetic epoch, not a claimed data-collection date.

## How to read the evidence

![Machine, fit and validation, residuals and local loss slice](report.png)

Fit chirp and held-out reversals have different frequency/phase composition and
both reset to q={m.q0:g} rad, internal velocity={m.qd0:g} rad/s. Only the chirp
enters optimization. Validation is evaluated once the fitted delay is selected.
The separate machine panel shows a recorded validation frame, using the same
angle array as the plots. The interactive timeline replays those arrays.

Curve key: **Oracle solid black; Initial orange; Identified blue dashed with
hollow markers; target dotted green-gray**. Overlapping Oracle and Identified
curves are expected in this matched benchmark. The torque row labels the
pre-delay Oracle command and applied torques as evaluation-only diagnostics.

Residual means `model - Oracle`. The Initial model leaves repeating signed
lobes near reversal transitions; the residual-versus-velocity view exposes
structured timing error. A small time shift often gives an error proportional
to velocity, so correlation alone does not prove friction. The Identified
residual collapses here because the one-delay model matches the generator.

The fit-only local loss slice tests nine nearby delays with known mechanics held
fixed. Its minimum provides local delay sensitivity evidence, not a confidence
interval or proof of identifiability for arbitrary commands. Slow excitation can
make the minimum shallow. Bounded least squares starts at the independent
optimizer guess; if its unscaled combined q/qd cost exceeds 1e-8, seven evenly
spaced public starts are tried and the lowest fit loss wins. No validation score
or Oracle parameter chooses a start.

## Parameters and held-out prediction

| Role | Effective delay | Mechanical parameters |
|---|---:|---|
| Oracle (evaluation only) | {r.config.truth.delay_s:.5f} s | fixed known arm and payload |
| Initial model | {r.config.initial.delay_s:.5f} s | same known values |
| Identified Student | {r.fit.params.delay_s:.5f} s | same known values |

Public bounds: [{r.config.lower.delay_s:g}, {r.config.upper.delay_s:g}] s.
Optimizer start: {r.config.optimizer_start.delay_s:g} s, independent of the Initial model.
Fit success: {r.fit.success}; solver message: `{r.fit.message}`.

| Split | Initial q RMSE (rad) | Identified q RMSE | Initial qd RMSE (rad/s) | Identified qd RMSE |
|---|---:|---:|---:|---:|
{table}

Default acceptance thresholds: delay recovery error ≤ 1 ms and held-out q **and**
qd RMSE reduction ≥ 90%. This run's delay error is
{summary["acceptance"]["delay_error_s"]:.6g} s. Detailed improvements are in
`metrics.json`. These are matched synthetic benchmark thresholds, not hardware
accuracy guarantees. The fitted delay is **effective, boundary-dependent and
sampling-dependent**, not a physical motor constant.

## Reproduce and understand the limits

From the repository root:

```bash
python -m synthetic.l1_servo_loaded_pendulum --output-dir reports/l1_servo_loaded_pendulum
```

The same configuration regenerates this report and metrics. Same-environment
artifacts are deterministic; across CPU/library versions use 1e-8 absolute
numerical tolerance for delays and metrics, and compare plot content rather than
PNG bytes. Notebook and guided app use the same numerical module.

This synthetic, ideal observation lesson is not a motor-electromagnetic or
whole-robot simulation and does not establish hardware transfer. Omitted effects
include torque scale/bias, friction, saturation, compliance/backlash, sensor noise,
voltage/temperature, contact, payload shifts and reflected motor inertia. Add
friction or saturation only with concrete residual evidence; then move to a
fixed-base leg for coupled dynamics.
"""
    (out / "report.md").write_text(text)
    return out / "report.md"


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--output-dir", default="reports/l1_servo_loaded_pendulum")
    write_report(run_l1(), a.parse_args(argv).output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
