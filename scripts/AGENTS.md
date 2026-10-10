# scripts/

This directory holds the generators that keep the site in sync with its sources, and the libraries they share. Every script uses the Python standard library only.

## Scripts

This list comes from the first sentence of each script's docstring. `gen_script_index.py` generates it. To change a line, change the script's docstring.

<!-- SCRIPTS:START -->
- `dev.sh`: Local dev server for site/.
- `gen_blog_index.py`: Regenerates the post listing in site/index.html from posts under site/posts/ (auto-discovered via lib_posts, newest first, drafts excluded).
- `gen_crawler_files.py`: Generates site/CNAME, site/robots.txt, and site/llms.txt from the data files and the published posts.
- `gen_record.py`: Generates the `<!-- RECORD:START -->` block in docs/all-experiences.md from data/experiences.json, the single record behind the resume.
- `gen_resume.py`: Renders the resume from data/experiences.json, the single experience record.
- `gen_script_index.py`: Generates the script list in scripts/AGENTS.md from the first sentence of each script's docstring or leading comment.
- `gen_sitemap.py`: Regenerates site/sitemap.xml from the top-level pages + non-draft posts under site/.
- `lib_blocks.py`: Generated blocks between `<!-- NAME:START -->` and `<!-- NAME:END -->` markers.
- `lib_html.py`: Small HTML text helpers shared by the generators and checks.
- `lib_pagebreaks.py`: Pure checks for where printed page breaks fall in the resume.
- `lib_posts.py`: Shared helpers for reading post metadata straight out of each post's index.html.
- `lib_record.py`: Loads data/experiences.json, the single record of every experience fact, and builds the resume view of it.
- `lib_resume.py`: Shared mini-markup parser for resume strings in data/experiences.json.
- `lib_schema.py`: Validates JSON data against a JSON Schema, with the standard library only.
- `lib_site.py`: Single source of truth for site-wide constants (name, base URL, social links) in data/site.json, and for the top-level pages in data/pages.json.
- `sync_nav.py`: Keeps every page's `<nav class="site-nav">` block in sync with templates/nav.html.
- `sync_seo.py`: Stamps SEO/social meta tags (description, canonical, OpenGraph, Twitter card) into every page under site/, between `<!-- SEO:START -->` / `<!-- SEO:END -->` markers.
- `sync_social.py`: Regenerates the JSON-LD Person block and the visible social-links row on site/about.html from data/site.json.
- `update-dcurves-downloads.sh`: Refreshes the dcurves PyPI download count shown in resume.html from pepy.tech's public badge endpoint (no API key required, unlike api.pepy.tech).
<!-- SCRIPTS:END -->

## How a Generator Works

- A `gen_*.py` or `sync_*.py` script reads a source, builds text, and writes it into a file.
- It writes a marker block through `lib_blocks.py` (`wrap`, `sync_block`), or a whole file through `write_if_changed`. It writes only when the text changes.
- `main()` calls `sync(REPO_ROOT)`. `sync(repo_root)` takes the repo root, so tests can run it on a temporary repo.
- Loaders validate each JSON file in `data/` against its schema through `lib_schema.py`.

## Add a Generator

1. Write a failing test in `tests/test_<name>.py`.
2. Add `scripts/<name>.py` with a module docstring. Its first sentence becomes the line in the list above.
3. Add a `sync-<name>` target to the `Makefile` and add it to `SYNC_TARGETS`. Declare a dependency if the order matters.
4. Run `make sync`, `make lint`, and `make test`.

## Rules

- Keep each function to one job. Split a long function. Use a table of named handlers instead of an `if`/`elif` chain on a type.
- Do not write nested functions or lambdas. `tests/test_code_shape.py` fails on them.
- Fix a lint failure by restructuring the code. Do not raise a limit in `ruff.toml`.
- Import modules from `scripts/` by their plain name, for example `from lib_site import load_site`.
- Do not hardcode a fact from `data/`. Load it.
- Do not add a third-party package.
