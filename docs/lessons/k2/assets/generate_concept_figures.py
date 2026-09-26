"""Generate K2's illustrative torque/residual figure.

This is an analytic teaching example, deliberately separate from any lab run.
It uses q(t)=0.45 sin(1.3t), with declared J, b, m*g*l and a declared illustrative residual. The output is a conceptual figure, not experiment data.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "torque-residual-illustrative.png"

t = np.linspace(0, 8, 800)
q = 0.45 * np.sin(1.3 * t)
qd = 0.45 * 1.3 * np.cos(1.3 * t)
qdd = -0.45 * 1.3**2 * np.sin(1.3 * t)
J, b, mgl = 0.8, 0.12, 1.4
inertia = J * qdd
dissipation = b * qd
gravity = mgl * np.sin(q)
residual = 0.18 * np.sin(0.9 * t + 0.4) * np.abs(qd) / np.max(np.abs(qd))

fig, axes = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True, constrained_layout=True)
fig.suptitle("Illustrative analytic decomposition · not experiment evidence", fontsize=13, fontweight="bold")
axes[0].plot(t, q, color="#176f91", lw=2, label="q (rad)")
axes[0].plot(t, qd, color="#26734a", lw=1.6, label="q̇ (rad/s)")
axes[0].set_ylabel("angle (rad) / rate (rad/s)")
axes[0].legend(ncol=2, frameon=False, loc="upper right")
axes[0].grid(alpha=0.2)
axes[1].plot(t, inertia, color="#a65b08", lw=1.8, label="inertia Jq̈")
axes[1].plot(t, gravity, color="#176f91", lw=1.8, label="gravity mgl sin(q)")
axes[1].plot(t, dissipation, color="#26734a", lw=1.8, label="dissipation bq̇")
axes[1].plot(t, residual, color="#8d2f58", lw=2, ls="--", label="illustrative residual")
axes[1].axhline(0, color="#59665f", lw=0.8)
axes[1].set_xlabel("time (s)")
axes[1].set_ylabel("torque (N·m)")
axes[1].legend(ncol=2, frameon=False, loc="upper right")
axes[1].grid(alpha=0.2)
fig.savefig(OUT, dpi=160)
print(OUT)
