# Development

## Local dev server

`make dev` serves `site/` with hot reload (via `npx live-server`, downloaded ad hoc — nothing committed to the repo). Falls back to `python3 -m http.server` (no reload) if `npx`/Node isn't installed. Override the port: `PORT=3000 make dev`.

You can also open any `.html` file under `site/` directly in a browser — everything works via `file://` except `stuff.html`'s 3D model viewer, which needs `http://`.

## Adding a new blog post

Create `site/posts/<slug>/index.html` following the shape of an existing post: title in `<h1 class="page-title">`, date + categories in `<p class="page-meta">`, plus `<!-- NAV:START -->`/`<!-- SEO:START -->` marker comments (copy from any existing post). Drop a `.draft` file in the post's directory to keep it unlisted/unindexed but still reachable by direct URL.

Commit — the pre-commit hook automatically stamps in the nav, fills in SEO/social meta (description auto-derived from the post's first paragraph), and adds the post to the blog listing and sitemap (unless `.draft`). Nothing else needs to be touched by hand.

## Project structure

- `site/` — the entire published website: top-level pages (`index.html`, `about.html`, `stuff.html`, `resume.html`), `posts/`, `media/`, `styles/site.css`, `robots.txt`/`sitemap.xml`/`llms.txt`, `CNAME`.
- `templates/nav.html` — single source of truth for the nav bar.
- `scripts/` — maintenance scripts (below), run via the pre-commit hook or `make sync`.
- `tests/` — unit tests for `scripts/` (`make test`).
- `docs/pr-docs/` — planning docs for each feature/PR.

## Scripts (`scripts/`)

Each is a thin `main()` around testable functions; `lib_posts.py` holds the shared post-parsing logic (title/date/categories/excerpt/image/draft-status, read straight out of each post's own HTML — there's no front matter anymore).

| Script | Regenerates |
|---|---|
| `sync_nav.py` | every page's `<!-- NAV:START -->` block, from `templates/nav.html` |
| `sync_seo.py` | every page's `<!-- SEO:START -->` block (description/canonical/OpenGraph/Twitter) |
| `gen_blog_index.py` | the post listing in `site/index.html` |
| `gen_sitemap.py` | `site/sitemap.xml` |
| `update-dcurves-downloads.sh` | the dcurves PyPI download count in `site/resume.html`, from pepy.tech |

All five run from `.githooks/pre-commit` on every commit, or on demand via `make sync`.
