"""Minimal teacher/student SysID lab.

The teacher plant contains inertia, viscous friction, Coulomb friction and delay.
The student model intentionally starts with a smaller hypothesis class.

Run:
    python synthetic/one_dof_lab.py

Requires only numpy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Tuple

import numpy as np


@dataclass(frozen=True)
class Params:
    inertia: float
    viscous: float
    coulomb: float = 0.0
    delay_s: float = 0.0


def chirp_command(t: np.ndarray, f0: float = 0.2, f1: float = 4.0) -> np.ndarray:
    duration = t[-1] if t[-1] > 0 else 1.0
    k = (f1 - f0) / duration
    phase = 2.0 * np.pi * (f0 * t + 0.5 * k * t**2)
    return 0.8 * np.sin(phase)


def multi_sine_command(t: np.ndarray) -> np.ndarray:
    return (
        0.55 * np.sin(2.0 * np.pi * 0.35 * t)
        + 0.25 * np.sin(2.0 * np.pi * 1.3 * t + 0.3)
        + 0.12 * np.sin(2.0 * np.pi * 3.0 * t + 1.0)
    )


def simulate(params: Params, t: np.ndarray, command: np.ndarray) -> np.ndarray:
    """Simulate J*qdd + b*qd + Fc*sign(qd) = u(t-delay)."""
    dt = float(t[1] - t[0])
    q = np.zeros_like(t)
    dq = np.zeros_like(t)
    delay_steps = max(0, int(round(params.delay_s / dt)))

    for k in range(len(t) - 1):
        cmd_idx = max(0, k - delay_steps)
        u = command[cmd_idx]
        friction = params.viscous * dq[k]
        if abs(dq[k]) > 1e-6:
            friction += params.coulomb * np.sign(dq[k])
        ddq = (u - friction) / params.inertia
        dq[k + 1] = dq[k] + dt * ddq
        q[k + 1] = q[k] + dt * dq[k + 1]
    return q


def mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b)))


def random_search(
    t: np.ndarray,
    u: np.ndarray,
    y: np.ndarray,
    sampler: Callable[[np.random.Generator], Params],
    iterations: int = 2500,
    seed: int = 0,
) -> Tuple[Params, float]:
    rng = np.random.default_rng(seed)
    best_params = None
    best_loss = np.inf
    for _ in range(iterations):
        candidate = sampler(rng)
        loss = mae(simulate(candidate, t, u), y)
        if loss < best_loss:
            best_params = candidate
            best_loss = loss
    assert best_params is not None
    return best_params, best_loss


def fit_model(
    name: str,
    t: np.ndarray,
    u: np.ndarray,
    y: np.ndarray,
) -> Tuple[Params, float]:
    if name == "M0_inertia_only":
        sampler = lambda rng: Params(
            inertia=rng.uniform(0.02, 0.12), viscous=0.0, coulomb=0.0, delay_s=0.0
        )
    elif name == "M1_viscous":
        sampler = lambda rng: Params(
            inertia=rng.uniform(0.02, 0.12),
            viscous=rng.uniform(0.0, 0.16),
            coulomb=0.0,
            delay_s=0.0,
        )
    elif name == "M2_friction":
        sampler = lambda rng: Params(
            inertia=rng.uniform(0.02, 0.12),
            viscous=rng.uniform(0.0, 0.16),
            coulomb=rng.uniform(0.0, 0.2),
            delay_s=0.0,
        )
    elif name == "M3_friction_delay":
        sampler = lambda rng: Params(
            inertia=rng.uniform(0.02, 0.12),
            viscous=rng.uniform(0.0, 0.16),
            coulomb=rng.uniform(0.0, 0.2),
            delay_s=rng.uniform(0.0, 0.04),
        )
    else:
        raise ValueError(name)
    return random_search(t, u, y, sampler=sampler)


def main() -> None:
    dt = 0.005
    t = np.arange(0.0, 12.0, dt)

    # Hidden from the identification algorithm in a real benchmark.
    teacher = Params(inertia=0.065, viscous=0.055, coulomb=0.075, delay_s=0.018)

    u_fit = chirp_command(t)
    y_fit = simulate(teacher, t, u_fit)

    # Different input spectrum for validation.
    u_val = multi_sine_command(t)
    y_val = simulate(teacher, t, u_val)

    models = [
        "M0_inertia_only",
        "M1_viscous",
        "M2_friction",
        "M3_friction_delay",
    ]

    print("Hidden teacher:", teacher)
    print()
    print(f"{'model':24s} {'fit MAE':>12s} {'val MAE':>12s}  parameters")
    print("-" * 90)
    for idx, model in enumerate(models):
        params, fit_loss = fit_model(model, t, u_fit, y_fit)
        val_loss = mae(simulate(params, t, u_val), y_val)
        print(f"{model:24s} {fit_loss:12.6f} {val_loss:12.6f}  {params}")

    print("\nQuestions to discuss:")
    print("1. Which model improves held-out prediction, not only fit loss?")
    print("2. Do fitted parameters approach the hidden truth as structure improves?")
    print("3. What changes if the fit trajectory is slow and quasi-static?")
    print("4. What happens if the teacher adds backlash but no student model can represent it?")


if __name__ == "__main__":
    main()
