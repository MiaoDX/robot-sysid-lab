# Maintaining the bilingual course

Serve the repository with `python -m http.server 2720 --bind 0.0.0.0` and open
`/docs/course/index.html` or `/docs/course/index.zh-CN.html`. The right-hand
language links lead to the same page in the other language. They preserve the
current section and reading position, remember the selected language, and add
an explicit `?lang=en` or `?lang=zh-CN` to shared links. Static navigation also
works without JavaScript; storage restrictions only disable preference memory.

The course homepage is hand-authored paired HTML. Its styles are shared across
languages. Lessons K0, K1, L0, and L1 use paired `index.md` sources; the builder
adds matching section IDs and previous/next navigation. Lessons, supplementary
notes, reports, and project resources are generated from paired Markdown
(`name.md` and `name.zh-CN.md`):

```bash
python -m pip install -r requirements-docs.txt
python tools/build_course.py
python tools/build_course.py --check
python -m pytest -q tests/test_course_site.py
```

Commit the generated HTML so serving the site requires no build step. Edit
Markdown, not the generated HTML. Keep heading order, equations, units, and
numerical evidence aligned. The builder gives translations the English heading
IDs so deep links and language changes land on corresponding sections. It
rewrites links to paired notes and reports into same-language HTML.

The original report data, plots, and video footage remain shared evidence.
Chinese report prose explains the plotted English labels. Each video has an
English and Chinese WebVTT explanation track, selected by page language, and a
written explanation beneath it. `architecture.zh-CN.svg` translates the course
diagram without changing its information flow. Python apps, notebooks, raw
metrics, and engineering verification records are downloadable research
artifacts; they are not generated reading pages.

KaTeX 0.16.22 is vendored from the npm `katex` package under `vendor/katex`,
including its MIT license and WOFF2 fonts. No CDN or remote translation service
is required while reading. `math.js` renders authored TeX with trusted commands
disabled. Documentation build dependencies are separate from the numerical
lab dependencies.

## Writing for learners

The homepage explains the value of identification and recommends K0 → K1 → L0.
Keep one primary start action. Available courses have complete reading pages;
future courses show a learning objective and a clear “Coming later” / “准备中”
status without a placeholder body link. Project plans and delivery records live
behind the project-resources link.

Write complete, connected explanations that sound natural when read silently.
Use concrete experiments to introduce terms. Avoid explaining naming or
implementation choices unless they help the learner. Omit unnecessary terminal
periods in headings; keep question marks when the heading asks a question.
English and Chinese share structure, concepts, equations, data, and conclusions;
their sentence structure should be natural in each language.

Each lesson is one continuous page: question, system, physical intuition,
experiment, evidence, exercise, and limits. Put videos next to the question they
answer and include validation evidence on the page. Local execution is optional.
Supplementary notes support deeper reading; they are not required to complete
the main explanation. Use explicit heading IDs with `{#section}` to preserve
shared links as wording changes. Preserve the original clip and report assets.
