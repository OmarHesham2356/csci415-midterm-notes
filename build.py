#!/usr/bin/env python3
"""
Build a static, Netlify-ready copy of CSCI415_Midterm_Master_Notes.md.

What it fixes compared with the old web_export/index.html:
  * real Markdown tables (old export printed raw "| a | b |" lines)
  * correct inline-code tags (old export emitted </code>text<code>)
  * valid block nesting (no <p><div class="mcq-quiz">)
  * working MCQ quizzes (old JS wiped the DOM with body.innerHTML = ...)
  * TikZ diagrams pre-rendered to SVG with Tectonic + pdftocairo
  * Obsidian callouts, wikilinks, task lists
  * KaTeX math, Chart.js chart, and the GenUI blocks

Usage:
    .venv/bin/python build.py            # rebuild web_export/
    python3 -m http.server -d web_export 8080
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "CSCI415_Midterm_Master_Notes.md"
OUT = ROOT / "web_export"
DIAGRAMS = OUT / "diagrams"
CACHE = DIAGRAMS / ".cache.json"

MD_EXTENSIONS = ["extra", "sane_lists", "toc"]

# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

_MATH_RE = re.compile(r"\$\$(.+?)\$\$|(?<!\$)\$(?!\$)([^\n$]+?)\$(?!\$)", re.S)


_LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")


def ensure_list_spacing(text: str) -> str:
    """Obsidian lets a list follow a paragraph directly; Python-Markdown does not."""
    out: list[str] = []
    for line in text.split("\n"):
        prev = out[-1] if out else ""
        if (
            _LIST_RE.match(line)
            and prev.strip()
            and not _LIST_RE.match(prev)
            and not prev.lstrip().startswith((">", "|", "#", "<", "```"))
        ):
            out.append("")
        out.append(line)
    return "\n".join(out)


def md_convert(text: str) -> str:
    """Convert a Markdown fragment, protecting math and wikilinks first."""
    text = ensure_list_spacing(text)
    math_store: list[str] = []
    wiki_store: list[tuple[str, str]] = []

    def keep_math(m: re.Match) -> str:
        math_store.append(m.group(0))
        return f"@@MATH{len(math_store) - 1}@@"

    text = _MATH_RE.sub(keep_math, text)

    def keep_wiki(m: re.Match) -> str:
        target, _, label = m.group(1).partition("|")
        heading = target.lstrip("#")
        label = label or heading
        # The Contents list is an <ol> whose labels repeat the heading's "1." prefix.
        num = re.match(r"^(\d+)\.\s+(.*)$", label)
        if num and heading.startswith(num.group(1) + ". "):
            label = num.group(2)
        slug = HEADING_SLUGS.get(heading, slugify(heading, "-"))
        wiki_store.append((slug, label))
        return f"@@WIKI{len(wiki_store) - 1}@@"

    text = re.sub(r"\[\[([^\]]+)\]\]", keep_wiki, text)

    out = markdown.markdown(text, extensions=MD_EXTENSIONS)

    for i, raw in enumerate(math_store):
        out = out.replace(f"@@MATH{i}@@", raw)
    for i, (slug, label) in enumerate(wiki_store):
        out = out.replace(
            f"@@WIKI{i}@@", f'<a class="wikilink" href="#{html.escape(slug)}">{html.escape(label)}</a>'
        )
    return out


def inline_md(text: str) -> str:
    """Markdown for a single line (question, option, title)."""
    out = md_convert(text).strip()
    m = re.fullmatch(r"<p>(.*)</p>", out, re.S)
    return m.group(1) if m else out


def esc(text: str) -> str:
    return html.escape(text, quote=False)


# ---------------------------------------------------------------------------
# Sidebar table of contents
# ---------------------------------------------------------------------------

_HEADING_TAG_RE = re.compile(r'<h([1-3]) id="([^"]+)">(.*?)</h\1>', re.S)


def build_toc(body: str) -> str:
    """Build the left navigation tree from the rendered h1/h2/h3 headings."""
    entries: list[tuple[int, str, str]] = []
    for m in _HEADING_TAG_RE.finditer(body):
        level, hid, inner = int(m.group(1)), m.group(2), m.group(3)
        if hid == "contents":  # the body already has a Contents section
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", inner))
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            entries.append((level, hid, text))

    out = ['<ul class="toc-root">']
    open_group = False
    first_h1 = True
    for level, hid, text in entries:
        if level == 1:
            if open_group:
                out.append("</ul></li>")
            label = "Overview" if first_h1 else text
            first_h1 = False
            out.append(
                f'<li class="toc-h1"><div class="toc-row">'
                f'<a href="#{hid}">{html.escape(label)}</a>'
                f'<button class="toc-caret" type="button" aria-label="Toggle section" '
                f'aria-expanded="false">▸</button></div>'
                f'<ul class="toc-children">'
            )
            open_group = True
        elif level == 2:
            out.append(f'<li class="toc-h2"><a href="#{hid}">{html.escape(text)}</a></li>')
        else:
            out.append(f'<li class="toc-h3"><a href="#{hid}">{html.escape(text)}</a></li>')
    if open_group:
        out.append("</ul></li>")
    out.append("</ul>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# TikZ -> SVG
# ---------------------------------------------------------------------------

TIKZ_RE = re.compile(r"^```tikz[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
LIB_RE = re.compile(r"\\usetikzlibrary\{[^}]*\}")


def find_tectonic() -> str | None:
    candidates = [os.environ.get("TECTONIC"), "/tmp/opencode/tectonic", shutil.which("tectonic")]
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def build_tex(code: str) -> str:
    libs = "\n".join(dict.fromkeys(LIB_RE.findall(code)))
    body = LIB_RE.sub("", code)
    body = body.replace("\\begin{document}", "").replace("\\end{document}", "")
    return (
        "\\documentclass[border=4pt]{standalone}\n"
        "\\usepackage{tikz}\n"
        "\\usepackage{amsmath,amssymb}\n"
        f"{libs}\n"
        "\\begin{document}\n"
        f"{body}\n"
        "\\end{document}\n"
    )


def render_tikz(code: str, index: int, tectonic: str | None) -> str:
    """Return HTML for one TikZ block. Emits a cached SVG when possible."""
    DIAGRAMS.mkdir(parents=True, exist_ok=True)
    stem = f"diagram-{index:02d}"
    svg = DIAGRAMS / f"{stem}.svg"
    tex = DIAGRAMS / f"{stem}.tex"
    pdf = DIAGRAMS / f"{stem}.pdf"
    digest = hashlib.sha256(build_tex(code).encode()).hexdigest()

    cache: dict[str, str] = {}
    if CACHE.exists():
        try:
            cache = json.loads(CACHE.read_text())
        except Exception:
            cache = {}

    fresh = cache.get(stem) == digest and svg.exists()
    if not fresh and tectonic:
        tex.write_text(build_tex(code), encoding="utf-8")
        proc = subprocess.run(
            [tectonic, "-X", "compile", "--outdir", str(DIAGRAMS), str(tex)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(f"  ! TikZ {stem} failed:\n{proc.stderr[-800:]}", file=sys.stderr)
        elif pdf.exists():
            conv = subprocess.run(
                ["pdftocairo", "-svg", str(pdf), str(svg)], capture_output=True, text=True
            )
            if conv.returncode != 0:
                print(f"  ! SVG {stem} failed: {conv.stderr[-400:]}", file=sys.stderr)
            else:
                cache[stem] = digest
                pdf.unlink(missing_ok=True)
                tex.unlink(missing_ok=True)
                print(f"  · rendered {stem}")

    CACHE.write_text(json.dumps(cache, indent=2))

    if svg.exists():
        return (
            '<figure class="tikz-card">'
            f'<img src="diagrams/{stem}.svg" alt="TikZ diagram {index}" loading="lazy">'
            "</figure>"
        )
    # graceful fallback: show the source instead of a cryptic error
    return (
        '<details class="tikz-fallback"><summary>Diagram source (run with Tectonic to render)</summary>'
        f"<pre><code>{esc(code)}</code></pre></details>"
    )


# ---------------------------------------------------------------------------
# GenUI blocks
# ---------------------------------------------------------------------------

QUIZZES: list[dict] = []
CHARTS: list[dict] = []


def build_quiz(raw: str) -> str:
    data = json.loads(raw)
    quiz = {
        "title": data.get("title", "Quiz"),
        "questions": [
            {
                "q": inline_md(q["q"]),
                "options": [inline_md(o) for o in q["options"]],
                "answer": int(q["answer"]),
                "explain": md_convert(q.get("explain", "")),
            }
            for q in data["questions"]
        ],
    }
    idx = len(QUIZZES)
    QUIZZES.append(quiz)
    return f"""
