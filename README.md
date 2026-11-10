# CSCI415 Midterm Notes — web build

The site is generated from `CSCI415_Midterm_Master_Notes.md` into `web_export/`.

## What's in the site

- **Navigation sidebar** — generated from the rendered `h1`/`h2`/`h3` headings.
  - Click a lecture to jump to it; expand a lecture to reach individual sections.
  - The **Filter sections** box narrows the tree as you type; clearing it collapses
    back to the section you are currently reading.
  - The section at the top of the viewport is highlighted automatically (scrollspy).
  - On screens narrower than 1100px the sidebar becomes a drawer opened with the ☰
    button (closes on link click, overlay click, or `Esc`).
- **Interactive quizzes** — 13 quizzes / 125 questions.
  - Selecting an option only marks it; the correct answer and explanation stay hidden.
  - Answers are revealed **only after pressing “Check Answer”** for that question.
  - Navigating to another question and back preserves your selection but does not
    reveal the answer until you check it.
  - Once checked, the result stays visible when you navigate away and return.
  - “Reset Quiz” clears all selections and checked state.
- **Diagrams** — 37 TikZ blocks pre-rendered to SVG in `web_export/diagrams/`.
- **Chart** — the `chatgpt-jsx` block becomes a Chart.js bar chart.

## Preview locally

```bash
cd /home/omarcash/Documents/Notes/Compiler
./serve.sh                 # http://localhost:8080
```

`serve.sh` is just `python3 -m http.server 8080 --directory web_export`.

## Rebuild

```bash
.venv/bin/python build.py
```

The first time only:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`build.py` does five things:

1. Converts Markdown with **Python-Markdown** (`extra` → tables, fenced code, footnotes).
2. Converts Obsidian callouts (`> [!warning]`), wikilinks (`[[#...]]`), and task lists.
3. Replaces ` ```mcq-quiz ` blocks with working quiz components.
4. Replaces ` ```chatgpt-jsx ` / ` ```chatgpt-ui ` blocks with a Chart.js chart / tip box.
5. Renders every ` ```tikz ` block to `web_export/diagrams/diagram-NN.svg` using
   **Tectonic** (LaTeX) + **pdftocairo**, so the published site needs no LaTeX.

TikZ diagrams are cached. If you change a diagram, either install Tectonic
(`https://tectonic-typesetting.github.io/`) and re-run the build, or set
`TECTONIC=/path/to/tectonic`. Without Tectonic the build keeps the existing SVGs.

## Deploy to Netlify

**Drag and drop:** drag the whole `web_export/` folder onto <https://app.netlify.com/drop>.

**CLI:**

```bash
netlify deploy --prod --dir=web_export
```

**Git:** the root `netlify.toml` publishes `web_export/`. Commit `web_export/`
(the SVGs are static assets), or add a build command
`pip install -r requirements.txt && python build.py` if you want Netlify to rebuild.
Netlify does not have Tectonic, so a rebuild there will reuse the committed SVGs.

## Why not just fix the old export?

The old `web_export/index.html` was a hand-written exporter with several bugs:

- Markdown tables were never enabled → raw `| a | b |` lines.
- Inline code was emitted backwards (`</code>text<code>`).
- `<div class="mcq-quiz">` was nested inside `<p>` (invalid HTML).
- TikZ blocks called `lualatex`, which was not installed → 37 error boxes.
- The quiz script ended with `document.body.innerHTML = ...`, which destroyed every
  rendered question/option and every event listener. That is why quizzes showed only
  “Question 1 of 10 / Previous / Next / Check Answer”.
- The wikilink regex was double-escaped, so `[[#...]]` links were never converted.

## Alternatives worth knowing

| Need | Library / tool | Notes |
|---|---|---|
| Obsidian vault → site | **Quartz** | Native wikilinks, callouts, graph view, search, KaTeX. Needs Node. Custom MCQ/Chart blocks need a Quartz component/plugin. |
| Markdown docs → site | **MkDocs Material** | Python, excellent tables/admonitions/KaTeX, easy Netlify. Wikilinks need a plugin. |
| React/MDX docs | **Astro Starlight** / **Docusaurus** | Best if you want interactive quiz components as real React components. |
| Math | **KaTeX** (used here) | Faster than MathJax; good enough for these formulas. |
| TikZ in browser | **TikZJax** | Client-side WASM TeX; no LaTeX install, but slower and only supports a subset of libraries. |
| TikZ at build time | **Tectonic + pdftocairo** (used here) | Fast static SVG, perfect fidelity, no runtime cost. |
| Charts | **Chart.js** (used here) | Small, renders the `chatgpt-jsx` bar chart. |
| Quizzes | custom JS (used here) / **quizdown-js** | Custom keeps the existing JSON format and explanations. |
