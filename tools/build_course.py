"""Render paired course notes as static HTML. Run from the repository root."""
from __future__ import annotations

import argparse
import hashlib
import html
import os
import re
import struct
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "toc", "sane_lists", "md_in_html", "attr_list"]
LESSON_ORDER = ("k0", "k1", "l0", "l1")


def relative(path: Path, page: Path) -> str:
    return Path(os.path.relpath(path, page.parent)).as_posix()


def render(source: Path, pairs: dict[Path, Path]) -> str:
    chinese = ".zh-CN." in source.name
    lang = "zh-CN" if chinese else "en"
    page = source.with_suffix(".html")
    suffix = ".zh-CN" if chinese else ""
    peer = pairs[source].with_suffix(".html")
    text = source.read_text()
    # Preserve TeX delimiters through Markdown; KaTeX renders them locally.
    text = text.replace("\\[", "$$").replace("\\]", "$$")
    soup = BeautifulSoup(markdown.markdown(text, extensions=MARKDOWN_EXTENSIONS), "html.parser")
    # Both translations get the English heading IDs, so hash links survive switching.
    english_source = pairs[source] if chinese else source
    english = BeautifulSoup(markdown.markdown(english_source.read_text(), extensions=MARKDOWN_EXTENSIONS), "html.parser")
    headings = soup.select("h1,h2,h3,h4,h5,h6")
    english_headings = english.select("h1,h2,h3,h4,h5,h6")
    if len(headings) != len(english_headings):
        raise ValueError(f"Heading count differs: {source.relative_to(ROOT)} ({len(headings)} vs {len(english_headings)})")
    for heading, original in zip(headings, english_headings):
        heading["id"] = original["id"]
    for tag in soup.select("a[href],img[src]"):
        attr = "href" if tag.name == "a" else "src"
        url = urlsplit(tag[attr])
        if url.scheme or url.netloc or not url.path:
            continue
        target = (source.parent / unquote(url.path)).resolve()
        if target in pairs:
            explicit_language_link = bool(re.fullmatch(r"English(?: version)?|英文版?|中文(?:版)?", tag.get_text(strip=True)))
            translated = target if explicit_language_link or (".zh-CN." in target.name) == chinese else pairs[target]
            tag[attr] = urlunsplit(("", "", relative(translated.with_suffix(".html"), page), url.query, url.fragment))
            if explicit_language_link:
                tag["hreflang"] = "zh-CN" if ".zh-CN." in translated.name else "en"
        elif tag.name == "a" and target.suffix == ".html":
            canonical = target.name.replace(".zh-CN.html", ".html")
            localized = target.with_name(canonical.replace(".html", suffix + ".html"))
            if localized.exists():
                tag[attr] = urlunsplit(("", "", relative(localized, page), url.query, url.fragment))
        elif tag.name == "img":
            localized = target.with_name(target.stem + ".zh-CN" + target.suffix)
            if chinese and localized.exists():
                tag[attr] = relative(localized, page)
    for table in soup.select("table"):
        wrapper = soup.new_tag("div", attrs={"class": "table-scroll", "tabindex": "0", "role": "region", "aria-label": "数据表格" if chinese else "Data table"})
        table.wrap(wrapper)
    for image in soup.select("img"):
        image["loading"] = "lazy"
        image_path = (source.parent / urlsplit(image["src"]).path).resolve()
        if image_path.suffix == ".png" and image_path.exists():
            with image_path.open("rb") as handle:
                header = handle.read(24)
            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                image["width"], image["height"] = map(str, struct.unpack(">II", header[16:24]))
    title = headings[0].get_text() if headings else source.stem
    toc = "".join(f'<a href="#{h["id"]}">{html.escape(h.get_text())}</a>' for h in soup.select("h2"))
    course = relative(ROOT / f"docs/course/index{suffix}.html", page)
    start = relative(ROOT / f"docs/lessons/k0/index{suffix}.html", page)
    context = ""
    progression = ""
    lesson = source.parent.name
    if source.parent.parent == ROOT / "docs/lessons" and lesson in LESSON_ORDER:
        if source.name.startswith("index."):
            neighbors = []
            index = LESSON_ORDER.index(lesson)
            for relation, offset, label in (("prev", -1, "上一课" if chinese else "Previous"), ("next", 1, "下一课" if chinese else "Next")):
                if 0 <= index + offset < len(LESSON_ORDER):
                    neighbor = LESSON_ORDER[index + offset]
                    href = f"../{neighbor}/index{suffix}.html"
                    neighbors.append(f'<a rel="{relation}" href="{href}">{label} · {neighbor.upper()}</a>')
            neighbors.insert(1 if index else 0, f'<a href="{course}#tracks">{"课程目录" if chinese else "All lessons"}</a>')
            progression = '<nav class="lesson-nav" aria-label="' + ("课程顺序" if chinese else "Lesson sequence") + '">' + "".join(neighbors) + '</nav>'
        else:
            label = f"返回 {lesson.upper()} 完整课程" if chinese else f"Read the full {lesson.upper()} lesson"
            context = f'<p class="article-context"><a href="index{suffix}.html">{label}</a></p>'
    css = relative(ROOT / "docs/site/reading.css", page)
    shared_css = relative(ROOT / "docs/site/site.css", page)
    script = relative(ROOT / "docs/site/language.js", page)
    katex = relative(ROOT / "docs/site/vendor/katex/katex.min.css", page)
    katex_js = relative(ROOT / "docs/site/vendor/katex/katex.min.js", page)
    math_js = relative(ROOT / "docs/site/math.js", page)
    en_url, zh_url = (relative(peer, page), page.name) if chinese else (page.name, relative(peer, page))
    labels = ("课程地图", "本页内容", "课程导航", "语言", "返回课程") if chinese else ("Course map", "On this page", "Course navigation", "Language", "Back to course")
    digest = hashlib.sha256(text.encode()).hexdigest()[:12]
    body_class = f' class="reading-page lesson-{lesson}"' if source.parent.parent == ROOT / "docs/lessons" else ""
    return f'''<!doctype html>
<!-- Generated by tools/build_course.py from {source.relative_to(ROOT)} ({digest}). -->
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · Robot SysID Lab</title>
<link rel="stylesheet" href="{css}"><link rel="stylesheet" href="{shared_css}"><link rel="stylesheet" href="{katex}">
<script defer src="{katex_js}"></script><script defer src="{math_js}"></script><script defer src="{script}"></script>
</head><body{body_class}>
<header><div class="shell"><a class="brand" href="{course}">Robot SysID Lab</a><div class="header-actions">
<nav aria-label="{labels[2]}"><a href="{course}#tracks">{labels[0]}</a><a href="{start}">{"从头开始" if chinese else "Start here"}</a></nav>
<span class="language-switch" aria-label="{labels[3]}"><a href="{en_url}" lang="en" hreflang="en"{' aria-current="page"' if not chinese else ''}>EN</a><a href="{zh_url}" lang="zh-CN" hreflang="zh-CN"{' aria-current="page"' if chinese else ''}>中文</a></span>
</div></div></header>
<div class="reading-layout shell"><aside><details open><summary>{labels[1]}</summary>{toc}</details></aside><main id="content">{context}{soup}{progression}</main></div>
<footer class="shell"><a href="{course}">{labels[4]}</a><a href="{source.name}" download>Markdown</a></footer>
</body></html>
'''


def build(check: bool = False) -> int:
    pairs = {}
    for directory in (ROOT / "docs", ROOT / "reports"):
        for zh in sorted(directory.rglob("*.zh-CN.md")):
            en = zh.with_name(zh.name.replace(".zh-CN.md", ".md"))
            if not en.exists():
                raise ValueError(f"Missing English source: {en}")
            pairs[en] = zh
            pairs[zh] = en
    stale = []
    for source in pairs:
        output = source.with_suffix(".html")
        content = render(source, pairs)
        if check:
            if not output.exists() or output.read_text() != content:
                stale.append(output.relative_to(ROOT).as_posix())
        else:
            output.write_text(content)
    if stale:
        raise SystemExit("Rebuild course pages: " + ", ".join(stale))
    print(f"{'Checked' if check else 'Rendered'} {len(pairs)} bilingual document pages.")
    return len(pairs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    build(parser.parse_args().check)
