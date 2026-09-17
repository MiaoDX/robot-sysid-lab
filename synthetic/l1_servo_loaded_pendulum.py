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
        return self.arm_mass * self.arm_length**2 / 3.0 + self.payload_mass * self.arm_length**2

    @property
    def gravity_moment(self) -> float:
        return self.gravity * (self.arm_mass * self.arm_length / 2.0 + self.payload_mass * self.arm_length)


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
    def dt(self): return self.model.dt
    @property
    def duration_s(self): return self.model.duration_s
    @property
    def q0(self): return self.model.q0
    @property
    def qd0(self): return self.model.qd0
    @property
    def arm_mass(self): return self.model.arm_mass
    @property
    def payload_mass(self): return self.model.payload_mass
    @property
    def mass(self): return self.model.mass
    @property
    def arm_length(self): return self.model.arm_length
    @property
    def gravity(self): return self.model.gravity
    @property
    def kp(self): return self.model.kp
    @property
    def kd(self): return self.model.kd


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
        dt=float(raw["dt"]), duration_s=float(raw["duration_s"]),
        q0=float(raw["initial_state"]["q"]), qd0=float(raw["initial_state"]["qd"]),
        arm_mass=float(pl["arm_mass"]),
        payload_mass=float(pl["payload_mass"]),
        arm_length=float(pl["arm_length"]), gravity=float(pl["gravity"]),
        kp=float(raw["controller"]["kp"]), kd=float(raw["controller"]["kd"]),
        integration_substeps=raw["integration_substeps"],
    )
    p = lambda x: Params(float(x["delay_s"]))
    meta = raw.get("metadata", {})
    return Config(raw["version"], model, p(raw["truth"]), p(raw["initial_model"]),
                  p(raw["optimizer_start"]), p(raw["bounds"]["lower"]),
                  p(raw["bounds"]["upper"]), float(raw["fit_excitation"]["amplitude_rad"]),
                  float(raw["fit_excitation"]["f0_hz"]), float(raw["fit_excitation"]["f1_hz"]),
                  float(raw["validation_excitation"]["amplitude_rad"]), int(meta.get("seed", 7)),
                  str(meta["timestamp_utc"]),
                  float(raw["validation_excitation"]["frequency_hz"]),
                  float(raw["validation_excitation"]["modulation_cycles"]),
                  float(raw["validation_excitation"]["modulation_hz"]),
                  float(raw["validation_excitation"]["phase_rad"]),
                  float(raw["validation_excitation"]["edge_gain"]))


def make_time(c: Config | PublicModel) -> np.ndarray:
    _validate_model(_model(c))
    n = int(round(c.duration_s / c.dt))
    return np.arange(n + 1, dtype=float) * c.dt


def excitation(t: np.ndarray, amp: float, f0: float, f1: float, duration: float) -> np.ndarray:
    e = np.asarray(t, dtype=float) - float(t[0])
    return amp * np.sin(2 * np.pi * (f0 * e + 0.5 * (f1 - f0) / duration * e * e))


def derive_velocity(q: np.ndarray, dt: float) -> np.ndarray:
    """Finite-difference encoder velocity; initial sample uses forward difference."""
    q = np.asarray(q, dtype=float)
    if q.ndim != 1 or q.size < 2 or not np.all(np.isfinite(q)) or not np.isfinite(dt) or dt <= 0: raise ValueError("q must be 1-D with >=2 samples and dt>0")
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
    vals = (m.dt, m.duration_s, m.q0, m.qd0, m.arm_mass, m.payload_mass,
            m.arm_length, m.gravity, m.kp, m.kd)
    if (not all(np.isfinite(vals)) or m.dt <= 0 or m.duration_s < m.dt
            or m.arm_mass < 0 or m.payload_mass < 0 or m.inertia <= 0
            or m.arm_length <= 0 or m.gravity < 0 or m.kp < 0 or m.kd < 0
            or not isinstance(m.integration_substeps, (int, np.integer))
            or isinstance(m.integration_substeps, bool) or m.integration_substeps < 1):
        raise ValueError("invalid physical or numerical model parameters")


def _readonly(array: np.ndarray) -> np.ndarray:
    result = np.asarray(array, dtype=float).copy()
    result.setflags(write=False)
    return result


