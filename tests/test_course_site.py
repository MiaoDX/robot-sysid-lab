"""Static site contracts; these checks do not require documentation build packages."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
STANDALONE_SITE_PAGES = {
    ROOT / "docs/course/lesson-visual-styles.html",
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.lang = None
        self.links = []
        self.switches = {}
        self.ids = set()
        self.tracks = []
        self.videos = []
        self.current_video = None
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
            if self.current_video is not None:
                self.current_video["tracks"].append(attrs)
        if tag == "video":
            self.current_video = {"tracks": [], "sources": []}
            self.videos.append(self.current_video)
        if tag == "source" and self.current_video is not None:
            self.current_video["sources"].append(attrs)

    def handle_endtag(self, tag):
        if tag == "video":
            self.current_video = None


def site_pages():
    return sorted(p for directory in (ROOT / "docs", ROOT / "reports") for p in directory.rglob("*.html"))


def paired_site_pages():
    pages = set(site_pages())
    return sorted(path for path in pages if _language_peer(path) in pages)


def _language_peer(path):
    if ".zh-CN.html" in path.name:
        return path.with_name(path.name.replace(".zh-CN.html", ".html"))
    return path.with_name(path.name.replace(".html", ".zh-CN.html"))


def test_all_site_pages_have_same_page_language_switches():
    unpaired = set(site_pages()) - set(paired_site_pages())
    assert unpaired == STANDALONE_SITE_PAGES
    for path in paired_site_pages():
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
    # Discover every embed, including knowledge lessons that reuse a lab clip.
    for path in paired_site_pages():
        page = Page(path)
        for video in page.videos:
            assert video["sources"], path
            tracks = video["tracks"]
            assert sorted(track["srclang"] for track in tracks) == ["en", "zh-CN"], path
            defaults = [track for track in tracks if "default" in track]
            assert len(defaults) == 1 and defaults[0]["srclang"] == page.lang, path
            cue_times = []
            for track in tracks:
                text = (path.parent / track["src"]).read_text()
                assert text.startswith("WEBVTT\n")
                stamps = re.findall(r"(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})", text)
                assert stamps, (path, track)
                assert all(start < end for start, end in stamps), (path, track)
                assert all(end <= following for (_, end), (following, _) in zip(stamps, stamps[1:])), (path, track)
                cue_times.append(stamps)
            assert cue_times[0] == cue_times[1], (path, "translations must follow the same scenes")


def test_translated_report_tables_keep_the_recorded_numbers():
    def numbers(path):
        table = "\n".join(line for line in path.read_text().splitlines() if line.startswith("|"))
        return re.findall(r"\d+(?:\.\d+)?(?:e[+-]?\d+)?", table)

    for original in (ROOT / "reports").glob("l*/report.md"):
        assert numbers(original) == numbers(original.with_name("report.zh-CN.md")), original


def test_course_status_inventory_matches_every_lesson_and_embed():
    """The public media ledger must describe actual lesson delivery, not intent."""
    lessons = {path.parent.name for path in (ROOT / "docs/lessons").glob("*/index.md")}
    for suffix in ("", ".zh-CN"):
        status = (ROOT / f"docs/course/status{suffix}.md").read_text()
        rows = {}
        for line in status.splitlines():
            match = re.match(r"\| \[([KL][\d]+(?:-[A-Z])?)\]", line)
            if match:
                rows[match[1].lower()] = line
        assert set(rows) == lessons, (suffix, "every lesson needs an evidence/media status")
        for lesson, row in rows.items():
            page = Page(ROOT / f"docs/lessons/{lesson}/index{suffix}.html")
            actual = {Path(source["src"]).name for video in page.videos for source in video["sources"]}
            declared = set(re.findall(r"rendered/([^/)]+\.mp4)", row))
            assert declared == actual, (lesson, suffix, declared, actual)
