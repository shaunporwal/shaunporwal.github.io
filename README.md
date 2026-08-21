# Shaun Porwal's Site Repository

Source for shaunporwal.com — plain static HTML/CSS, no build step, no framework.

## Quick Start

```
make dev    # hot-reload dev server (site/)
make test   # run tests
make sync   # regenerate nav/SEO/sitemap/listing by hand
```

Everything published lives under `site/`; everything else (`templates/`, `scripts/`, `tests/`, `docs/`) is repo tooling, not site content. Pushing to `main` publishes `site/` to `gh-pages` via `.github/workflows/publish.yaml` — no build step, the committed HTML is what ships.

Enable the pre-commit hook once per clone (keeps nav/SEO/sitemap/listing in sync automatically):

```
git config core.hooksPath .githooks
```

See [docs/development.md](docs/development.md) for adding a new post, what each script does, and full project structure.

## Conventions (for agents/future contributors)

- `site/` is the *only* published output. Content never goes anywhere else; tooling (`scripts/`, `templates/`, `data/`, `tests/`, `docs/`) never gets published.
- Generated content lives between `<!-- X:START -->...<!-- X:END -->` markers (nav, SEO meta, blog listing, resume body). **Never hand-edit inside a marker block** — edit the source it's generated from (`templates/nav.html`, `data/resume.json`, a post's own content) and run `make sync`. If you're editing inside a marker block, stop and find the generator instead.
- No framework, no build step, no npm/Node dependency committed to the repo (`scripts/dev.sh` uses `npx` for local hot reload only — nothing installed into the repo itself).
- Every script in `scripts/` is small pure functions (`build_block`, `inject`, `sync`, etc.) plus a thin `main()` — not top-level script code — so it's importable and testable. Add a matching test in `tests/` for any new script or behavior change, and run `make test` before committing.
- Adding a post = one new `site/posts/<slug>/index.html` (+ optional `.draft`). Nothing else needs touching — the pre-commit hook regenerates nav/SEO/listing/sitemap.
- Resume content changes go in `data/resume.json`, never directly in `site/resume.html`.
- Name, base URL, and social/contact links (GitHub, X, LinkedIn, email, cal.com) live in `data/site.json` — never hardcode a new copy of one of these elsewhere; read it via `scripts/lib_site.py` instead.
