# PR 5: Resume Wording Fixes, NTU Research Entry, and One Experience Record

Status: done

Branch: `fix/resume-wording`

## Goal

Make the resume text match the real status of each claim. Fix two overclaims, shorten one bullet, merge the duplicate scholarship line, and add the NTU research entry.

## Context

At the start of this PR, `site/resume.html` was generated from `data/resume.json`. Tiers 1 to 3 edit that file. Tier 4 replaces it with `data/experiences.json`.

Two lines currently overclaim. Junto bullet 1 says "full regulatory compliance". The Domain skill says "Chemical regulatory compliance / ISO", but ISO certification is still in progress.

The Rutgers entry and the National Taiwan University (NTU) entry both show a Taiwan Ministry of Education (MOE) scholarship. Shaun confirms both lines name the same scholarship.

The NTU research work is not on the resume. The resume markup has no italic token, so the species name needs a small parser change.

The resume had a test that capped the print at 2 pages. Shaun removed that cap. The resume has no page limit. The rule is clean page breaks instead.

Today the Selected Projects section splits across pages. One project stays on page 1 and the rest move to page 2. A print layout check must catch this. The check needs Playwright Chromium and `pdftotext`.

The personal record `docs/all-experiences.md` held the same stale scholarship facts. It listed the Huayu line under Rutgers. It also said "MOE Full Scholarship" for NTU. An earlier resume fix already removed "Full" because the scholarship was not a full one.

## Implementation Checklist

Ordered from least consequential/complex to highest blast radius. Follow TDD:
write the focused failing test before implementing changed behavior.

### Tier 1 — Wording changes in `data/resume.json`

- [x] Junto bullet 1: replace "with full regulatory compliance and version-controlled document provenance" with "with regulatory document management and version-controlled provenance".
- [x] Skills, Domain: replace "Chemical regulatory compliance / ISO" with "Chemical inventory and regulatory documentation (ISO certification in progress)".
- [x] Junto bullet 2: replace the whole bullet with "Built a self-hosted **multi-agent AI system** (local LLMs via vLLM/llama.cpp, scheduled runs, evals) for **market research** and **competitive analysis**; delivered a full ICP/GTM report and verified competitor benchmarks".
- [x] Education: delete the `sub` line from the Rutgers entry. Set the NTU `sub` line to "Huayu Enrichment Scholarship, Taiwan Ministry of Education (MOE)". This replaces "MOE Scholarship recipient".
- [x] `docs/all-experiences.md`: move the Huayu line from the Rutgers block to the NTU block. Replace "MOE Full Scholarship recipient".
- [x] Make `AGENTS.md` the real instruction file. It was a symlink to `CLAUDE.md`. Delete `CLAUDE.md`.
- [x] `AGENTS.md`: record four rules. Open the PR at once. Install check tools without asking. Keep `docs/all-experiences.md` in sync. Treat hook-made changes as normal.
- [x] Delete `tests/test_resume_page_count.sh`. The new print layout check in Tier 2 replaces it.
- [x] Run `make sync`. Check that the diff of `site/resume.html` shows only these four changes. The pre-commit hook also refreshes the dcurves download count. Ignore that change.

### Tier 2 — Italic token in the resume markup

- [x] Write failing tests in `tests/test_lib_resume.py`: `*text*` renders `<em>` in HTML, renders bare text in plain text, escapes its content, and does not break `**bold**`.
- [x] Add the `*text*` token to `scripts/lib_resume.py`. Update the module docstring. Match `**bold**` before `*italic*`. Replace the `if`/`elif` chains on token type with tables of named handlers.
- [x] Run `make test`. All existing tests must pass.

### Tier 2b — Clean page breaks

- [x] Write failing tests in `tests/test_lib_pagebreaks.py`. An entry must not split. A heading must not sit alone at the end of a page. A short section must not split. Only Experience may span pages, between entries.
- [x] Add `scripts/lib_pagebreaks.py` with the pure break checks.
- [x] Write failing generator tests. Then wrap each section in `<section class="resume-section">` in `scripts/gen_resume.py`. Mark Experience as `resume-section-long`.
- [x] Add the print rules `.resume-section` and `.resume-section-long` to `site/resume.html`.
- [x] Add `tests/test_resume_print_layout.py`. It renders the real PDF with Chromium, reads it with `pdftotext`, and runs the checks. It fails in CI when a tool is missing.
- [x] Install `poppler-utils` in `.github/workflows/test.yaml`. Update `docs/development.md`. Remove the old test from the `Makefile`.

