# scripts/

This directory holds the generators that keep the site in sync with its sources, and the libraries they share. Every script uses the Python standard library only.

## Scripts

This list comes from the first sentence of each script's docstring. `gen_script_index.py` generates it. To change a line, change the script's docstring.

<!-- SCRIPTS:START -->
- `commit-downloads.sh`: Refreshes the dcurves download count in resume.html, then commits and pushes the change to main as the bot.
- `dev.sh`: Local dev server for site/.
- `gen_agent_files.py`: Generates site/agents.txt and site/.well-known/agents.json, the rules for AI agents, from data/site.json.
- `gen_blog_index.py`: Regenerates the post listing in site/index.html from posts under site/posts/ (auto-discovered via lib_posts, newest first, drafts excluded).
- `gen_crawler_files.py`: Generates site/CNAME, site/robots.txt, and site/llms.txt from the data files and the published posts.
- `gen_feed.py`: Generates site/feed.xml, an Atom feed of the published posts, newest first, from the posts.
- `gen_icon.py`: Generates site/media/favicon.svg, the site icon, from the light colors in data/theme.json.
- `gen_llms_full.py`: Generates site/llms-full.txt, the full text of every published post as Markdown, from the posts.
- `gen_manifest.py`: Generates site/manifest.webmanifest, the web app manifest, from data/site.json and data/theme.json.
- `gen_record.py`: Generates the `<!-- RECORD:START -->` block in docs/all-experiences.md from data/experiences.json, the single record behind the resume.
- `gen_resume.py`: Renders the resume from data/experiences.json, the single experience record.
- `gen_script_index.py`: Generates the script list in scripts/AGENTS.md from the first sentence of each script's docstring or leading comment.
- `gen_sitemap.py`: Regenerates site/sitemap.xml from the top-level pages + non-draft posts under site/.
- `gen_theme.py`: Generates the THEME token block in site/styles/site.css from data/theme.json.
- `lib_blocks.py`: Generated blocks between `<!-- NAME:START -->` and `<!-- NAME:END -->` markers.
- `lib_curve.py`: Decision curve maths and plot geometry for the dcurves card picture, with the standard library only.
- `lib_curve_svg.py`: Draws the sample decision curve on the dcurves card as inline SVG, with the standard library only.
- `lib_html.py`: Small HTML text helpers shared by the generators and checks.
- `lib_images.py`: Reads the pixel size of a PNG, JPEG or WebP file, with the standard library only.
- `lib_jsonld.py`: Builds the schema.org JSON-LD for the site: Person, WebSite, ProfilePage, BlogPosting and BreadcrumbList.
- `lib_markdown.py`: Converts the body of a post's index.html to Markdown for llms-full.txt.
- `lib_pagebreaks.py`: Pure checks for where printed page breaks fall in the resume.
- `lib_pictures.py`: Renders the picture at the top of each Work card from the `picture` object of a project in data/site.json.
- `lib_posts.py`: Shared helpers for reading post metadata straight out of each post's index.html.
- `lib_record.py`: Loads data/experiences.json, the single record of every experience fact, and builds the resume view of it.
- `lib_resume.py`: Shared mini-markup parser for resume strings in data/experiences.json.
- `lib_schema.py`: Validates JSON data against a JSON Schema, with the standard library only.
- `lib_site.py`: Single source of truth for site-wide constants (name, base URL, social links) in data/site.json, for the top-level pages in data/pages.json, and for the color and type tokens in data/theme.json.
- `render_pdf.py`: Prints each page that names a `pdf` in data/pages.json to that PDF in site/, with headless Chrome.
- `sync_footer.py`: Keeps every page's footer block in sync with templates/footer.html.
- `sync_home.py`: Stamps the hero and the Work cards into site/index.html from data/site.json and the experience record.
- `sync_nav.py`: Keeps every page's header block in sync with templates/nav.html.
- `sync_seo.py`: Stamps SEO/social meta tags (description, canonical, OpenGraph, Twitter card, icons, theme colors, feed link, structured data) into every page under site/, between `<!-- SEO:START -->` / `<!-- SEO:END -->` markers.
- `sync_social.py`: Regenerates the ProfilePage JSON-LD block and the visible link buttons on site/about.html from data/site.json.
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