def _acc(m: PublicModel, q: float, torque: float) -> float:
    return (torque - m.gravity_moment * np.sin(q)) / m.inertia


def simulate(c: Config | PublicModel, q_des: np.ndarray, *, delay_s: float,
             q0: float | None = None, qd0: float | None = None,
             return_torque: bool = False, role: str = "simulation"):
    """Integrate deterministic held-torque RK4 dynamics and return arrays.

    ``return_torque=True`` returns ``(q, qd_raw, delayed_torque)`` for legacy
    callers. Use :func:`simulate_trajectory` to retain all command signals.
    """
    tr = simulate_trajectory(c, q_des, delay_s=delay_s, q0=q0, qd0=qd0, role=role)
    return (tr.q, tr.qd_raw, tr.torque) if return_torque else (tr.q, tr.qd_raw)


def simulate_trajectory(c: Config | PublicModel, q_des: np.ndarray, *, delay_s: float,
                        q0: float | None = None, qd0: float | None = None,
                        role: str = "simulation") -> Trajectory:
    m = _model(c); q_des = np.asarray(q_des, dtype=float)
    _validate_model(m)
    if q_des.ndim != 1 or q_des.size < 2 or not np.all(np.isfinite(q_des)):
        raise ValueError("q_des must be a finite 1-D array with >=2 samples")
    if not np.isfinite(delay_s) or delay_s < 0:
        raise ValueError("delay_s must be finite and non-negative")
    if not all(np.isfinite(v) for v in (m.q0 if q0 is None else q0, m.qd0 if qd0 is None else qd0)):
        raise ValueError("reset state must be finite")
    nsub = max(1, int(m.integration_substeps)); dt = m.dt / nsub; n = q_des.size
    q = np.empty(n); qd = np.empty(n); cmd = np.empty(n); torque = np.empty(n)
    q[0] = m.q0 if q0 is None else float(q0); qd[0] = m.qd0 if qd0 is None else float(qd0)
    for i in range(n):
        cmd[i] = m.kp * (q_des[i] - q[i]) - m.kd * qd[i]
        torque[i] = _delayed(cmd, i, delay_s, m.dt)
        if i == n - 1: break
        # Hold the delayed torque over the complete sample interval, with RK4 substeps.
        def f(xq, xv): return xv, _acc(m, xq, torque[i])
        xq, xv = q[i], qd[i]
        for _ in range(nsub):
            h = dt
            k1q, k1v = f(xq, xv); k2q, k2v = f(xq+.5*h*k1q, xv+.5*h*k1v)
            k3q, k3v = f(xq+.5*h*k2q, xv+.5*h*k2v); k4q, k4v = f(xq+h*k3q, xv+h*k3v)
            xq += h*(k1q+2*k2q+2*k3q+k4q)/6; xv += h*(k1v+2*k2v+2*k3v+k4v)/6
        q[i+1], qd[i+1] = xq, xv
    qd_obs = derive_velocity(q, m.dt)
    return Trajectory(*(_readonly(a) for a in (np.arange(n)*m.dt, q_des, q, qd_obs, qd, cmd, torque)), role)


def _validation_excitation(t: np.ndarray, c: Config) -> np.ndarray:
    phase = 2 * np.pi * (c.validation_frequency_hz * t + c.validation_modulation_cycles
                        * np.sin(2 * np.pi * c.validation_modulation_hz * t)) + c.validation_phase_rad
    return c.validation_amp * np.clip(c.validation_edge_gain * np.sin(phase), -1, 1)