### Tier 3 — NTU research entry

- [x] Shaun confirms the entry details. Final details merge the AI draft with `docs/all-experiences.md`.
- [x] Add one Experience entry between "Inorganic Manufacturing Associate — SPEX CertiPrep" and "Quality Control Intern — Tokyo Chemical Industry". The list stays in reverse-chronological order.
- [x] Entry format: title "Research Intern", org "Lab of Prof. Jiun-Hong Chen, National Taiwan University", meta "Aug 2017 · Taipei, Taiwan", one bullet.
- [x] Bullet text: "Studied gene expression during regeneration in the freshwater annelid *Aeolosoma viride* using **whole-mount in situ hybridization**".
- [x] Update the NTU entry in `docs/all-experiences.md` to match.
- [x] Run `make sync` and `make test`. The page count may grow. The print layout check must pass.

### Tier 4 — One experience record

Shaun wants one source of truth for all experience facts. A flag on each item selects what goes on the resume.

- [x] Add `data/experiences.schema.json`. It declares the record format as JSON Schema.
- [x] Write failing tests in `tests/test_lib_schema.py`. Then add `scripts/lib_schema.py`, a small validator for the JSON Schema subset that the record uses. The repo has no third-party packages.
- [x] Write failing tests in `tests/test_lib_record.py`. Then add `scripts/lib_record.py`. It loads and validates the record, formats dates, and builds the resume view.
- [x] The `resume` key is the switch. `true` puts an item on the resume as it is. A string or an object replaces the text or fields on the resume only.
- [x] Add `data/experiences.json`. Move every fact from `data/resume.json` and `docs/all-experiences.md` into it. Delete `data/resume.json`.
- [x] Point `scripts/gen_resume.py` at the resume view. The resume output must not change, except the NTU bullet.
- [x] Write failing tests in `tests/test_gen_record.py`. Then add `scripts/gen_record.py`. It generates the record block in `docs/all-experiences.md`.
- [x] Remove the phone number. The resume does not show it.
- [x] NTU entry: add the presentation and the Mandarin facts. Use one resume bullet for the entry.
- [x] Run `gen_record.py` from `make sync` and the pre-commit hook. Stage `docs/all-experiences.md` in the hook.
- [x] Update `AGENTS.md` and `docs/development.md`.
- [x] Run `make sync` and `make test`. The print layout check must pass.

### Tier 5 — Lint

- [x] Add `ruff.toml` with limits on complexity, statements, branches, arguments, returns, and nested blocks. Add the inline SQL check. Pin the ruff version.
- [x] Add `tests/test_code_shape.py`. It fails on a nested function or a lambda in `scripts/` or `tests/`.
- [x] Restructure every function over a limit: `parse_post`, `all_posts`, `render_plaintext`, `sync_seo.sync`, and `sync_social.sync`. Do not raise a limit.
- [x] Add `make lint`. `make test`, the pre-commit hook, and CI run it.
- [x] Check that `make sync` leaves `site/` unchanged after the restructure.
- [x] `AGENTS.md`: keep follow-up work in the current PR unless Shaun asks for a new one.

### Tier 6 — Shared abstractions

Every change in this tier keeps the output the same. After each step, `make sync` must leave `site/` and `docs/all-experiences.md` unchanged.

- [x] Remove the unused `except ImportError` import fallback from every script.
- [x] Remove the second copy of `TAG_RE`. Keep `strip_tags` in one module.
- [x] Add `REPO_ROOT` to `scripts/lib_site.py`. Every `main()` uses it. Every `sync()` takes `repo_root`.
- [x] Add one temporary-repo helper to `tests/context.py`. The tests use it instead of their own setup.
- [x] Make the pre-commit hook run `make -k sync`. The Makefile is the only list of generators and their order. Split `sync` into one target per generator, so one failure does not stop the others.
- [x] Write failing tests in `tests/test_lib_blocks.py`. Then add `scripts/lib_blocks.py` with `wrap`, `replace_block`, and `write_if_changed`. A block that contains a backslash must not crash.
- [x] Move every generator to `lib_blocks.py`.
- [x] Add `data/pages.json` with each top-level page and its SEO, sitemap, and nav settings. `sync_seo.py`, `gen_sitemap.py`, and `sync_nav.py` read it.
- [x] Run `make lint` and `make test`.

