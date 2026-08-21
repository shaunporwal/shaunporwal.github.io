# Development

## Local dev server

`make dev` serves `site/` with hot reload (via `npx live-server`, downloaded ad hoc — nothing committed to the repo). Falls back to `python3 -m http.server` (no reload) if `npx`/Node isn't installed. Override the port: `PORT=3000 make dev`.

You can also open any `.html` file under `site/` directly in a browser — everything works via `file://` except `stuff.html`'s 3D model viewer, which needs `http://`.

## Adding a new blog post

Create `site/posts/<slug>/index.html` following the shape of an existing post: title in `<h1 class="page-title">`, date + categories in `<p class="page-meta">`, plus `<!-- NAV:START -->`/`<!-- SEO:START -->` marker comments (copy from any existing post). Drop a `.draft` file in the post's directory to keep it unlisted/unindexed but still reachable by direct URL.

Commit — the pre-commit hook automatically stamps in the nav, fills in SEO/social meta (description auto-derived from the post's first paragraph), and adds the post to the blog listing and sitemap (unless `.draft`). Nothing else needs to be touched by hand.

## Updating the resume

`data/resume.json` is the single source of truth — never hand-edit the `<!-- RESUME:START -->` block in `site/resume.html` directly, it gets overwritten. Edit the JSON, then either commit (pre-commit regenerates `site/resume.html`) or run `python3 scripts/gen_resume.py` directly.

Bullet/title/sub strings in the JSON support a tiny markup: `[label](url)` for links, `` `code` `` for inline code, `**text**` for bold, and `{dcurves}` for the live dcurves download count. Use bold sparingly — real impact metrics and standout tech only (e.g. `**$1M+**`, `**50+ data scientists**`), not decoratively. `docs/all-experiences.md` is the fuller, hand-maintained work-history reference to pull additional bullets from — it isn't wired into generation, so it never goes stale-vs-itself, but it also won't auto-update `resume.json`.

Need a plain-text copy for LinkedIn or anywhere else that doesn't take HTML: `make resume-text` (prints to stdout, links rendered as `label (url)`, dcurves count fetched live).

## Project structure

- `site/` — the entire published website: top-level pages (`index.html`, `about.html`, `stuff.html`, `resume.html`), `posts/`, `media/`, `styles/site.css`, `robots.txt`/`sitemap.xml`/`llms.txt`, `CNAME`.
- `data/resume.json` — resume content (source of truth; see above).
- `templates/nav.html` — single source of truth for the nav bar.
- `scripts/` — maintenance scripts (below), run via the pre-commit hook or `make sync`.
- `tests/` — unit tests for `scripts/` (`make test`).
- `docs/pr-docs/` — planning docs for each feature/PR.
- `docs/all-experiences.md` — full work-history reference (not generated, not wired into `resume.json`).

## Scripts (`scripts/`)

Each is a thin `main()` around testable functions; `lib_posts.py` and `lib_resume.py` hold shared parsing/rendering logic used by the generators below.

| Script | Regenerates |
|---|---|
| `gen_resume.py` | `site/resume.html`'s `<!-- RESUME:START -->` block, from `data/resume.json`; `--text` prints a plain-text version instead |
| `sync_nav.py` | every page's `<!-- NAV:START -->` block, from `templates/nav.html` |
| `sync_seo.py` | every page's `<!-- SEO:START -->` block (description/canonical/OpenGraph/Twitter) |
| `gen_blog_index.py` | the post listing in `site/index.html` |
| `gen_sitemap.py` | `site/sitemap.xml` |
| `update-dcurves-downloads.sh` | the dcurves PyPI download count in `site/resume.html`, from pepy.tech (must run *after* `gen_resume.py`, since that writes a static placeholder) |

`tests/test_resume_page_count.sh` (run via `make test`) renders `site/resume.html` to PDF with `npx playwright` and fails if it exceeds 2 printed pages — a safety net against `data/resume.json` quietly growing past what the print CSS was tuned for. If it fails: trim a bullet, or tighten `@media print` in `site/resume.html`.

All six run in order from `.githooks/pre-commit` on every commit, or on demand via `make sync`.