def build_benchmark(c: Config) -> BenchmarkData:
    t = make_time(c); fd = excitation(t, c.fit_amp, c.fit_f0, c.fit_f1, c.duration_s)
    vd = _validation_excitation(t, c)
    ft = simulate_trajectory(c.model, fd, delay_s=c.truth.delay_s, role="oracle")
    vt = simulate_trajectory(c.model, vd, delay_s=c.truth.delay_s, role="oracle")
    metadata = {
        "config_version": c.version, "config_hash": hashlib.sha256(json.dumps(asdict(c), sort_keys=True, default=str).encode()).hexdigest()[:16], "seed": c.seed,
        "timestamp_utc": c.timestamp_utc, "units": {"t": "s", "q": "rad", "qd": "rad/s", "torque": "N m"},
        "observations": ["t", "q_des", "q", "qd"], "public_observations": ["t", "q_des", "q", "qd"],
        "oracle_only": ["true_torque", "delayed_command_state", "raw_integration_velocity"],
        "delay_semantics": "effective command delay after fixed PD law; fractional linear interpolation; zero prehistory",
        "sensor_velocity": "qd from q: forward difference at initial sample, centered interior, backward final sample",
        "fit_excitation": {"kind": "linear chirp", "amplitude_rad": c.fit_amp,
                           "f0_hz": c.fit_f0, "f1_hz": c.fit_f1, "phase_rad": 0.0,
                           "duration_s": c.duration_s},
        "validation_excitation": {"kind": "phase-modulated clipped-sine reversal",
                                  "amplitude_rad": c.validation_amp,
                                  "frequency_hz": c.validation_frequency_hz,
                                  "modulation_cycles": c.validation_modulation_cycles,
                                  "modulation_hz": c.validation_modulation_hz,
                                  "phase_rad": c.validation_phase_rad,
                                  "edge_gain": c.validation_edge_gain},
        "controller": {"kp": c.kp, "kd": c.kd, "sample_period_s": c.dt,
                       "velocity_feedback": "fixed internal integration velocity",
                       "filtering": "none", "rate_limits": "none"},
        "model": asdict(c.model),
        "reset_state": {"q": c.q0, "qd": c.qd0}, "numerical": {"dt": c.dt, "integrator": "RK4 held torque", "substeps": c.model.integration_substeps},
    }
    return BenchmarkData(Observations(ft.t, ft.q_des, ft.q, ft.qd), Observations(vt.t, vt.q_des, vt.q, vt.qd),
                         ft.torque, vt.torque, metadata, {"fit": ft, "validation": vt})


def fit_student(observations: Observations, model: PublicModel, *, optimizer_start: Params | None = None,
                lower: Params = Params(0.0), upper: Params = Params(0.2)) -> FitResult:
    """Fit delay from public observations and a frozen public model only."""
    if not isinstance(observations, Observations): raise TypeError("observations required")
    if not isinstance(model, PublicModel): raise TypeError("model must be PublicModel")
    _validate_model(model)
    arrays = [np.asarray(getattr(observations, key), dtype=float) for key in ("t", "q_des", "q", "qd")]
    if any(a.ndim != 1 or a.size < 2 or not np.all(np.isfinite(a)) for a in arrays):
        raise ValueError("observations must be finite 1-D arrays with >=2 samples")
    if any(a.shape != arrays[0].shape for a in arrays):
        raise ValueError("observation arrays must have equal shape")
    if not np.allclose(arrays[0], np.arange(arrays[0].size) * model.dt, rtol=0, atol=1e-10):
        raise ValueError("observation t must start at zero with uniform model.dt sampling")
    start = optimizer_start or Params((lower.delay_s + upper.delay_s) / 2)
    if not all(np.isfinite((lower.delay_s, upper.delay_s, start.delay_s))) or not (lower.delay_s <= start.delay_s <= upper.delay_s) or lower.delay_s < 0 or upper.delay_s <= lower.delay_s: raise ValueError("invalid optimizer bounds/start")
    def residual(x):
        tr = simulate_trajectory(model, observations.q_des, delay_s=float(x[0]), q0=model.q0, qd0=model.qd0)
        return np.r_[tr.q - observations.q, tr.qd - observations.qd]
    result = least_squares(residual, [start.delay_s], bounds=([lower.delay_s], [upper.delay_s]), max_nfev=100,
                           ftol=1e-12, xtol=1e-12, gtol=1e-12)
    if float(result.cost) > 1e-8:
        starts = np.linspace(lower.delay_s, upper.delay_s, 7)
        results = [least_squares(residual, [float(s)], bounds=([lower.delay_s], [upper.delay_s]), max_nfev=100,
                                 ftol=1e-12, xtol=1e-12, gtol=1e-12) for s in starts]
        result = min([result, *results], key=lambda r: float(r.cost))
    return FitResult(Params(float(result.x[0])), bool(result.success), str(result.message), float(result.cost), int(result.nfev))


