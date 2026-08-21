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
