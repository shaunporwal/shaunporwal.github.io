# Development

## Local dev server

`make dev` serves `site/` with hot reload (via `npx live-server`, downloaded ad hoc — nothing committed to the repo). Falls back to `python3 -m http.server` (no reload) if `npx`/Node isn't installed. Override the port: `PORT=3000 make dev`.

You can also open any `.html` file under `site/` directly in a browser — everything works via `file://` except `stuff.html`'s 3D model viewer, which needs `http://`.

## Adding a new blog post

Create `site/posts/<slug>/index.html` following the shape of an existing post: title in `<h1 class="page-title">`, date + categories in `<p class="page-meta">`, plus `<!-- NAV:START -->`/`<!-- SEO:START -->` marker comments (copy from any existing post). Drop a `.draft` file in the post's directory to keep it unlisted/unindexed but still reachable by direct URL.

Commit — the pre-commit hook automatically stamps in the nav, fills in SEO/social meta (description auto-derived from the post's first paragraph), and adds the post to the blog listing and sitemap (unless `.draft`). Nothing else needs to be touched by hand.

## Updating the resume

`data/experiences.json` is the single source of truth for every experience fact. It generates two outputs:

- `site/resume.html` (the `<!-- RESUME:START -->` block), through `scripts/gen_resume.py`.
- `docs/all-experiences.md` (the `<!-- RECORD:START -->` block), through `scripts/gen_record.py`.

Never edit a generated block by hand. Edit the JSON, then commit or run `make sync`. `data/experiences.schema.json` declares the format. `scripts/lib_record.py` validates the record against it at load time, so a bad edit fails at once.

The `resume` key on an item is the switch that puts it on the resume:

- `"resume": true` shows the item on the resume as it is.
- On a bullet, a `resume` string replaces the bullet text on the resume only.
- On an entry, education item, project, or skill, a `resume` object replaces named fields on the resume only, for example `{"org": "MSKCC"}`.
- On a group of bullets, a `resume` string is one resume bullet that sums up the group.
- A bullet with only a `resume` string shows on the resume and not in the record.

An item with no `resume` key shows only in the record. Dates are `YYYY-MM` (or `"present"`). Each output formats them in its own style. The resume Languages row comes from the `languages` list.

Strings that reach the resume support a tiny markup: `[label](url)` for links, `` `code` `` for inline code, `**text**` for bold, and `{dcurves}` for the live dcurves download count. Use bold sparingly — real impact metrics and standout tech only (e.g. `**$1M+**`, `**structural variants**`), not decoratively. Tokens can't nest (`**{dcurves}**` renders the literal text, not the substituted count) — keep them side by side instead.

On the resume, a project's title and links share a row (like experience/education), and its description is the one-line impact statement below. An education item's degree and dates/location share a row; the school (and the optional `honors` note) sit on their own line below, so a long school name can never push the dates onto a separate line.

Need a plain-text copy for LinkedIn or anywhere else that doesn't take HTML: `make resume-text` (prints to stdout, links rendered as `label (url)`, dcurves count fetched live).

## Lint

`ruff.toml` sets the lint rules for `scripts/` and `tests/`, including limits on complexity, statements, branches, and nested blocks. `tests/test_code_shape.py` adds two checks that ruff does not have: no nested functions and no lambdas.

- Run `make lint` to run both. `make test` runs lint first.
- The pre-commit hook runs `make lint`. A lint failure stops the commit.
- Install ruff once with `uv tool install ruff`. `ruff.toml` names the exact version, and CI installs that version.

Fix a lint failure by restructuring the code. Do not raise a limit to make a check pass.

## Site-wide constants (name, URLs, socials)

`data/site.json` is the single source of truth for the name, canonical base URL, and social/contact links (GitHub, X, LinkedIn, email, cal.com, default OG image). Anything that needs one of these — `sync_seo.py`, `gen_sitemap.py`, `sync_nav.py` (via `templates/nav.html`'s `{name}`/`{github}`/`{x}`/`{cal}` placeholders), `sync_social.py` (the JSON-LD + social links on `about.html`) — reads it from there via `scripts/lib_site.py`, instead of each hardcoding its own copy. Change a handle or URL once, in `data/site.json`, and it propagates everywhere on the next `make sync`/commit.

`data/pages.json` lists every top-level page with its SEO title and description, page type, and two switches: `sitemap` (list it in `sitemap.xml`) and `nav` (stamp the shared nav into it). `sync_seo.py`, `gen_sitemap.py`, and `sync_nav.py` all read it. To add a top-level page, create the HTML file and add one entry to `data/pages.json`. `data/pages.schema.json` declares the format.

(The `contact` list in `data/experiences.json` is intentionally separate, not merged into this — it's a deliberately curated subset/format for the resume specifically, e.g. no X/LinkedIn shown there but `cheminventory.co` included.)

`scripts/gen_crawler_files.py` generates `site/CNAME` (the host of `base_url`), `site/robots.txt`, and `site/llms.txt` from `data/site.json`, `data/pages.json`, the current role in `data/experiences.json`, and the published posts. Do not edit these files by hand. `base_url` must be the domain that GitHub Pages serves without a redirect (`www.shaunporwal.com`), because every canonical URL starts with it.

## Project structure

- `site/` — the entire published website: top-level pages (listed in `data/pages.json`), `posts/`, `media/`, `styles/site.css`, and the generated `robots.txt`, `sitemap.xml`, `llms.txt`, and `CNAME`.
- `data/experiences.json` — every experience fact; generates the resume and the full record (source of truth; see above).
- `data/experiences.schema.json` — the declared format of `data/experiences.json`.
- `data/site.json` — site-wide name/URL/social constants (source of truth; see above).
- `data/pages.json` — the top-level pages and their SEO, sitemap, and nav settings (source of truth; see above).
- `templates/nav.html` — single source of truth for the nav bar.
- `scripts/` — maintenance scripts (below), run via the pre-commit hook or `make sync`.
- `tests/` — unit tests for `scripts/` (`make test`).
- `docs/pr-docs/` — planning docs for each feature/PR.
- `docs/all-experiences.md` — the full experience record, generated from `data/experiences.json`.

## Scripts (`scripts/`)

Each is a thin `main()` around testable functions; `lib_blocks.py`, `lib_html.py`, `lib_posts.py`, `lib_record.py`, `lib_resume.py`, `lib_schema.py`, and `lib_site.py` hold shared parsing/rendering/config logic used by the generators below. Every generator writes its output between `<!-- NAME:START -->` and `<!-- NAME:END -->` markers through `lib_blocks.py`, so no generator has its own marker code.

| Script | Regenerates |
|---|---|
| `gen_resume.py` | `site/resume.html`'s `<!-- RESUME:START -->` block, from the items in `data/experiences.json` that are on the resume; `--text` prints a plain-text version instead |
| `gen_record.py` | `docs/all-experiences.md`'s `<!-- RECORD:START -->` block, from every item in `data/experiences.json` |
| `sync_nav.py` | every page's `<!-- NAV:START -->` block, from `templates/nav.html` + `data/site.json`; skips pages whose `nav` is off in `data/pages.json` |
| `sync_seo.py` | every page's `<!-- SEO:START -->` block (description/canonical/OpenGraph/Twitter), from `data/pages.json` + `data/site.json` |
| `sync_social.py` | `about.html`'s JSON-LD `Person` block and visible social-links row, from `data/site.json` |
| `gen_blog_index.py` | the post listing in `site/index.html` |
| `gen_sitemap.py` | `site/sitemap.xml`, from `data/pages.json` and the published posts |
| `update-dcurves-downloads.sh` | the dcurves PyPI download count in `site/resume.html`, from pepy.tech (runs *after* `gen_resume.py`, since that writes a static placeholder; the `Makefile` declares this) |

`tests/test_resume_print_layout.py` (run via `make test`) renders `site/resume.html` to PDF with Chromium. It reads the PDF text with `pdftotext`. The test fails when a page break splits an entry or a short section. It also fails when a heading sits alone at the bottom of a page. The resume has no page limit. If the test fails, change the `@media print` rules in `site/resume.html`. The test needs `npx` and `pdftotext`. Install `pdftotext` with `brew install poppler`. Install Chromium with `npx playwright install chromium`.

`make sync` runs all of the above. The `Makefile` is the only list of generators and their order. The pre-commit hook runs `make -k sync`, so a failed generator (for example, no network for the dcurves count) gives a warning, and the others still run.