def score(observations: Observations, model_or_config: Config | PublicModel, delay_s: float, *, trajectory: Trajectory | None = None) -> Metrics:
    tr = trajectory or simulate_trajectory(model_or_config, observations.q_des, delay_s=delay_s, q0=(_model(model_or_config)).q0, qd0=(_model(model_or_config)).qd0, role="score")
    dq, dv = tr.q - observations.q, tr.qd - observations.qd
    return Metrics(float(np.mean(abs(dq))), float(np.mean(abs(dv))), float(np.sqrt(np.mean(dq*dq))), float(np.sqrt(np.mean(dv*dv))))


def run_l1(c: Config | None = None) -> Run:
    c = c or load_config(); data = build_benchmark(c)
    fit = fit_student(data.fit, c.model, optimizer_start=c.optimizer_start, lower=c.lower, upper=c.upper)
    trajectories: dict[str, dict[str, Trajectory]] = {}
    for split, obs in (("fit", data.fit), ("validation", data.validation)):
        trajectories[split] = {
            "oracle": data.oracle_trajectories[split],
            "initial": simulate_trajectory(c.model, obs.q_des, delay_s=c.initial.delay_s, q0=c.model.q0, qd0=c.model.qd0, role="initial"),
            "identified": simulate_trajectory(c.model, obs.q_des, delay_s=fit.params.delay_s, q0=c.model.q0, qd0=c.model.qd0, role="identified"),
        }
    loss_slice = tuple({"delay_s": float(d), "fit_q_rmse": score(data.fit, c.model, float(d)).q_rmse}
                       for d in np.linspace(max(c.lower.delay_s, fit.params.delay_s - .02),
                                            min(c.upper.delay_s, fit.params.delay_s + .02), 9))
    return Run(c, data, fit, score(data.fit, c.model, c.initial.delay_s, trajectory=trajectories["fit"]["initial"]),
               score(data.fit, c.model, fit.params.delay_s, trajectory=trajectories["fit"]["identified"]),
               score(data.validation, c.model, c.initial.delay_s, trajectory=trajectories["validation"]["initial"]),
               score(data.validation, c.model, fit.params.delay_s, trajectory=trajectories["validation"]["identified"]), trajectories, loss_slice)


def run_summary(r: Run) -> dict[str, Any]:
    return {"config_version": r.config.version, "metadata": r.data.metadata, "truth": asdict(r.config.truth),
            "initial": asdict(r.config.initial), "identified": asdict(r.fit.params), "fit_result": asdict(r.fit),
            "fit": {"initial": asdict(r.initial_fit), "identified": asdict(r.identified_fit)},
            "validation": {"initial": asdict(r.initial_validation), "identified": asdict(r.identified_validation)},
            "effective_delay_note": "identified delay is boundary and sampling dependent",
            "local_loss_slice": list(r.local_loss_slice),
            "acceptance": {"delay_tolerance_s": 0.001, "minimum_validation_rmse_improvement": 0.90,
                           "delay_error_s": abs(r.fit.params.delay_s - r.config.truth.delay_s),
                           "validation_q_improvement": 1 - r.identified_validation.q_rmse / r.initial_validation.q_rmse if r.initial_validation.q_rmse else None,
                           "validation_qd_improvement": 1 - r.identified_validation.qd_rmse / r.initial_validation.qd_rmse if r.initial_validation.qd_rmse else None}}



def machine_frame(r: Run, split: str = "validation", index: int = 0, role: str = "oracle") -> dict[str, Any]:
    tr = r.trajectories[split][role]; i = int(np.clip(index, 0, tr.q.size - 1)); q, qd, L = float(tr.q[i]), float(tr.qd[i]), r.config.arm_length
    return {"index": i, "t": float(tr.t[i]), "q": q, "qd": qd, "tip": (L*np.sin(q), -L*np.cos(q)), "tip_velocity": (L*np.cos(q)*qd, L*np.sin(q)*qd), "role": role, "split": split}


