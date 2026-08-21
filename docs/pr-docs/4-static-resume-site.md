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
- [x] No leftover references to Quarto/R/Python in build docs, CI, or CLAUDE.md (repo-wide grep clean except frozen historical post prose and PR #3's own historical description, both left as accurate-at-the-time records).

## Product Decisions

- **Full site migration, not resume-only:** Shaun explicitly chose the larger scope over a resume-only static page, accepting the larger effort to fully drop Quarto/R/Python tooling from the personal site.
- **Executed-code posts are frozen, not dropped:** existing rendered output for `best-resume-builder` and `python-package-automation` is preserved as static HTML rather than deleted or re-executed.
- **New branch off `main`, independent of PR #3:** this work is unrelated to the (now-merged) 3D print shop scaffolding, so it branches cleanly from `main` rather than stacking on that work.
- **Resume PDF stays available for job portals:** the site's HTML resume is the source; Shaun exports to PDF himself (browser print-to-PDF) for job-portal submissions rather than maintaining a second generated-PDF pipeline.
- **Nav stays DRY via a pre-commit sync script, not hand duplication:** `templates/nav.html` is the single source of truth, stamped into every page by `scripts/sync-nav.py` (run from `.githooks/pre-commit`). Rejected both hand-duplicating the nav block across 14 files (drifts out of sync) and a runtime include/fetch (breaks when opening pages via `file://`, which Shaun does directly for the resume). Served pages remain plain static HTML with zero runtime templating.
- **CI swaps mechanism, not destination:** the new `publish.yaml` still deploys to the `gh-pages` branch (via `peaceiris/actions-gh-pages` instead of `quarto publish`), so no GitHub Pages repo-settings change is required — avoids an extra production-infrastructure mutation beyond what this PR already needs.

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
