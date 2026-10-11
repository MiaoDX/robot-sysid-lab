import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from sysid_lab.cli import export_l0
from sysid_lab.l0_inertia_damping import run_l0
from synthetic.l0_inertia_damping import run_l0 as legacy_run_l0


def test_canonical_runner_matches_legacy_runner():
    canonical, legacy = run_l0(), legacy_run_l0()
    np.testing.assert_allclose(
        [canonical.fit.params.inertia, canonical.fit.params.damping],
        [legacy.fit.params.inertia, legacy.fit.params.damping],
        rtol=1e-8,
        atol=1e-10,
    )
    for current, reference in (
        (canonical.data.fit, legacy.data.fit),
        (canonical.data.validation, legacy.data.validation),
    ):
        for left, right in zip((current.t, current.u, current.q, current.qd), (reference.t, reference.u, reference.q, reference.qd)):
            np.testing.assert_allclose(left, right, rtol=1e-7, atol=1e-9)


def test_export_manifest_is_self_consistent(tmp_path):
    export_l0(tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    paths = {entry["path"] for entry in manifest["files"]}
    assert "manifest.json" not in paths
    assert {"config.json", "metrics.json", "trajectory.json", "report.md"} <= paths
    for entry in manifest["files"]:
        digest = hashlib.sha256((tmp_path / entry["path"]).read_bytes()).hexdigest()
        assert digest == entry["sha256"]


def test_lesson_slice_has_bilingual_pages_and_no_old_report_links():
    root = Path("course/lessons/02-inertia-damping")
    pages = sorted(root.glob("*.md"))
    assert len(pages) == 12
    assert all(path.with_name(path.name.replace(".zh-CN.md", ".md")).exists() for path in pages if ".zh-CN." in path.name)
    text = "\n".join(path.read_text(encoding="utf-8") for path in pages)
    assert "reports/02_inertia_damping" not in text
    assert "notebooks/02_inertia_damping" not in text
    assert "artifacts/02-inertia-damping" in text


def test_shadow_pages_load_required_runtimes(tmp_path):
    pytest.importorskip("markdown")
    pytest.importorskip("bs4")
    from bs4 import BeautifulSoup
    from tools.build_course import build_shadow

    output = tmp_path / "site-preview"
    assert build_shadow(Path("course"), output) == 12
    math_assets = [Path("docs/site/vendor/katex/katex.min.js"), Path("docs/site/math.js")]
    math_names = [asset.name for asset in math_assets]
    for page in (output / "course").rglob("*.html"):
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        math_scripts = [tag for tag in soup.select("script[src]") if Path(tag["src"]).name in math_names]
        assert [Path(tag["src"]).name for tag in math_scripts] == math_names, page
        for script, asset in zip(math_scripts, math_assets):
            assert "defer" in script.attrs, page
            assert (page.parent / script["src"]).read_bytes() == asset.read_bytes(), page
        scripts = [tag for tag in soup.select("script[src]") if tag["src"].endswith("subtitles.js")]
        if soup.select_one("video"):
            assert len(scripts) == 1, page
            assert "defer" in scripts[0].attrs
            assert (page.parent / scripts[0]["src"]).read_bytes() == Path("docs/site/subtitles.js").read_bytes()
        else:
            assert not scripts, page