### Tier 7 — SEO and AI SEO

The audit found these problems on the live site:

- `shaunporwal.com` redirects (301) to `www.shaunporwal.com`. Every canonical URL, `og:url`, sitemap entry, and the `robots.txt` sitemap line points at the redirect.
- Draft posts are reachable and have no `noindex` tag. Search engines can index them.
- Posts have no structured data, so search engines cannot read the date or the author.
- The default social image is 4.6 MB.
- `site/CNAME`, `site/robots.txt`, and `site/llms.txt` restate facts by hand: the host, the sitemap URL, the page list, the contact links, and the current role.
- `resume.html` has no favicon.

Checklist:

- [x] Set `base_url` in `data/site.json` to `https://www.shaunporwal.com`. Add `data/site.schema.json` and validate `site.json` at load time.
- [x] Write failing tests. Then make `sync_seo.py` add `noindex` to drafts and `BlogPosting` structured data to published posts.
- [x] Write failing tests. Then add `scripts/gen_crawler_files.py`. It generates `site/CNAME`, `site/robots.txt`, and `site/llms.txt` from the data files and the posts.
- [x] Add a 1200-pixel social image, `site/media/og-image.jpg`, and use it as the default.
- [x] Add the favicon to `resume.html`.
- [x] Run `make sync`, `make lint`, and `make test`.

### Tier 8 — Agent instructions

- [x] Rewrite the root `AGENTS.md` so that an agent with no other context can learn the repo from it.
- [x] Add an `AGENTS.md` to each top-level directory: `data/`, `docs/`, `scripts/`, `site/`, `templates/`, and `tests/`.
- [x] Write failing tests. Then add `scripts/gen_script_index.py`. It generates the script list in `scripts/AGENTS.md` from each script's docstring. Remove the hand-written table in `docs/development.md`.
- [x] Add a test that every top-level directory has an `AGENTS.md`, and that the root `AGENTS.md` links to each one.

### Tier 9 — Palette, 3D files, and the last driftable literals

- [x] Replace the site palette with the colours.cafe palette: navy (`#3a3f58`) background, cream (`#ece6cd`) text, apricot (`#f9ac67`) links, and coral (`#ee6a59`) accents, with no gradient. Shaun rejected the first try, a dark gradient palette, because it looked like a disco. Put every color in a `:root` token in `site/styles/site.css`. The resume keeps its print palette.
- [x] Add a test that fails on a color literal outside `:root` in `site/styles/site.css`.
- [x] Move every `.glb`, `.blend`, and `.blend1` file from `site/media/` to `projects/website-models/` in the `3d-printing-lab` repo, through a branch and a PR there (3d-printing-lab PR 8).
- [x] Remove the 3D model gallery and the `model-viewer` script from `stuff.html`. Update its description in `data/pages.json`.
- [x] Write failing tests. Then let a resume contact item name a `data/site.json` key instead of a literal value. Remove the copied email, website, GitHub, and LinkedIn values from `data/experiences.json`.
- [x] Remove `name` from `data/experiences.json`. The resume and the record use the name in `data/site.json`.
- [x] Write failing tests. Then make `sync_seo.py` generate each page's `<title>` from the same title as its SEO tags.
- [x] Write failing tests. Then generate the nav's page links from `data/pages.json`. Add a `menu` entry to each page that shows in the nav.
- [x] Replace the heron with Shaun's headshot: a 360-pixel square crop (`media/avatar.jpg`) on the About page, and the 1200-pixel headshot as the default social image (`media/og-image.jpg`).
- [x] Remove the unused files from `site/media/`: `heron.jpg`, `heron_no_background.png`, `porwal-resume.pdf`, `2015_ntu_mandarin_cert_and_grade.pdf`, `gravchamber_pics/`, and `gravitychamber.gif`.
- [x] Add `tests/test_media_refs.py`. It fails if a file in `site/media/` is not used.
- [x] Show the About page links as buttons, with the same style as the nav.
- [x] Run `make sync`, `make lint`, and `make test`.