<section class="mcq-quiz" data-quiz-index="{idx}">
  <h3 id="quiz-{idx}">{esc(quiz['title'])}</h3>
  <div class="quiz-progress">Question <span class="q-num">1</span> of {len(quiz['questions'])}</div>
  <div class="quiz-question"></div>
  <div class="quiz-options"></div>
  <div class="quiz-feedback"></div>
  <div class="quiz-controls">
    <button class="btn-prev" type="button" disabled>Previous</button>
    <button class="btn-next" type="button">Next</button>
    <button class="btn-check" type="button">Check Answer</button>
    <button class="btn-reset" type="button" style="display:none">Reset</button>
  </div>
  <div class="quiz-score" style="display:none"></div>
</section>"""


def build_chart(raw: str) -> str:
    m = re.search(r"content=(\{.*\})", raw, re.S)
    if not m:
        return f'<pre class="chart-source">{esc(raw)}</pre>'
    payload = m.group(1)
    # JSX wraps the JSON object in an extra pair of braces: content={{...}}
    if payload.startswith("{{") and payload.endswith("}}"):
        payload = payload[1:-1]
    cfg = json.loads(payload)
    idx = len(CHARTS)
    CHARTS.append(cfg)
    title = esc(cfg.get("title", ""))
    footer = esc((cfg.get("meta") or {}).get("footer", ""))
    return f"""
<figure class="chart-card">
  <figcaption class="chart-title">{title}</figcaption>
  <div class="chart-wrap"><canvas id="chart-{idx}"></canvas></div>
  {f'<div class="chart-footer">{footer}</div>' if footer else ''}
