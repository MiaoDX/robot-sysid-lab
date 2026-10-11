from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import re
from dataclasses import asdict
from pathlib import Path

from .l0_inertia_damping import (
    load_config,
    run_l0,
    run_summary,
    write_fitting_journey,
    write_report,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_l0(output: Path, config_path: Path | None = None) -> Path:
    canonical_output = (Path.cwd() / "artifacts/02-inertia-damping").resolve()
    if config_path is not None and output.resolve() == canonical_output:
        raise ValueError("--config requires an explicit --output-dir")
    config = load_config(config_path)
    run = run_l0(config)
    output.mkdir(parents=True, exist_ok=True)
    write_report(run, output)
    write_fitting_journey(run, output)
    report_path = output / "report.md"
    report = report_path.read_text(encoding="utf-8")
    report = re.sub(r"\[[^]]+\]\([^)]*docs/lessons/l0[^)]*\)", "[lesson artifact](manifest.json)", report)
    report = re.sub(r"\[[^]]+\]\([^)]*apps/l0_inertia_damping\.py\)", "[lesson artifact](manifest.json)", report)
    report = re.sub(r"\[[^]]+\]\([^)]*03-assumptions-and-next-step\.md\)", "[lesson artifact](manifest.json)", report)
    report = report.replace("python -m synthetic.l0_inertia_damping --output-dir reports/l0_inertia_damping", "uv run sysid-lab run 02 --output-dir artifacts/02-inertia-damping")
    report_path.write_text(report, encoding="utf-8")
    (output / "config.json").write_text(
        json.dumps({
            "version": config.version, "dt": config.dt, "duration_s": config.duration_s,
            "initial_state": {"q": config.q0, "qd": config.qd0},
            "nominal": asdict(config.nominal), "bounds": {"lower": asdict(config.lower_bounds), "upper": asdict(config.upper_bounds)},
            "fit_excitation": {"f0_hz": config.chirp_f0_hz, "f1_hz": config.chirp_f1_hz, "amplitude_nm": config.chirp_amplitude_nm},
            "validation_excitation": {"frequencies_hz": config.validation_frequencies_hz, "amplitudes_nm": config.validation_amplitudes_nm, "phases_rad": config.validation_phases_rad},
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    trajectory = {"t": run.data.fit.t.tolist(), "fit": {"u": run.data.fit.u.tolist(), "q": run.data.fit.q.tolist(), "qd": run.data.fit.qd.tolist()}, "validation": {"u": run.data.validation.u.tolist(), "q": run.data.validation.q.tolist(), "qd": run.data.validation.qd.tolist()}}
    (output / "trajectory.json").write_text(json.dumps(trajectory, separators=(",", ":")) + "\n", encoding="utf-8")
    files = []
    roles = {"config.json": "public", "metrics.json": "evaluation", "trajectory.json": "public", "report.md": "public", "report.png": "public", "fitting_paths.json": "evaluation", "fitting_landscape.png": "evaluation"}
    for name, role in roles.items():
        files.append({"path": name, "role": role, "sha256": _sha256(output / name)})
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    manifest = {"schema_version": "1.0", "lesson": {"number": 2, "slug": "02-inertia-damping"}, "command": "sysid-lab run 02", "git_commit": commit, "config_path": str(config_path or "synthetic/l0_config.json"), "config_sha256": _sha256(output / "config.json"), "python": platform.python_version(), "dependencies": {"numpy": __import__("numpy").__version__, "scipy": __import__("scipy").__version__}, "random_seed": None, "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "files": files}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sysid-lab")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("lesson")
    run.add_argument("--output-dir", type=Path, default=Path("artifacts/02-inertia-damping"))
    run.add_argument("--config", type=Path)
    args = parser.parse_args(argv)
    if args.lesson not in {"02", "02-inertia-damping"}:
        parser.error("only lesson 02-inertia-damping is available")
    export_l0(args.output_dir, args.config)
    print(f"artifact: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
