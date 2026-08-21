# Shaun Porwal's Site Repository

This repository contains the source files for my personal website, shaunporwal.com — plain static HTML/CSS, no build step, no framework, no npm/Node.

## Local Development

```
make dev
```

Serves `site/` with hot reload on save (via `npx live-server` — downloaded ad hoc, nothing committed to the repo) and prints the URL. Falls back to a plain `python3 -m http.server` (no reload) if `npx`/Node isn't installed. Override the port with `PORT=3000 make dev`.

You can also open any `.html` file under `site/` directly in a browser — everything works via `file://` except `stuff.html`'s 3D model viewer, which needs `http://`.

## Adding a new blog post

Create `site/posts/<slug>/index.html` following the shape of an existing post (title in `<h1 class="page-title">`, date + categories in `<p class="page-meta">`, plus `<!-- NAV:START -->`/`<!-- SEO:START -->` marker comments — copy them from any existing post). Drop a `.draft` file in the post's directory to keep it unlisted/unindexed but still reachable by direct URL. Commit — the pre-commit hook (see below) automatically:

- stamps in the current nav
- fills in SEO/social meta tags (description auto-derived from the post's first paragraph)
- adds the post to the blog listing on `site/index.html` (unless `.draft`)
- adds it to `site/sitemap.xml` (unless `.draft`)

No other file needs to be touched by hand.

## Deployment

Pushing to `main` triggers `.github/workflows/publish.yaml`, which publishes the `site/` directory as-is to the `gh-pages` branch. No build/render step — the committed HTML is what ships.

## Project Structure

Everything published to the live site lives under `site/` — everything else here is repo tooling/docs, not site content:

- `site/`: the entire published website
  - `index.html`, `about.html`, `stuff.html`, `resume.html`: top-level pages
  - `posts/`: blog posts, one `index.html` per post directory
  - `media/`: images, 3D models, PDFs
  - `styles/site.css`: shared stylesheet
  - `robots.txt`, `sitemap.xml`, `llms.txt`: classic + AI-crawler SEO
  - `CNAME`: custom domain for GitHub Pages
- `templates/nav.html`: single source of truth for the nav bar
- `scripts/`: maintenance scripts run via the pre-commit hook — see below
- `tests/`: unit tests for `scripts/` (`python3 -m unittest discover -s tests`)
- `docs/pr-docs/`: planning docs for each feature/PR

## Scripts (`scripts/`)

Each script is a thin `main()` wrapper around testable functions in the same file (`lib_posts.py` holds the shared post-parsing logic used by the other three):

- `sync_nav.py`: stamps `templates/nav.html` into every page's `<!-- NAV:START -->` block.
- `sync_seo.py`: stamps description/canonical/OpenGraph/Twitter meta into every page's `<!-- SEO:START -->` block (top-level pages hand-registered, posts auto-discovered).
- `gen_blog_index.py`: regenerates the post listing in `site/index.html`.
- `gen_sitemap.py`: regenerates `site/sitemap.xml`.
- `update-dcurves-downloads.sh`: refreshes the dcurves PyPI download count in `site/resume.html` from pepy.tech.

All five run automatically from `.githooks/pre-commit` on every commit, or on demand via `make sync`.

## Git hooks

Enable the repo's pre-commit hook once per clone:

```
git config core.hooksPath .githooks
```

## Tests

```
make test
```

(equivalent to `python3 -m unittest discover -s tests -p "test_*.py" && bash tests/test_update_dcurves_downloads.sh`)