</figure>"""


def build_genui(raw: str) -> str:
    try:
        data = json.loads(raw)
    except Exception:
        return f'<pre class="genui-source">{esc(raw)}</pre>'
    auto = data.get("suggest_automation")
    if auto:
        label = esc(auto.get("label", "Suggested automation"))
        return f'<aside class="callout callout-tip genui-tip"><div class="callout-title">Suggested automation</div><div class="callout-body"><p>{label}</p></div></aside>'
    return f'<pre class="genui-source">{esc(raw)}</pre>'


# ---------------------------------------------------------------------------
# callouts
# ---------------------------------------------------------------------------

CALLOUT_RE = re.compile(r"^>\s*\[!(\w+)\]([-+]?)\s*(.*)$")


def convert_callouts(text: str) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        m = CALLOUT_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        kind, fold, title = m.group(1).lower(), m.group(2), m.group(3).strip()
        body: list[str] = []
        i += 1
        while i < len(lines) and lines[i].lstrip().startswith(">"):
            line = lines[i].lstrip()[1:]
            if line.startswith(" "):
                line = line[1:]
            body.append(line)
            i += 1
        body_html = md_convert("\n".join(body))
        title_html = inline_md(title) if title else kind.capitalize()
        cls = f"callout callout-{kind}"
        if fold:
            open_attr = " open" if fold == "+" else ""
            out.append(
                f'<details class="{cls} collapsible"{open_attr}><summary class="callout-title">{title_html}</summary>'
                f'<div class="callout-body">{body_html}</div></details>'
            )
        else:
            out.append(
                f'<div class="{cls}"><div class="callout-title">{title_html}</div>'
                f'<div class="callout-body">{body_html}</div></div>'
            )
    return "\n".join(out)


# ---------------------------------------------------------------------------
# main build
# ---------------------------------------------------------------------------

HEADING_SLUGS: dict[str, str] = {}
FRONT: dict[str, str] = {}


def load_source() -> str:
    raw = SRC.read_text(encoding="utf-8")
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        for line in fm.strip().splitlines():
            if ":" in line and not line.startswith((" ", "\t", "-")):
                k, v = line.split(":", 1)
                FRONT[k.strip()] = v.strip().strip('"').strip("'")
        raw = body.lstrip("\n")
    return raw


def extract_blocks(raw: str, tectonic: str | None) -> tuple[str, dict[str, str]]:
    """Replace fenced blocks with placeholders. Returns (text, placeholder->html)."""
    placeholders: dict[str, str] = {}
    parts: list[str] = []
    pos = 0
    pattern = re.compile(r"^```([A-Za-z0-9_-]*)[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)

    for n, m in enumerate(pattern.finditer(raw)):
        parts.append(raw[pos : m.start()])
        lang, code = m.group(1).lower(), m.group(2)
        key = f"@@BLOCK{n}@@"

        if lang == "tikz":
            rendered = render_tikz(code, n + 1, tectonic)
        elif lang == "mcq-quiz":
            rendered = build_quiz(code)
        elif lang == "chatgpt-jsx":
            rendered = build_chart(code)
        elif lang == "chatgpt-ui":
            rendered = build_genui(code)
        else:
            language = {"text": "plaintext", "bnf": "plaintext"}.get(lang, lang or "plaintext")
            rendered = (
                f'<pre class="code-block"><code class="language-{language}">{esc(code)}</code></pre>'
            )

        placeholders[key] = rendered
        parts.append(f"\n\n{key}\n\n")
        pos = m.end()

    parts.append(raw[pos:])
    return "".join(parts), placeholders


def build() -> None:
    raw = load_source()

    # heading -> anchor map (must exist before md_convert resolves wikilinks)
    for line in raw.splitlines():
        hm = re.match(r"^(#{1,6})\s+(.*)$", line)
        if hm:
            text = re.sub(r"[`*_]", "", hm.group(2)).strip()
            HEADING_SLUGS[text] = slugify(text, "-")

    tectonic = find_tectonic()
    print(f"Tectonic: {tectonic or 'NOT FOUND (using cached SVGs only)'}")

    text, placeholders = extract_blocks(raw, tectonic)
    text = convert_callouts(text)
    body = md_convert(text)
    # Obsidian uses \| inside table cells; Python-Markdown keeps the backslash.
    body = body.replace("\\|", "|")

    for key, value in placeholders.items():
        body = body.replace(f"<p>{key}</p>", value).replace(key, value)

    # wrap tables so wide tables scroll instead of overflowing
    body = re.sub(r"<table>(.*?)</table>", r'<div class="table-wrap"><table>\1</table></div>', body, flags=re.S)
    # Obsidian task lists
    body = body.replace("<li>[ ] ", '<li class="task"><input type="checkbox" disabled> ')
    body = body.replace("<li>[x] ", '<li class="task"><input type="checkbox" checked disabled> ')
    body = body.replace("<li>[X] ", '<li class="task"><input type="checkbox" checked disabled> ')

    page = TEMPLATE.format(
        title=esc(FRONT.get("title", "CSCI415 Midterm Master Notes")),
        toc=build_toc(body),
        body=body,
        quiz_json=json.dumps(QUIZZES, ensure_ascii=False).replace("</", "<\\/"),
        chart_json=json.dumps(CHARTS, ensure_ascii=False).replace("</", "<\\/"),
    )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "netlify.toml").write_text(
        '[build]\n  publish = "."\n\n[[headers]]\n  for = "/*"\n'
        '  [headers.values]\n    X-Content-Type-Options = "nosniff"\n',
        encoding="utf-8",
    )
    print(f"Wrote {OUT / 'index.html'} ({len(page):,} bytes), {len(QUIZZES)} quizzes, "
          f"{len(CHARTS)} charts, {len(list(DIAGRAMS.glob('*.svg')))} diagrams")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.9.0/styles/github-dark.min.css">
<style>
:root {{
  --bg-primary:#1e1e1e; --bg-secondary:#252526; --bg-tertiary:#2d2d2d;
  --text-primary:#d4d4d4; --text-secondary:#a8a8a8; --text-muted:#7a7a7a;
  --accent:#4da3ff; --accent-hover:#7ab8ff; --border:#3c3c3c;
  --callout-bg:#2d2d2d; --callout-border:#3c3c3c;
  --warning-bg:#3a2d0a; --warning-border:#8a6914; --warning-text:#ffcc66;
  --important-bg:#16283a; --important-border:#2a6a9a; --important-text:#6fc3e0;
  --danger-bg:#3a1a1a; --danger-border:#a33; --danger-text:#ff7b72;
  --success-bg:#173a1f; --success-border:#2e8b45; --success-text:#7ee787;
  --code-bg:#161616; --sidebar-width:300px;
}}
@media (prefers-color-scheme: light) {{
  :root {{
    --bg-primary:#fff; --bg-secondary:#f6f6f6; --bg-tertiary:#ececec;
    --text-primary:#1f2328; --text-secondary:#4a4a4a; --text-muted:#777;
    --accent:#0969da; --accent-hover:#0550ae; --border:#d8d8d8;
    --callout-bg:#f6f6f6; --callout-border:#d8d8d8;
    --warning-bg:#fff8e1; --warning-border:#e0a800; --warning-text:#7a5a00;
    --important-bg:#e8f2fb; --important-border:#4a90c2; --important-text:#0b4f7a;
    --danger-bg:#fdecec; --danger-border:#d9534f; --danger-text:#a12b2b;
    --success-bg:#eaf7ec; --success-border:#3c9a55; --success-text:#1d6b32;
    --code-bg:#f3f3f3;
  }}
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; scroll-padding-top:1rem; }}
body {{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  margin:0; padding:0; line-height:1.7;
  color:var(--text-primary); background:var(--bg-primary);
  -webkit-font-smoothing:antialiased;
}}
.page {{ margin-left:var(--sidebar-width); }}
main {{ max-width:980px; margin:0 auto; padding:2rem 1.25rem 6rem; }}
h1,h2,h3,h4,h5,h6 {{ color:var(--text-primary); font-weight:650; line-height:1.3; scroll-margin-top:1rem; }}
h1 {{ border-bottom:1px solid var(--border); padding-bottom:.5rem; margin-top:0; font-size:2rem; }}
h2 {{ border-bottom:1px solid var(--border); padding-bottom:.3rem; margin-top:3rem; font-size:1.5rem; }}
h3 {{ margin-top:2rem; font-size:1.2rem; }}
h4 {{ margin-top:1.5rem; }}
p {{ margin:.75rem 0; }}
a {{ color:var(--accent); text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
a.wikilink {{ border-bottom:1px dashed var(--accent); }}
hr {{ border:none; border-top:1px solid var(--border); margin:2.5rem 0; }}
ul,ol {{ padding-left:1.6rem; }}
li {{ margin:.3rem 0; }}
li.task {{ list-style:none; margin-left:-1.2rem; }}
li.task input {{ margin-right:.5rem; accent-color:var(--success-border); }}
blockquote {{
  border-left:4px solid var(--accent); padding:.4rem 1rem; margin:1rem 0;
  color:var(--text-secondary); background:var(--bg-secondary); border-radius:0 6px 6px 0;
}}
code {{
  background:var(--code-bg); padding:.12rem .35rem; border-radius:4px;
  font-family:"JetBrains Mono","Fira Code",Consolas,monospace; font-size:.9em;
  border:1px solid var(--border);
}}
pre {{
  background:#161616; color:#d4d4d4; padding:1rem; border-radius:8px;
  overflow-x:auto; border:1px solid var(--border); line-height:1.5;
}}
pre code {{ background:none; padding:0; border:none; font-size:.86rem; }}
.table-wrap {{ overflow-x:auto; margin:1.1rem 0; border-radius:8px; border:1px solid var(--border); }}
table {{ border-collapse:collapse; width:100%; font-size:.9rem; min-width:max-content; }}
th,td {{ border:1px solid var(--border); padding:.5rem .7rem; text-align:left; vertical-align:top; }}
th {{ background:var(--bg-tertiary); font-weight:650; white-space:nowrap; }}
tbody tr:nth-child(even) {{ background:var(--bg-secondary); }}
.callout {{ padding:1rem 1.25rem; border-radius:8px; margin:1.1rem 0; border-left:4px solid var(--callout-border); background:var(--callout-bg); }}
.callout-title {{ font-weight:650; margin-bottom:.4rem; display:flex; gap:.5rem; align-items:center; }}
details.callout > summary {{ cursor:pointer; margin-bottom:0; list-style:none; }}
details.callout > summary::-webkit-details-marker {{ display:none; }}
details.callout > summary::before {{ content:"▸"; display:inline-block; transition:transform .15s; }}
details.callout[open] > summary::before {{ transform:rotate(90deg); }}
.callout-body > :first-child {{ margin-top:0; }}
.callout-body > :last-child {{ margin-bottom:0; }}
.callout-warning,.callout-example {{ background:var(--warning-bg); border-color:var(--warning-border); }}
.callout-warning .callout-title,.callout-example .callout-title {{ color:var(--warning-text); }}
.callout-important,.callout-tip,.callout-info {{ background:var(--important-bg); border-color:var(--important-border); }}
.callout-important .callout-title,.callout-tip .callout-title,.callout-info .callout-title {{ color:var(--important-text); }}
.callout-danger {{ background:var(--danger-bg); border-color:var(--danger-border); }}
.callout-danger .callout-title {{ color:var(--danger-text); }}
.callout-success,.callout-summary {{ background:var(--success-bg); border-color:var(--success-border); }}
.callout-success .callout-title,.callout-summary .callout-title {{ color:var(--success-text); }}
.callout-note {{ background:var(--callout-bg); border-color:var(--callout-border); }}
.tikz-card {{ margin:1.5rem 0; text-align:center; background:#fff; border:1px solid var(--border); border-radius:10px; padding:1rem; overflow-x:auto; }}
.tikz-card img {{ max-width:100%; height:auto; }}
.tikz-fallback {{ margin:1rem 0; }}
.chart-card {{ margin:1.5rem 0; background:var(--bg-secondary); border:1px solid var(--border); border-radius:10px; padding:1rem; }}
.chart-title {{ font-weight:650; text-align:center; margin-bottom:.5rem; }}
.chart-wrap {{ position:relative; height:340px; }}
.chart-footer {{ color:var(--text-muted); font-size:.85rem; text-align:center; margin-top:.6rem; }}
.genui-tip {{ margin:1rem 0; }}
.mcq-quiz {{ background:var(--bg-secondary); border:1px solid var(--border); border-radius:10px; padding:1.5rem; margin:1.75rem 0; }}
.mcq-quiz h3 {{ margin-top:0; color:var(--accent); }}
.quiz-progress {{ color:var(--text-muted); font-size:.9rem; margin-bottom:1rem; }}
.quiz-question {{ font-size:1.08rem; font-weight:550; margin-bottom:1rem; }}
.quiz-question p {{ margin:0; }}
.quiz-options {{ display:flex; flex-direction:column; gap:.55rem; }}
.quiz-option {{ padding:.75rem 1rem; border:2px solid var(--border); border-radius:8px; cursor:pointer; background:var(--bg-tertiary); transition:border-color .15s,background .15s; }}
.quiz-option p {{ margin:0; }}
.quiz-option:hover {{ border-color:var(--accent); }}
.quiz-option.selected {{ border-color:var(--accent); background:color-mix(in srgb,var(--accent) 18%,var(--bg-tertiary)); }}
.quiz-option.correct {{ border-color:var(--success-border); background:var(--success-bg); }}
.quiz-option.incorrect {{ border-color:var(--danger-border); background:var(--danger-bg); }}
.quiz-option.disabled {{ cursor:not-allowed; opacity:.65; }}
.quiz-feedback {{ margin-top:1rem; padding:1rem; border-radius:8px; display:none; line-height:1.6; }}
.quiz-feedback.show {{ display:block; }}
.quiz-feedback.correct {{ background:var(--success-bg); border:1px solid var(--success-border); }}
.quiz-feedback.incorrect {{ background:var(--danger-bg); border:1px solid var(--danger-border); }}
.quiz-feedback ul {{ margin:.4rem 0; }}
.quiz-controls {{ display:flex; gap:.5rem; margin-top:1.4rem; flex-wrap:wrap; }}
.mcq-quiz button {{ padding:.5rem 1rem; border:none; border-radius:6px; font-weight:600; cursor:pointer; font-size:.9rem; }}
.mcq-quiz button:disabled {{ opacity:.45; cursor:not-allowed; }}
.btn-next {{ background:var(--accent); color:#fff; }}
.btn-prev {{ background:var(--bg-tertiary); color:var(--text-primary); border:1px solid var(--border); }}
.btn-check {{ background:var(--success-border); color:#fff; }}
.btn-reset {{ background:var(--warning-border); color:#1a1a1a; }}
.quiz-score {{ margin-top:1.4rem; padding:1rem; background:var(--bg-tertiary); border:1px solid var(--border); border-radius:8px; text-align:center; font-weight:650; color:var(--accent); }}
.katex {{ font-size:1em !important; }}
.katex-display {{ overflow-x:auto; overflow-y:hidden; padding:.2rem 0; }}
/* Sidebar navigation */
.sidebar {{
  position:fixed; top:0; left:0; bottom:0; width:var(--sidebar-width);
  display:flex; flex-direction:column; z-index:60;
  background:var(--bg-secondary); border-right:1px solid var(--border);
  transition:transform .22s ease;
}}
.sidebar-header {{ display:flex; align-items:center; justify-content:space-between; gap:.5rem; padding:.9rem 1rem; border-bottom:1px solid var(--border); }}
.sidebar-title {{ font-weight:700; font-size:.95rem; letter-spacing:.01em; }}
.sidebar-close {{ display:none; border:none; background:transparent; color:var(--text-secondary); font-size:1.5rem; line-height:1; cursor:pointer; padding:.1rem .3rem; }}
.sidebar-collapse {{ display:flex; align-items:center; justify-content:center; width:2rem; height:2rem; border:none; background:var(--bg-tertiary); color:var(--text-secondary); border-radius:6px; cursor:pointer; font-size:1rem; line-height:1; transition:background .15s, color .15s; }}
.sidebar-collapse:hover {{ background:var(--accent); color:#fff; }}
/* Collapsed sidebar state (desktop) — keep a narrow tab with the expand button */
body.sidebar-collapsed .sidebar {{ width:44px; border-right:1px solid var(--border); }}
body.sidebar-collapsed .page {{ margin-left:44px; }}
body.sidebar-collapsed .sidebar-toggle {{ display:none; }}
body.sidebar-collapsed .sidebar-resize {{ display:none; }}
body.sidebar-collapsed .sidebar-title {{ display:none; }}
body.sidebar-collapsed .toc-filter {{ display:none; }}
body.sidebar-collapsed .toc {{ display:none; }}
body.sidebar-collapsed .sidebar-close {{ display:none; }}
body.sidebar-collapsed .sidebar-header {{ padding:.9rem 0; justify-content:center; }}
body.sidebar-collapsed .sidebar-collapse {{ display:flex; }}
.toc-filter {{ margin:.7rem .8rem .4rem; padding:.5rem .65rem; border:1px solid var(--border); border-radius:6px; background:var(--bg-primary); color:var(--text-primary); font:inherit; font-size:.85rem; }}
.toc-filter:focus {{ outline:2px solid color-mix(in srgb,var(--accent) 45%,transparent); outline-offset:1px; border-color:var(--accent); }}
.toc {{ flex:1; overflow-y:auto; padding:.2rem .55rem 2rem; font-size:.84rem; scrollbar-width:thin; }}
.toc ul {{ list-style:none; margin:0; padding:0; }}
.toc-root > .toc-h1 {{ margin:.1rem 0; }}
.toc-row {{ display:flex; align-items:center; gap:.15rem; }}
.toc-row > a {{ flex:1; }}
.toc-caret {{ flex:none; width:1.4rem; height:1.4rem; border:none; background:transparent; color:var(--text-muted); cursor:pointer; font-size:.75rem; line-height:1; border-radius:4px; transition:transform .15s, background .15s; }}
.toc-caret:hover {{ background:var(--bg-tertiary); color:var(--text-primary); }}
.toc-h1.open > .toc-row .toc-caret {{ transform:rotate(90deg); }}
.toc-children {{ display:none; }}
.toc-h1.open > .toc-children {{ display:block; }}
.toc a {{ display:block; padding:.32rem .5rem; border-radius:5px; color:var(--text-secondary); line-height:1.35; text-decoration:none; }}
.toc a:hover {{ background:var(--bg-tertiary); color:var(--text-primary); }}
.toc a.active {{ background:color-mix(in srgb,var(--accent) 16%,transparent); color:var(--accent); font-weight:650; box-shadow:inset 3px 0 0 var(--accent); }}
.toc-h2 > a {{ padding-left:1rem; }}
.toc-h3 > a {{ padding-left:1.9rem; font-size:.8rem; }}
.sidebar-toggle {{ display:none; position:fixed; top:.8rem; left:.8rem; z-index:70; width:2.6rem; height:2.6rem; align-items:center; justify-content:center; border:1px solid var(--border); border-radius:8px; background:var(--bg-secondary); color:var(--text-primary); font-size:1.25rem; cursor:pointer; box-shadow:0 2px 10px rgba(0,0,0,.25); }}
.sidebar-overlay {{ display:none; position:fixed; inset:0; z-index:55; background:rgba(0,0,0,.5); }}
/* Sidebar resize handle */
.sidebar-resize {{ position:absolute; top:0; right:0; bottom:0; width:6px; cursor:col-resize; background:transparent; transition:background .15s; z-index:1; }}
.sidebar-resize:hover {{ background:color-mix(in srgb,var(--accent) 35%,transparent); }}
.sidebar-resize:active {{ background:var(--accent); }}
::-webkit-scrollbar {{ width:9px; height:9px; }}
::-webkit-scrollbar-track {{ background:var(--bg-primary); }}
::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:4px; }}
::-webkit-scrollbar-thumb:hover {{ background:var(--text-muted); }}
@media (max-width:1100px) {{
  .sidebar {{ width:min(88vw,320px); transform:translateX(-100%); box-shadow:0 0 30px rgba(0,0,0,.35); }}
  body.sidebar-open .sidebar {{ transform:none; }}
  .sidebar-toggle {{ display:flex; }}
  body.sidebar-open .sidebar-toggle {{ display:none; }}
  body.sidebar-open .sidebar-overlay {{ display:block; }}
  .sidebar-close {{ display:block; }}
  .page {{ margin-left:0; }}
  body.sidebar-collapsed .sidebar {{ width:min(88vw,320px); transform:translateX(-100%); }}
  body.sidebar-collapsed .sidebar-toggle {{ display:flex; }}
  body.sidebar-collapsed .sidebar-collapse {{ display:none; }}
}}
@media (max-width:640px) {{
  main {{ padding:1rem .9rem 4rem; }}
  .mcq-quiz {{ padding:1rem; }}
  .chart-wrap {{ height:280px; }}
}}
@media print {{
  .sidebar,.sidebar-toggle,.sidebar-overlay {{ display:none !important; }}
  .page {{ margin-left:0; }}
  .quiz-controls,.quiz-feedback {{ display:none !important; }}
  .tikz-card {{ break-inside:avoid; }}
}}
</style>
</head>
<body>
<button id="sidebar-toggle" class="sidebar-toggle" type="button" aria-label="Open navigation" aria-controls="sidebar" aria-expanded="false">☰</button>
<aside id="sidebar" class="sidebar" aria-label="Section navigation">
  <div class="sidebar-header">
    <div class="sidebar-title">CSCI415 Midterm</div>
    <button id="sidebar-collapse" class="sidebar-collapse" type="button" aria-label="Collapse sidebar" aria-expanded="true" title="Collapse sidebar">◀</button>
    <button id="sidebar-close" class="sidebar-close" type="button" aria-label="Close navigation">×</button>
  </div>
  <input id="toc-filter" class="toc-filter" type="search" placeholder="Filter sections…" aria-label="Filter sections">
  <nav id="toc" class="toc">
{toc}
  </nav>
  <div id="sidebar-resize" class="sidebar-resize" role="separator" aria-label="Resize sidebar" tabindex="0" aria-orientation="vertical"></div>
</aside>
<div id="sidebar-overlay" class="sidebar-overlay"></div>
<div class="page">
<main id="content">
{body}
</main>
</div>

<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.9.0/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
window.QUIZZES = {quiz_json};
window.CHARTS = {chart_json};

function renderMathIn(el) {{
  if (!window.renderMathInElement) return;
  renderMathInElement(el, {{
    delimiters: [
      {{left: "$$", right: "$$", display: true}},
      {{left: "\\\\[", right: "\\\\]", display: true}},
      {{left: "$", right: "$", display: false}},
      {{left: "\\\\(", right: "\\\\)", display: false}}
    ],
    throwOnError: false
  }});
}}

document.addEventListener("DOMContentLoaded", function () {{
  if (window.hljs) document.querySelectorAll("pre code").forEach(function (b) {{ hljs.highlightElement(b); }});
  renderMathIn(document.body);

  // ---- sidebar navigation ----
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebarClose = document.getElementById("sidebar-close");
  const sidebarOverlay = document.getElementById("sidebar-overlay");
  const sidebarResize = document.getElementById("sidebar-resize");
  const sidebarCollapse = document.getElementById("sidebar-collapse");
  const toc = document.getElementById("toc");
  const tocFilter = document.getElementById("toc-filter");

  // sidebar collapse/expand (desktop)
  if (sidebarCollapse) {{
    sidebarCollapse.addEventListener("click", function () {{
      const collapsed = document.body.classList.toggle("sidebar-collapsed");
      sidebarCollapse.setAttribute("aria-expanded", collapsed ? "false" : "true");
      sidebarCollapse.setAttribute("aria-label", collapsed ? "Expand sidebar" : "Collapse sidebar");
      sidebarCollapse.textContent = collapsed ? "▶" : "◀";
      sidebarCollapse.title = collapsed ? "Expand sidebar" : "Collapse sidebar";
      localStorage.setItem("sidebar-collapsed", collapsed);
    }});
    // restore collapsed state
    if (localStorage.getItem("sidebar-collapsed") === "true") {{
      document.body.classList.add("sidebar-collapsed");
      sidebarCollapse.setAttribute("aria-expanded", "false");
      sidebarCollapse.setAttribute("aria-label", "Expand sidebar");
      sidebarCollapse.textContent = "▶";
      sidebarCollapse.title = "Expand sidebar";
    }}
  }}

  // sidebar resize (desktop only)
  let resizing = false;
  let startX = 0;
  let startWidth = 0;

  function setSidebarWidth(px) {{
    const minW = 200, maxW = 500;
    px = Math.max(minW, Math.min(maxW, px));
    document.documentElement.style.setProperty("--sidebar-width", px + "px");
    localStorage.setItem("sidebar-width", px);
  }}

  if (sidebarResize) {{
    function onDown(e) {{
      if (window.matchMedia("(max-width: 1100px)").matches) return;
      resizing = true;
      startX = e.clientX;
      const rootStyle = getComputedStyle(document.documentElement);
      startWidth = parseInt(rootStyle.getPropertyValue("--sidebar-width"), 10) || 300;
      document.body.style.userSelect = "none";
      e.preventDefault();
    }}
    function onMove(e) {{
      if (!resizing) return;
      const delta = e.clientX - startX;
      setSidebarWidth(startWidth + delta);
    }}
    function onUp() {{
      resizing = false;
      document.body.style.userSelect = "";
    }}
    sidebarResize.addEventListener("mousedown", onDown);
    sidebarResize.addEventListener("touchstart", onDown, {{ passive: true }});
    document.addEventListener("mousemove", onMove);
    document.addEventListener("touchmove", onMove, {{ passive: true }});
    document.addEventListener("mouseup", onUp);
    document.addEventListener("touchend", onUp);
    // keyboard support
    sidebarResize.addEventListener("keydown", function (e) {{
      if (window.matchMedia("(max-width: 1100px)").matches) return;
      const step = e.shiftKey ? 40 : 10;
      const rootStyle = getComputedStyle(document.documentElement);
      const cur = parseInt(rootStyle.getPropertyValue("--sidebar-width"), 10) || 300;
      if (e.key === "ArrowRight") {{ e.preventDefault(); setSidebarWidth(cur + step); }}
      else if (e.key === "ArrowLeft") {{ e.preventDefault(); setSidebarWidth(cur - step); }}
    }});
    // restore saved width
    const saved = localStorage.getItem("sidebar-width");
    if (saved) setSidebarWidth(parseInt(saved, 10));
  }}

  function setSidebar(open) {{
    document.body.classList.toggle("sidebar-open", open);
    sidebarToggle.setAttribute("aria-expanded", open ? "true" : "false");
  }}
  sidebarToggle.addEventListener("click", function () {{
    setSidebar(!document.body.classList.contains("sidebar-open"));
  }});
  sidebarClose.addEventListener("click", function () {{ setSidebar(false); }});
  sidebarOverlay.addEventListener("click", function () {{ setSidebar(false); }});
  document.addEventListener("keydown", function (e) {{
    if (e.key === "Escape") setSidebar(false);
  }});
  toc.querySelectorAll("a").forEach(function (a) {{
    a.addEventListener("click", function () {{
      if (window.matchMedia("(max-width: 1100px)").matches) setSidebar(false);
    }});
  }});

  // expand / collapse a lecture group
  toc.querySelectorAll(".toc-caret").forEach(function (btn) {{
    btn.addEventListener("click", function (e) {{
      e.preventDefault();
      const group = btn.closest(".toc-h1");
      const open = group.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }});
  }});

  // filter the section list
  if (tocFilter) {{
    tocFilter.addEventListener("input", function () {{
      const q = tocFilter.value.trim().toLowerCase();
      toc.querySelectorAll(".toc-h1").forEach(function (group) {{
        const head = group.querySelector(".toc-row a").textContent.toLowerCase();
        let any = head.includes(q);
        group.querySelectorAll(".toc-h2, .toc-h3").forEach(function (li) {{
          const hit = li.textContent.toLowerCase().includes(q);
          li.style.display = (!q || hit) ? "" : "none";
          if (hit) any = true;
        }});
        group.style.display = (!q || any) ? "" : "none";
        if (q && any) group.classList.add("open");
      }});
      if (!q) {{
        // clearing the filter: collapse everything except the section we are on
        const activeLink = toc.querySelector("a.active");
        const keep = activeLink ? activeLink.closest(".toc-h1") : toc.querySelector(".toc-h1");
        toc.querySelectorAll(".toc-h1").forEach(function (g) {{
          const open = g === keep;
          g.classList.toggle("open", open);
          const c = g.querySelector(".toc-caret");
          if (c) c.setAttribute("aria-expanded", open ? "true" : "false");
        }});
        activeId = null;   // force scrollspy to re-evaluate and re-collapse
        updateActive();
      }}
    }});
  }}

  // scrollspy: highlight the section currently at the top
  const navLinks = new Map();
  toc.querySelectorAll("a[href^='#']").forEach(function (a) {{
    navLinks.set(decodeURIComponent(a.getAttribute("href").slice(1)), a);
  }});
  const headings = Array.from(document.querySelectorAll("main h1[id], main h2[id], main h3[id]"));
  let activeId = null;
  let ticking = false;

  function setActive(id) {{
    if (!id || id === activeId) return;
    activeId = id;
    navLinks.forEach(function (a) {{ a.classList.remove("active"); }});
    const link = navLinks.get(id);
    if (!link) return;
    link.classList.add("active");
    const group = link.closest(".toc-h1");
    if (group) {{
      // keep the tree compact: only the active lecture group stays expanded
      toc.querySelectorAll(".toc-h1.open").forEach(function (g) {{
        if (g === group) return;
        g.classList.remove("open");
        const c = g.querySelector(".toc-caret");
        if (c) c.setAttribute("aria-expanded", "false");
      }});
      if (!group.classList.contains("open")) {{
        group.classList.add("open");
        const caret = group.querySelector(".toc-caret");
        if (caret) caret.setAttribute("aria-expanded", "true");
      }}
    }}
    const r = link.getBoundingClientRect();
    const tr = toc.getBoundingClientRect();
    if (r.top < tr.top || r.bottom > tr.bottom) {{
      link.scrollIntoView({{ block: "nearest" }});
    }}
  }}

  function updateActive() {{
    ticking = false;
    let current = null;
    for (const h of headings) {{
      if (h.offsetParent === null) continue;
      if (h.getBoundingClientRect().top <= 120) current = h;
      else break;
    }}
    if (current) setActive(current.id);
  }}
  function onScroll() {{
    if (!ticking) {{
      ticking = true;
      window.requestAnimationFrame(updateActive);
    }}
  }}
  window.addEventListener("scroll", onScroll, {{ passive: true }});
  window.addEventListener("resize", onScroll);

  // open the group for the current hash, or the first group on a fresh visit
  const initial = decodeURIComponent(location.hash.slice(1));
  const initialLink = initial ? navLinks.get(initial) : null;
  const initialGroup = initialLink ? initialLink.closest(".toc-h1") : toc.querySelector(".toc-h1");
  if (initialGroup) initialGroup.classList.add("open");
  updateActive();

  document.querySelectorAll(".mcq-quiz").forEach(function (quizEl) {{
    const quiz = QUIZZES[Number(quizEl.dataset.quizIndex)];
    if (!quiz) return;

    const questions = quiz.questions;
    let currentQ = 0;
    let answers = new Array(questions.length).fill(null);
    // checked[i] is true only after "Check Answer" was pressed for question i.
    // Merely selecting an option must not reveal the answer when navigating back.
    let checked = new Array(questions.length).fill(false);

    const qEl = quizEl.querySelector(".quiz-question");
    const optEl = quizEl.querySelector(".quiz-options");
    const feedbackEl = quizEl.querySelector(".quiz-feedback");
    const progressEl = quizEl.querySelector(".q-num");
    const btnPrev = quizEl.querySelector(".btn-prev");
    const btnNext = quizEl.querySelector(".btn-next");
    const btnCheck = quizEl.querySelector(".btn-check");
    const btnReset = quizEl.querySelector(".btn-reset");
    const scoreEl = quizEl.querySelector(".quiz-score");

    function renderQuestion() {{
      const q = questions[currentQ];
      progressEl.textContent = currentQ + 1;
      qEl.innerHTML = q.q;
      optEl.innerHTML = "";
      q.options.forEach(function (opt, i) {{
        const div = document.createElement("div");
        div.className = "quiz-option";
        div.dataset.index = i;
        div.innerHTML = opt;
        div.addEventListener("click", function () {{ selectOption(i); }});
        if (answers[currentQ] === i) div.classList.add("selected");
        if (checked[currentQ]) {{
          div.classList.add("disabled");
          if (i === q.answer) div.classList.add("correct");
          if (i === answers[currentQ] && i !== q.answer) div.classList.add("incorrect");
        }}
        optEl.appendChild(div);
      }});
      feedbackEl.classList.remove("show", "correct", "incorrect");
      feedbackEl.innerHTML = "";
      if (checked[currentQ]) {{
        const ok = answers[currentQ] === q.answer;
        feedbackEl.classList.add("show", ok ? "correct" : "incorrect");
        feedbackEl.innerHTML = "<strong>" + (ok ? "✓ Correct!" : "✗ Incorrect") + "</strong> " + q.explain;
      }}
      btnPrev.disabled = currentQ === 0;
      btnNext.disabled = currentQ === questions.length - 1;
      btnCheck.style.display = checked[currentQ] ? "none" : "inline-block";
      btnReset.style.display = checked[currentQ] ? "inline-block" : "none";
      renderMathIn(quizEl);
    }}

    function selectOption(idx) {{
      if (checked[currentQ]) return;
      answers[currentQ] = idx;
      optEl.querySelectorAll(".quiz-option").forEach(function (el, i) {{
        el.classList.toggle("selected", i === idx);
      }});
    }}

    function checkAnswer() {{
      if (answers[currentQ] === null) {{
        feedbackEl.classList.add("show", "incorrect");
        feedbackEl.innerHTML = "<strong>Pick an option first.</strong>";
        return;
      }}
      checked[currentQ] = true;
      renderQuestion();
      if (checked.every(Boolean)) showScore();
    }}

    function nextQuestion() {{
      if (currentQ < questions.length - 1) {{
        currentQ += 1;
        renderQuestion();
      }}
    }}

    function prevQuestion() {{
      if (currentQ > 0) {{
        currentQ -= 1;
        renderQuestion();
      }}
    }}

    function resetQuiz() {{
      answers = new Array(questions.length).fill(null);
      checked = new Array(questions.length).fill(false);
      currentQ = 0;
      scoreEl.style.display = "none";
      renderQuestion();
    }}

    function showScore() {{
      const correct = answers.reduce(function (n, a, i) {{ return n + (a === questions[i].answer ? 1 : 0); }}, 0);
      scoreEl.style.display = "block";
      scoreEl.innerHTML = "<strong>Score: " + correct + "/" + questions.length +
        " (" + Math.round(correct / questions.length * 100) + "%)</strong>";
    }}

    btnNext.addEventListener("click", nextQuestion);
    btnPrev.addEventListener("click", prevQuestion);
    btnCheck.addEventListener("click", checkAnswer);
    btnReset.addEventListener("click", resetQuiz);
    renderQuestion();
  }});

  if (window.Chart) {{
    Chart.defaults.color = getComputedStyle(document.body).color;
    Chart.defaults.borderColor = getComputedStyle(document.documentElement).getPropertyValue("--border") || "#3c3c3c";
    CHARTS.forEach(function (cfg, idx) {{
      const canvas = document.getElementById("chart-" + idx);
      if (!canvas) return;
      const series = (cfg.series || [{{dataKey: "value", label: "Value"}}])[0];
      new Chart(canvas, {{
        type: cfg.chartType || "bar",
        data: {{
          labels: (cfg.data || []).map(function (d) {{ return d[cfg.xKey || "label"]; }}),
          datasets: [{{
            label: series.label || "Value",
            data: (cfg.data || []).map(function (d) {{ return d[series.dataKey]; }}),
            backgroundColor: "rgba(77,163,255,.65)",
            borderColor: "rgba(77,163,255,1)",
            borderWidth: 1,
            borderRadius: 6
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ display: false }},
            title: {{ display: false }},
            tooltip: {{ callbacks: {{ label: function (c) {{ return series.label + ": " + c.parsed.y; }} }} }}
          }},
          scales: {{
            y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }},
            x: {{ grid: {{ display: false }} }}
          }}
        }}
      }});
    }});
  }}
}});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