def machine_svg(r: Run, split: str = "validation", index: int = 0) -> str:
    """Render a recorded replay frame with all role angles and velocities."""
    roles = (("oracle", "#111", "", "o"), ("initial", "#e67e22", "", ""), ("identified", "#2878b5", "stroke-dasharray=5,3", ""))
    L = r.config.arm_length; cx, cy, scale = 110, 125, 72
    lines, labels = [], []
    for role, color, dash, marker in roles:
        f = machine_frame(r, split, index, role); q = f["q"]; x = cx + scale*np.sin(q); y = cy + scale*np.cos(q)
        extra = f' {dash}' if dash else ''
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="5"{extra}/>')
        lines.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="white" stroke="{color}" stroke-width="2"/>')
        labels.append(f'<text x="8" y="{155 + len(labels)*11}" fill="{color}" font-size="9">{role}: q={q:.3f}, qd={f["qd"]:.3f}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 205" role="img"><title>Loaded pendulum replay at t={machine_frame(r,split,index)["t"]:.3f}s</title>'
            '<defs><marker id="g" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#c33"/></marker></defs>'
            '<rect x="98" y="115" width="24" height="16" fill="#444"/><circle cx="110" cy="123" r="7" fill="#777"/>'
            + ''.join(lines) + '<line x1="110" y1="25" x2="110" y2="90" stroke="#c33" stroke-width="3" marker-end="url(#g)"/><text x="126" y="38" fill="#c33" font-size="9">gravity</text>' + ''.join(labels) + '</svg>')


