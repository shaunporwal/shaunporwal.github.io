# Development

## Local dev server

`make dev` serves `site/` with hot reload on all interfaces (via `npx live-server`, downloaded ad hoc — nothing committed to the repo). It prints only the tailnet link. It falls back to Python's static server, run with `uv` (no reload), if `npx`/Node isn't installed. The server log goes to `$TMPDIR/shaunporwal-site-dev-<port>.log`. The script exits with a message when the port is busy. Override the port: `PORT=3000 make dev`. `live-server` hides dotfiles, so `/.well-known/agents.json` answers 404 in dev only. The live site serves it.

You can also open any `.html` file under `site/` directly in a browser. Everything works through `file://`.

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

The `profiles` list in `data/site.json` names the profiles (GitHub, X, LinkedIn) and their order. The footer, the About buttons, the `llms.txt` Elsewhere list and the Person `sameAs` list all read it through `profile_links()` in `scripts/lib_site.py`. To add a profile, add its URL key to the schema, then add one `profiles` entry.

`data/pages.json` lists every top-level page, in nav menu order, with its title, SEO description, page type, and two switches: `sitemap` (list it in `sitemap.xml`) and `nav` (stamp the shared nav into it). A `menu` entry puts a link to the page in the nav. `sync_seo.py` writes each page's `<title>` and SEO tags from it, `gen_sitemap.py` lists it, and `sync_nav.py` builds the nav links from it. To add a top-level page, create the HTML file and add one entry to `data/pages.json`. `data/pages.schema.json` declares the format.

The resume `contact` list in `data/experiences.json` chooses which contact lines the resume shows. A line that `data/site.json` already holds names its key (`"site": "email"`) instead of a copy of the value. Only lines with no other home, such as the location, hold a literal `value`. The resume name also comes from `data/site.json`.

## Theme and motion

`data/theme.json` holds the color, type and motion tokens. `scripts/gen_theme.py` writes them into the `THEME` block of `site/styles/site.css`. `scripts/gen_icon.py` draws `site/media/favicon.svg` from the same colors. `tests/test_theme_contrast.py` checks the text pairs against WCAG AA in the light and dark modes.

The theme matches `cheminventory.co`: the same neutrals, radius, easing and grid. The accent is vermilion, and the display face is a system serif. Change a color once, in `data/theme.json`, then run `make sync`.

`site/js/motion.js` is the only script. It reveals sections on scroll, sets the header state, slides the nav marker, and writes the pointer position for the pointer light. It is first-party, has no framework and no build step. Every page works without it. A visitor who asks for reduced motion sees a still page.

The pointer light, the raised buttons, the edge light on the Book a call button and the lit hero dots read the `glow-tint`, `glow-on-primary`, `sheen` and `shadow-*` tokens and the `glow-size`, `motion-glow`, `motion-follow` and `sheen-duration` tokens in `data/theme.json`. Hover effects sit inside `@media (hover: hover) and (pointer: fine)`. Reduced motion hides the edge light and the lit dots. `tests/test_alive_css.py` guards these rules.

The PNG icons and `site/media/og-image.jpg` are rendered from `favicon.svg` and the data. No generator makes them. `tests/test_media_sizes.py` checks their sizes. After a change to the theme colors, the name or the hero lead, render them again.

## Discovery files

Each file below is generated. Change its source, then run `make sync`.

| File | Source | Script |
|---|---|---|
| `robots.txt`, `llms.txt`, `CNAME` | `data/site.json`, `data/pages.json`, the posts | `gen_crawler_files.py` |
| `sitemap.xml` | `data/pages.json`, the posts | `gen_sitemap.py` |
| `agents.txt`, `.well-known/agents.json` | `data/site.json` (`seo.agents`) | `gen_agent_files.py` |
| `llms-full.txt` | the posts | `gen_llms_full.py` |
| `feed.xml` | the posts | `gen_feed.py` |
| `manifest.webmanifest` | `data/site.json`, `data/theme.json` | `gen_manifest.py` |

No discovery file and no structured data holds the email address. The contact link is the booking link. `tests/test_site_contract.py` checks this. `resume.html` shows the email as a resume contact line.

`scripts/gen_crawler_files.py` generates `site/CNAME` (the host of `base_url`), `site/robots.txt`, and `site/llms.txt` from `data/site.json`, `data/pages.json`, the current role in `data/experiences.json`, and the published posts. Do not edit these files by hand. `base_url` must be the domain that GitHub Pages serves without a redirect (`www.shaunporwal.com`), because every canonical URL starts with it.

## Project structure

- `site/` — the entire published website: top-level pages (listed in `data/pages.json`), `posts/`, `media/`, `styles/site.css`, `js/motion.js`, and the generated discovery files (see above).
- `data/experiences.json` — every experience fact; generates the resume and the full record (source of truth; see above).
- `data/experiences.schema.json` — the declared format of `data/experiences.json`.
- `data/site.json` — site-wide name/URL/social constants (source of truth; see above).
- `data/pages.json` — the top-level pages and their SEO, sitemap, and nav settings (source of truth; see above).
- `data/theme.json` — the color, type and motion tokens (source of truth; see above).
- `templates/nav.html`, `templates/footer.html` — single sources of truth for the header and the footer.
- `scripts/` — maintenance scripts (below), run via the pre-commit hook or `make sync`.
- `tests/` — unit tests for `scripts/` (`make test`).
- `docs/pr-docs/` — planning docs for each feature/PR.
- `docs/all-experiences.md` — the full experience record, generated from `data/experiences.json`.

## Scripts (`scripts/`)

Each is a thin `main()` around testable functions. The `lib_*.py` modules hold the shared parsing, rendering, and config logic. Every generator writes its output between `<!-- NAME:START -->` and `<!-- NAME:END -->` markers through `lib_blocks.py`, so no generator has its own marker code.

`scripts/AGENTS.md` lists every script with a one-line summary. That list is generated from each script's docstring, so this guide does not repeat it.

`tests/test_resume_print_layout.py` (run via `make test`) renders `site/resume.html` to PDF with Chromium. It reads the PDF text with `pdftotext`. The test fails when a page break splits an entry or a short section. It also fails when a heading sits alone at the bottom of a page. The resume has no page limit. If the test fails, change the `@media print` rules in `site/resume.html`. The test needs `npx` and `pdftotext`. Install `pdftotext` with `brew install poppler`. Install Chromium with `npx playwright install chromium`.

`make sync` runs all of the above. The `Makefile` is the only list of generators and their order. The pre-commit hook runs `make -k sync`, so a failed generator (for example, no network for the dcurves count) gives a warning, and the others still run.

## Monthly download refresh

`.github/workflows/refresh-downloads.yaml` runs on the 1st of each month and by hand. It runs `scripts/commit-downloads.sh`, which refreshes the dcurves download count in `resume.html`, commits it as the bot and pushes it to `main`. Shaun asked for this on 2026-10-27, with no PR. A push made with the workflow token does not start the publish workflow, so the refresh starts `publish.yaml` itself. A by-hand run has a `republish` switch that publishes with no count change. The script stops when the diff is not exactly the one count line. The pre-commit hook still refreshes the count at each commit.
