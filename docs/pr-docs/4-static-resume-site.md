# PR 4: Drop Quarto, Rebuild as Plain Static HTML + Resume Page

Status: in-scope work complete

Branch: `feature/static-resume-site`

## Goal

Replace the Quarto-built site with a hand-written, minimal static HTML+CSS site (no framework, no executed R/Python), and add a `/resume` page as the first page built in the new style, reconciled from `jobapps/resume/all_experiences.txt` and the current LinkedIn export.

## Context

The site currently requires Quarto plus a Python/R execution environment (`renv`, `renv.lock`, `pyproject.toml`, `.python-version`) to render even prose-only pages, and publishes via `.github/workflows/quarto-publish.yaml`. Shaun no longer wants that overhead or academic-doc tooling in a personal site. The resume also currently only exists as a static PDF (`media/porwal-resume.pdf`) linked from the nav "Docs" menu, sourced from stale/incomplete data — the fuller, current source of truth is `jobapps/resume/all_experiences.txt` (cloned separately to `GitHub/other/jobapps`), reconciled with the newer LinkedIn export the recruiter-facing PDF is missing (current Junto Technologies role, etc).

## Implementation Checklist

Ordered from least consequential/complex to highest blast radius.

### Tier 1 — New resume page (isolated, additive, no existing page touched)