## Smoke Tests

Manual checks Shaun performs in the rendered/previewed site.

- [ ] Run `make dev`. Open `/resume.html`. Each changed line shows the new wording.
- [ ] Open `/`, `/about.html`, `/stuff.html`, and one post. Each uses the navy, cream, apricot, and coral palette, and text is easy to read.
- [ ] Open the page at phone width. No horizontal scroll appears. The new entry wraps cleanly.
- [ ] Print to PDF. No entry, short section, or heading breaks across pages.
- [ ] Copy the page text into a plain-text field. The species name appears with no asterisks.
- [ ] Open `docs/all-experiences.md`. It shows every entry, including entries that are not on the resume.
- [ ] Change one bullet in `data/experiences.json` and commit. The resume and the record both show the change.
- [ ] After merge and publish, open `https://www.shaunporwal.com/robots.txt` and `/llms.txt`. Both name `www.shaunporwal.com`.
- [ ] After publish, paste a post URL into a link-preview tool. The preview shows the title and image.

## Product Decisions

- Edit `data/experiences.json`, never a generated block. That file is the single source of truth for the resume and for `docs/all-experiences.md`.
- The `resume` key on an item is the switch that puts it on the resume.
- Where the two old files disagreed, the resume value wins. "Resolved Conflicts" lists each case.
- Keep the Huayu scholarship line on the NTU entry only. Shaun confirms the Rutgers line and the NTU line name the same scholarship.
- Add an italic token to the parser instead of hand-writing HTML. All resume markup stays in one place.
- The resume has no page limit. Page breaks must be clean. Shaun set this rule.
- A short section moves whole to the next page. Only Experience may span pages, and only between entries.

## Confirmed Details

Shaun confirmed these details for the NTU entry. The date is August 2017. The PI is Prof. Jiun-Hong Chen. The work studied gene expression during regeneration with whole-mount in situ hybridization. *Aeolosoma viride* regenerates both halves after a cut.

The NTU work did not study NR2B. An earlier record put NR2B and self-depurination (SDP) under NTU by mistake. Both came from unpaid independent study with Prof. Fresco. That study did not produce a paper. It stays in `docs/all-experiences.md` only, and it does not go on the resume.

## Resolved Conflicts

The old resume file and the old record disagreed on these facts. The record now uses the resume value. Shaun confirmed each one.

- Location: "Metuchen, NJ" (the record said "New York, NY").
- Mount Sinai degree date: February 2021 (the record said March 2021).
- NTU certificate name: "Certificate in Advanced Mandarin Chinese" (the record said "Certificate in Advanced Chinese").
- Hindi: fluent (the record said native). Shaun was not raised in India, so "native" does not apply.
- Japanese: conversational (the record said basic/conversational).
- Spanish: conversational (the record said basic).

The no-more-sql project said "serving 50+ Data Scientists". That claim is removed. Shaun shared the tool, but usage was not tracked. Shaun built it from scratch as a prototype for an internal grant application. The grant was not awarded.

## Scope

- Four wording changes in `data/resume.json`.
- One new inline markup token (`*italic*`) with tests.
- One new Experience entry for the NTU research.
- One matching fix in `docs/all-experiences.md` for the scholarship facts.
- `AGENTS.md` as the only instruction file, with `CLAUDE.md` removed.
- Four workflow rules in `AGENTS.md`, from Shaun's corrections.
- A print layout check that replaces the 2-page cap test.
- One experience record, `data/experiences.json`, that generates the resume and `docs/all-experiences.md`.
- A ruff lint configuration and a code-shape check, run by `make test`, the pre-commit hook, and CI.
- Shared abstractions for marker blocks, the page list, and test setup, with no change to the output.
- SEO fixes, generated crawler files, and agent instructions in each directory.

## Non-Goals

- No change to layout, styles, links, dates, or any other resume text.
- No new claims beyond the confirmed NTU entry.
- No rewording of record bullets during the move. The record keeps its own wording.
- No new check that the Experience list stays in date order.

## Related Docs

- None.
