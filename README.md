# Shaun Porwal's Site Repository

This repository contains the source files for my personal website, shaunporwal.com — plain static HTML/CSS, no build step, no framework.

## Local Development

Just open any `.html` file directly in a browser, or serve the repo root with any static file server (e.g. `python3 -m http.server`).

## Deployment

Pushing to `main` triggers `.github/workflows/publish.yaml`, which copies the site files to the `gh-pages` branch. No build/render step — the committed HTML is what ships.

## Project Structure

- `index.html`, `about.html`, `stuff.html`, `resume.html`: top-level pages
- `posts/`: blog posts, one `index.html` per post directory
- `media/`: images, 3D models, PDFs
- `styles/site.css`: shared stylesheet
- `templates/nav.html`: single source of truth for the nav bar, stamped into every page (see `scripts/sync-nav.py`)
- `scripts/`: small maintenance scripts run via the pre-commit hook (`.githooks/pre-commit`) — keeps the nav and the dcurves download count in `resume.html` current
- `docs/pr-docs/`: planning docs for each feature/PR

## Git hooks

Enable the repo's pre-commit hook once per clone:

```
git config core.hooksPath .githooks
```
