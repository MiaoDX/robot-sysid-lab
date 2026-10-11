# L0 Vertical Slice Verification Record

This record closes the implementation gates for `docs/plans/l0-vertical-slice-migration.md`.

## Environment

- Python: 3.12.12, constrained by `requires-python = ">=3.11,<3.13"`
- Locked core: numpy 2.4.0, scipy 1.17.0, matplotlib 3.10.8
- Locked extras: Markdown, beautifulsoup4, marimo, pytest
- Install proof: `uv sync --frozen --extra docs --extra interactive --extra dev`

## Automated Proof

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run pytest -q`: 68 passed.
- `uv run sysid-lab run 02 --output-dir artifacts/02-inertia-damping`: passed.
- Legacy `uv run python -m synthetic.l0_inertia_damping --output-dir .tmp/l0-old`: passed.
- Canonical and legacy parameters, metrics, and `t/u/q/qd` arrays match at the plan tolerances.
- Repeated canonical payloads (`config.json`, `metrics.json`, `trajectory.json`, `fitting_paths.json`) are byte-stable; provenance in `manifest.json` is excluded.
- Manifest contains seven non-manifest files, roles, provenance, and valid SHA-256 values.
- `uv run python tools/build_course.py --source-root course --output-dir site-preview` and `--check`: passed, 12 pages.
- The 12 generated course pages have 82 local resource references; all resolve inside the preview or its copied static roots.
- `uv run python -m json.tool notebooks/l0_inertia_damping.ipynb`: passed.

## Manual Browser Proof

The local preview is served from `.tmp/site-preview` at `http://127.0.0.1:4173`. Desktop (1280px) and narrow (375px) checks cover the English and Chinese index pages, local artifact image, bilingual navigation, horizontal overflow, and console errors. Screenshots and console summaries are retained in `.tmp/browser-proof/`.

## Compatibility Boundary

The old `synthetic.l0_inertia_damping` import and module command remain shims over `sysid_lab`; old reports, docs, Manim imports, notebook, and Pages source were not deleted or switched.