- [x] Reconcile `all_experiences.txt` + LinkedIn export into one current experience record (verify no content lost, dates consistent).
- [x] Build `resume.html`: plain HTML, minimal inline CSS, single page, print-friendly (for portal PDF export), no build step.
- [x] Correct the dcurves download count from a stale hand-typed "29k+" to the live figure (72k+, sourced from `static.pepy.tech`'s public badge endpoint — no API key required).
- [x] Add `scripts/update-dcurves-downloads.sh` + wire into `.githooks/pre-commit` so the dcurves download count in `resume.html` stays current on every commit.
- [x] All resume links open in a new tab (`<base target="_blank" rel="noopener">`) so the resume page itself never navigates away.
- [x] Remove GPA from the Education section.

### Tier 2 — Shared minimal layout (small, reusable, low risk)

- [x] Write a minimal shared nav + base CSS (`styles/site.css`, no framework), kept DRY via a single source template (`templates/nav.html`) stamped into every page by `scripts/sync-nav.py` between `<!-- NAV:START -->`/`<!-- NAV:END -->` markers — avoids both a runtime include/fetch (breaks under `file://`) and hand-duplicated nav blocks drifting out of sync.
- [x] Wire `sync-nav.py` into `.githooks/pre-commit` alongside the dcurves-download sync.
- [x] Wire resume page into the shared nav.

### Tier 3 — Migrate existing pages (touches live content, one page at a time)

- [x] Convert `about.qmd` → `about.html`.
- [x] Convert `stuff.qmd` → `stuff.html`.
- [x] Convert `index.qmd` (blog index) → `index.html` (generated from post front matter, non-draft posts only, sorted newest-first — matches prior Quarto listing behavior).

### Tier 4 — Migrate posts, freezing executed-code output (highest content risk)

- [x] For each `posts/*/index.qmd`, hand-convert to static HTML (extracted from the last `quarto render` output, wrapped in the new nav/CSS shell), preserving already-rendered output/images as committed static content (no re-execution, ever). All 10 posts converted, including drafts (matches prior behavior: draft posts stayed reachable by direct URL, just excluded from the listing).
- [x] Confirm every post's images/links still resolve after conversion (verified via local static server + asset-reference check — zero missing references).

### Tier 5 — Swap build/publish pipeline and remove Quarto (highest blast radius)

- [x] Replace `.github/workflows/quarto-publish.yaml` with `.github/workflows/publish.yaml`: rsyncs the static site files (excluding repo-internal dirs like `docs/`, `scripts/`, `.github/`) to a `_site/` dir and publishes it to the `gh-pages` branch via `peaceiris/actions-gh-pages` — same hosting mechanism (Pages served from `gh-pages`) as before, no GitHub repo-settings change required.
- [x] Remove `_quarto.yml`, `.quarto/`, `.quarto-output/`, `_freeze/`, `renv/`, `renv.lock`, `pyproject.toml`, `.python-version`, `.Rprofile`, `posts/_metadata.yml`, orphaned `media/banana.qmd`/`media/heron.qmd` (unreferenced standalone 3D-viewer pages), and the dead pre-migration stylesheets (`styles/base.css`, `styles/models.css`, `styles/navbar.css`, `styles/palette.css`, superseded by `styles/site.css`).
- [x] Update `README.md` to describe the new no-build static setup.
- [x] Update `CLAUDE.md` §9 (repo-specific guidance) off Quarto/poetry commands.
- [x] Update `.github/pull_request_template.md`'s "Required Checks" off `quarto render`.
- [x] Simplify `.gitignore` (drop R/Quarto/renv-specific entries, keep just `.DS_Store` and the new `_site/` build output dir).

## Smoke Tests

- [x] `resume.html` opens correctly standalone and prints to a clean single/few-page PDF; all links open in a new tab.
- [x] Nav links work identically across pages, no broken hrefs (verified via `scripts/sync-nav.py` round-trip test + full asset-reference scan).
- [x] Migrated `about`/`stuff`/`index` content and embedded media (`.glb` model viewers) still render (served locally via `python3 -m http.server`, all pages 200, all local asset refs resolve).
- [x] All 10 posts render with original content/images intact; all post images/links resolve.
- [ ] GitHub Pages deploy succeeds with the new `publish.yaml` workflow and serves the live site correctly at shaunporwal.com — **pending: verify after this branch merges to `main` and the workflow runs.**
- [ ] Mobile rendering (resume, nav, post images) verified on an actual phone/browser devtools — **pending: fixed the concrete overflow bugs found via CSS review (dead-class post images, resume date/skills grid), but this session has no screenshot/browser tool to visually confirm on a real small viewport. Please spot-check on your phone.**
- [x] No leftover references to Quarto/R/Python in build docs, CI, or CLAUDE.md (repo-wide grep clean except frozen historical post prose and PR #3's own historical description, both left as accurate-at-the-time records).

### Tier 6 — Declutter repo root into site/ (post-implementation follow-up, requested after Tier 5 landed)

- [x] Move all published content (`index.html`, `about.html`, `stuff.html`, `resume.html`, `posts/`, `media/`, `styles/`, `CNAME`, `.nojekyll`) into a new `site/` directory — repo root now holds only `site/`, `templates/`, `scripts/`, `docs/`, `.github/`, `.githooks/`, `README.md`, `CLAUDE.md`/`AGENTS.md`, `LICENSE`.
- [x] Update `scripts/sync_nav.py` and `scripts/update-dcurves-downloads.sh` to operate on `site/` instead of the repo root.
- [x] Simplify `.github/workflows/publish.yaml` to publish `site/` directly (no more rsync/exclude list needed, since `site/` only ever contains publishable content).
- [x] Removed stale pre-migration Quarto build cruft found during the move: root-level `_site/` (old default Quarto output dir) and `_environment` (pointed at a now-deleted `renv`-managed Python venv).
- [x] Update `README.md` and `CLAUDE.md` §9 to describe the `site/`-scoped layout.
- [x] Re-verify: local static server from `site/`, full asset-reference scan, nav-sync round-trip — all clean.

### Tier 7 — Classic + AI-crawler SEO quick wins (post-implementation follow-up)

- [x] `site/robots.txt`: allows all crawlers, points to the sitemap.
- [x] `site/sitemap.xml`: auto-generated (see Tier 8) from top-level pages + non-draft posts, with `<lastmod>` from each post's date.
- [x] `site/llms.txt`: hand-curated summary for AI agents/crawlers per the emerging llms.txt convention (site purpose, page list, contact links).
- [x] Per-page SEO/social meta (`<meta name="description">`, `<link rel="canonical">`, OpenGraph, Twitter Card) on every top-level page and every post — post descriptions/images auto-derived from each post's first paragraph and first local image.
- [x] JSON-LD `Person` structured data on `about.html` (name, url, email, `sameAs` → GitHub/X/LinkedIn).
- [x] Corrected `og:image`/`twitter:image` per post to use that post's own header image where one exists, falling back to a site default.

### Tier 8 — Automate the above so nothing needs manual upkeep, and add tests (post-implementation follow-up)

- [x] New `scripts/lib_posts.py`: single shared parser that reads a post's title/date/categories/excerpt/image/draft-status straight out of its own `index.html` (no front matter exists anymore) — backs `sync_seo.py`, `gen_sitemap.py`, and `gen_blog_index.py` so all three agree on what "a post" is, and a new post needs zero registration anywhere.
- [x] Draft status is now a `.draft` sentinel file in a post's directory (replaces the old Quarto `draft: true` front-matter field, which no longer exists post-migration). Backfilled `.draft` for the 5 posts that were draft under the old front matter.
- [x] New `scripts/sync_seo.py`, `scripts/gen_sitemap.py`, `scripts/gen_blog_index.py` — all wired into `.githooks/pre-commit` alongside the existing nav/download-count sync. Net effect: adding a new post is just "create `site/posts/<slug>/index.html`, commit" — nav, SEO tags, sitemap entry, and blog-listing entry all regenerate automatically.
- [x] Refactored every script from top-level script code into small pure functions (`build_block`, `inject`, `sync`, etc.) with a thin `main()`, both for testability and so each piece (rendering vs. file I/O vs. discovery) is independently reusable — renamed `sync-nav.py`/`sync-seo.py`/`gen-*.py` (hyphenated, not importable) to `sync_nav.py`/`sync_seo.py`/`gen_*.py`.
- [x] New `tests/` directory: 33 unit tests (`python3 -m unittest discover -s tests`) covering `lib_posts`, `sync_nav`, `sync_seo`, `gen_sitemap`, `gen_blog_index` — draft detection, idempotency (second run reports no changes), marker-injection edge cases (missing markers, already-synced), depth-aware relative nav paths, excerpt truncation, sorting. Plus a dependency-free shell test (`tests/test_update_dcurves_downloads.sh`) for the count-extraction and sed-rewrite logic in `update-dcurves-downloads.sh`, using fixture data instead of hitting the network.
- [x] New `.github/workflows/test.yaml`: runs the full test suite on every push to `main` and every PR.
- [x] Deleted the one-off migration scripts used to do the Quarto→static conversion and the first SEO-meta pass (both lived only in the session scratchpad, never committed) now that their output is committed and the ongoing-maintenance versions (`sync_seo.py`, etc.) supersede them.
- [x] Added `scripts/dev.sh`: one-command local dev server with hot reload (`npx live-server`, downloaded ad hoc — no `package.json`/`node_modules` committed), falling back to plain `python3 -m http.server` if Node/npx isn't installed.
- [x] Added a root `Makefile` (`make dev`, `make test`, `make sync`) so the common commands are short and memorable without adopting npm as a script runner. CI (`test.yaml`) now calls `make test` too, so there's one source of truth for "how tests run."

### Tier 9 — Docs trim + mobile fixes (post-implementation follow-up)

- [x] README was accumulating generated-content bookkeeping detail (per-script table, full "adding a post" walkthrough) better suited as reference material than something read on every visit — moved that detail to `docs/development.md`, README is now just Quick Start commands + a pointer. `CLAUDE.md` §9 trimmed the same way, pointing at `docs/development.md`.
- [x] Fixed a real mobile bug: the two images in `posts/python-package-automation/index.html` used leftover Bootstrap classes (`img-fluid figure-img`) that don't exist in `site.css`, so they had no width constraint and would overflow a phone viewport. Added a global `img, video { max-width: 100%; height: auto; }` rule to `site.css` (plus `pre, code { overflow-x: auto; }`), and removed the dead classes (added real `alt` text while touching those tags).
- [x] `resume.html`: `.entry-meta` (date ranges) and the skills/education grid now stack instead of staying `white-space: nowrap` under 420px, so long date/location strings can't force horizontal overflow on small phones.
- [x] Nav collapses into a hamburger (☰) dropdown under 700px, via a CSS-only checkbox toggle in `templates/nav.html` (no JS, consistent with the rest of the site) — `scripts/sync_nav.py` propagated it to every page.
- [x] Resume content update: agent-swarm bullet (Junto Technologies) reworded twice per feedback (dropped "within days," added Apple Watch remote-control detail, condensed to one clean parenthetical list); AI/ML skills line extended (vLLM/llama.cpp, Tailscale self-hosted infra, promptfoo evals) rather than adding a new skills row, per "parsimonious."
- [x] Added `make dev`/`make test` as the documented entry points (README pointed at `./scripts/dev.sh` directly before); CI's `test.yaml` now calls `make test` too, so there's one source of truth for how tests run.

### Tier 10 — DRY resume source of truth (`data/resume.json`), post-implementation follow-up

- [x] Problem: resume content lived only as hand-authored HTML in `site/resume.html`, duplicating whatever's on LinkedIn with no shared source — every update meant editing both by hand from scratch. Decision (discussed first): no LinkedIn write-back is possible (no API for that), so the fix is a single local source of truth plus a generated LinkedIn-paste-ready text export, not automated sync.
- [x] New `data/resume.json`: structured source of truth for all resume content (contact, experience, projects, education, skills). Bullet/title/sub strings support a tiny markup — `[label](url)` for links, `` `code` `` for inline code, `{dcurves}` for the live download-count token — parsed by new `scripts/lib_resume.py` (`render_html`/`render_text`).
- [x] New `scripts/gen_resume.py`: regenerates `site/resume.html`'s `<!-- RESUME:START -->` block from `data/resume.json` (verified byte-identical to the prior hand-authored HTML on first run); `--text` prints a plain-text, LinkedIn-paste-ready version to stdout, fetching the live dcurves count over the network for that mode specifically (falls back to the static placeholder if the fetch fails).
- [x] Wired into `.githooks/pre-commit` and `make sync`, ordered *before* `update-dcurves-downloads.sh` (which writes the live count into whatever `gen_resume.py` just wrote — order matters since `gen_resume.py` itself only writes a static placeholder). Added `make resume-text` shortcut.
- [x] New `docs/all-experiences.md`: the fuller work-history record (previously only in the separate `jobapps` repo) copied into this repo per Shaun's request, so it lives alongside the resume it feeds. Explicitly *not* wired into generation — hand-maintained reference to pull additional bullets from, not a second source of truth.
- [x] 21 new unit tests (`tests/test_lib_resume.py`, `tests/test_gen_resume.py`) — link/code/dcurves-token rendering in both HTML and text modes, marker injection/idempotency, education entries with/without a `sub` line. Full suite now 49 tests.
- [x] Updated `docs/development.md` ("Updating the resume" section) and the new README "Conventions" section to point future edits at `data/resume.json`, never at the generated HTML block directly.

## Product Decisions

- **Full site migration, not resume-only:** Shaun explicitly chose the larger scope over a resume-only static page, accepting the larger effort to fully drop Quarto/R/Python tooling from the personal site.
- **Executed-code posts are frozen, not dropped:** existing rendered output for `best-resume-builder` and `python-package-automation` is preserved as static HTML rather than deleted or re-executed.
- **New branch off `main`, independent of PR #3:** this work is unrelated to the (now-merged) 3D print shop scaffolding, so it branches cleanly from `main` rather than stacking on that work.
- **Resume PDF stays available for job portals:** the site's HTML resume is the source; Shaun exports to PDF himself (browser print-to-PDF) for job-portal submissions rather than maintaining a second generated-PDF pipeline.
- **Nav stays DRY via a pre-commit sync script, not hand duplication:** `templates/nav.html` is the single source of truth, stamped into every page by `scripts/sync-nav.py` (run from `.githooks/pre-commit`). Rejected both hand-duplicating the nav block across 14 files (drifts out of sync) and a runtime include/fetch (breaks when opening pages via `file://`, which Shaun does directly for the resume). Served pages remain plain static HTML with zero runtime templating.
- **CI swaps mechanism, not destination:** the new `publish.yaml` still deploys to the `gh-pages` branch (via `peaceiris/actions-gh-pages` instead of `quarto publish`), so no GitHub Pages repo-settings change is required — avoids an extra production-infrastructure mutation beyond what this PR already needs.
- **Published content isolated to `site/`:** Shaun wants the repo root itself to be immediately legible — one glance should separate "the website" from "the tooling that maintains it." `site/` is the entire publish surface; `templates/`, `scripts/`, `docs/` are repo-only and never ship.

## Scope

- New `/resume` page built from reconciled experience data.
- Minimal shared nav/header + base CSS with no framework.
- Migration of `about`, `stuff`, `index`, and all `posts/` pages to static HTML.
- Replacement of the Quarto publish workflow with a plain static-file deploy.
- Removal of all Quarto/renv/Python/R tooling from the repo.

## Non-Goals

- No new design system, component library, or CSS framework — deliberately minimal.
- No dynamic/generated PDF pipeline for the resume — manual browser export is sufficient.
- No changes to the 3D print shop feature (separate, future PR).
- No changes to DNS/CNAME or hosting provider.

## Related Docs

- [PR 3: Zero-Overhead 3D Print Shop & Multi-Channel Sales Funnel](./3-3d-print-shop.md) — unrelated scope, merged to `main` before this branch was cut.
