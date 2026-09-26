"""Static site contracts; these checks do not require documentation build packages."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.lang = None
        self.links = []
        self.switches = {}
        self.ids = set()
        self.tracks = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for attr in ("href", "src", "poster"):
            if attr in attrs:
                self.links.append(attrs[attr])
        if tag == "a" and attrs.get("lang") in ("en", "zh-CN") and "hreflang" in attrs:
            self.switches[attrs["hreflang"]] = attrs["href"]
        if tag == "track":
            self.tracks.append(attrs)


def site_pages():
    return sorted(p for directory in (ROOT / "docs", ROOT / "reports") for p in directory.rglob("*.html"))


def test_all_site_pages_have_same_page_language_switches():
    for path in site_pages():
        page = Page(path)
        assert page.lang in ("en", "zh-CN"), path
        assert set(page.switches) == {"en", "zh-CN"}, path
        for language, link in page.switches.items():
            destination = (path.parent / urlsplit(link).path).resolve()
            assert destination.is_file(), (path, link)
            assert Page(destination).lang == language
            assert destination.name.replace(".zh-CN", "") == path.name.replace(".zh-CN", "")
            assert destination.parent == path.parent


def test_site_file_links_and_local_section_links_resolve():
    for path in site_pages():
        page = Page(path)
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            assert target.exists(), (path.relative_to(ROOT), link)
            if url.fragment and target.suffix == ".html":
                assert unquote(url.fragment) in Page(target).ids, (path.relative_to(ROOT), link)


def test_video_pages_select_subtitles_for_the_page_language():
    for path in (ROOT / "docs/lessons").glob("l*/index*.html"):
        page = Page(path)
        expected = 4 if path.parent.name == "l0" else 3
        defaults = [track for track in page.tracks if "default" in track]
        assert len(defaults) == expected
        assert all(track["srclang"] == page.lang for track in defaults)
        assert len(page.tracks) == 2 * expected
        for track in page.tracks:
            assert (path.parent / track["src"]).read_text().startswith("WEBVTT\n")


def test_translated_report_tables_keep_the_recorded_numbers():
    def numbers(path):
        table = "\n".join(line for line in path.read_text().splitlines() if line.startswith("|"))
        return re.findall(r"\d+(?:\.\d+)?(?:e[+-]?\d+)?", table)

    for original in (ROOT / "reports").glob("l*/report.md"):
        assert numbers(original) == numbers(original.with_name("report.zh-CN.md")), original