def plot_run(r: Run, path: str | Path) -> Path:
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(5, 2, figsize=(13, 16), constrained_layout=True)
    colors = {"oracle": "tab:blue", "initial": "tab:red", "identified": "tab:green"}
    styles = {"oracle": "-", "initial": ":", "identified": "--"}
    for col, split in enumerate(("fit", "validation")):
        obs = getattr(r.data, split)
        ax[0, col].plot(obs.t, obs.q_des, color="black", alpha=.7, label="q_des target")
        for role in ("oracle", "initial", "identified"):
            tr = r.trajectories[split][role]
            ax[0, col].plot(tr.t, tr.q, color=colors[role], ls=styles[role], marker="o" if role == "oracle" else None, markevery=80, label=role.title())
            ax[1, col].plot(tr.t, tr.qd, color=colors[role], ls=styles[role], marker="o" if role == "oracle" else None, markevery=80, label=role.title())
        ax[0, col].set_title(f"{split.title()} angle")
        ax[1, col].set_title(f"{split.title()} velocity")
        ax[0, col].set_ylabel("rad"); ax[1, col].set_ylabel("rad/s")
        ax[0, col].legend(fontsize=8); ax[1, col].legend(fontsize=8)
        if split == "fit":
            for role in ("oracle", "initial", "identified"):
                tr = r.trajectories[split][role]
                ax[2, col].plot(tr.t, tr.command_torque, ls=styles[role], color=colors[role], label=f"{role} pre-delay command")
                ax[2, col].plot(tr.t, tr.torque, ls=styles[role], color=colors[role], alpha=.45, label=f"{role} applied torque")
            ax[2, col].set_title("Fit torque diagnostics (Oracle-only)")
            ax[2, col].set_ylabel("N m"); ax[2, col].legend(fontsize=7)
        else:
            ax[2, col].axis("off")
        initial = r.trajectories[split]["initial"]; identified = r.trajectories[split]["identified"]
        ax[3, col].plot(obs.t, initial.q - obs.q, color="tab:red", ls=styles["initial"], label="Initial q residual")
        ax[3, col].plot(obs.t, identified.q - obs.q, color="tab:green", ls=styles["identified"], label="Identified q residual")
        ax[4, col].plot(obs.t, initial.qd - obs.qd, color="tab:red", ls=styles["initial"], label="Initial qd residual")
        ax[4, col].plot(obs.t, identified.qd - obs.qd, color="tab:green", ls=styles["identified"], label="Identified qd residual")
        ax[3, col].set_title(f"{split.title()} residual vs time (q)")
        ax[4, col].set_title(f"{split.title()} residual vs time (qd)")
        ax[3, col].set_ylabel("rad"); ax[4, col].set_ylabel("rad/s")
        ax[3, col].legend(fontsize=7); ax[4, col].legend(fontsize=7)
    # A command/velocity residual view keeps the omitted effect visible in state space.
    fitobs = r.data.fit; ini = r.trajectories["fit"]["initial"]; ident = r.trajectories["fit"]["identified"]
    ax[2, 1].scatter(fitobs.qd, ini.qd - fitobs.qd, s=4, label="Initial", color="tab:red")
    ax[2, 1].scatter(fitobs.qd, ident.qd - fitobs.qd, s=4, label="Identified", color="tab:green")
    ax[2, 1].set_title("Fit residual vs measured velocity"); ax[2, 1].set_xlabel("qd (rad/s)"); ax[2, 1].set_ylabel("qd residual (rad/s)"); ax[2, 1].legend(fontsize=8)
    # Separate machine view: use recorded trajectory only, without simulation.
    f = machine_frame(r, "validation", len(r.data.validation.t)//2); x, y = f["tip"]
    ax[3, 1].plot([0, x], [0, y], lw=7, color="tab:blue"); ax[3, 1].scatter([x], [y], s=120, color="tab:orange"); ax[3, 1].scatter([0], [0], s=100, color="black", marker="s")
    ax[3, 1].arrow(0, 0, 0, -r.config.arm_length*.4, color="tab:red", width=.01); ax[3, 1].set_aspect("equal"); ax[3, 1].set_title("Machine schematic (synthetic)"); ax[3, 1].set_xlabel(f'q={f["q"]:.3f} rad, qd={f["qd"]:.3f} rad/s')
    ax[4, 1].axis("off")
    fig.savefig(p, dpi=140); plt.close(fig); return p


def write_report(r: Run, out: str | Path) -> Path:
    out=Path(out); out.mkdir(parents=True,exist_ok=True); plot_run(r,out/"report.png"); (out/"metrics.json").write_text(json.dumps(run_summary(r),indent=2))
    pct=100*(1-r.identified_validation.q_rmse/r.initial_validation.q_rmse) if r.initial_validation.q_rmse else 0
    text=f'''# L1 Servo Driven Loaded Pendulum\n\n![Recorded machine and trajectories](report.png)\n\nThis synthetic ideal experiment uses a fixed base, a uniform rigid arm (mass {r.config.arm_mass:g} kg, length {r.config.arm_length:g} m), a known point payload ({r.config.payload_mass:g} kg), gravity, and a fixed PD position servo. The declared boundary is `q_des -> PD -> effective command delay -> pendulum torque`; delay is applied after the PD law with fractional interpolation and zero prehistory.\n\nThe Oracle delay is **{r.config.truth.delay_s:.3f} s**. The Initial model fixes delay at **{r.config.initial.delay_s:.3f} s**. The Identified Student fits only `t`, `q_des`, `q`, and finite-difference `qd` from fit data, recovering **{r.fit.params.delay_s:.3f} s**. On held-out validation, q RMSE changes from **{r.initial_validation.q_rmse:.6g}** to **{r.identified_validation.q_rmse:.6g}** ({pct:.1f}% improvement).\n\nTorque, pre-delay command, raw integration velocity, and delayed state are Oracle diagnostics and never estimator inputs. Residuals expose phase/tracking error from the omitted delay; fit and validation use separate reset trajectories. The fitted value is an effective parameter dependent on this command boundary and sampling.\n\nOmitted effects include friction, saturation, compliance/backlash, sensor noise, voltage and thermal behavior, contacts, payload shifts, and whole-robot dynamics. This is not a motor-electromagnetic or hardware-transfer model.\n\n| Role | Delay | Mechanical parameters |
|---|---:|---|
| Oracle | hidden {r.config.truth.delay_s:.3f} s | known arm + payload |
| Initial Student | fixed {r.config.initial.delay_s:.3f} s | known arm + payload |
| Identified Student | fitted {r.fit.params.delay_s:.3f} s | known arm + payload |

Acceptance thresholds are delay error <= 1 ms and held-out q/qd RMSE improvement >= 90%. A local loss slice around the fitted delay is recorded in `metrics.json` to show the identification minimum. Run metadata, units, seed, reset state, excitation definitions, configuration hash, and numerical settings are recorded in `metrics.json`. Read the [guided lesson](../../docs/lessons/l1/README.md) for the learner exercise.\n'''
    (out/"report.md").write_text(text); return out/"report.md"


def main(argv=None):
    a=argparse.ArgumentParser(); a.add_argument("--output-dir",default="reports/l1_servo_loaded_pendulum"); write_report(run_l1(),a.parse_args(argv).output_dir); return 0

if __name__ == "__main__": raise SystemExit(main())
