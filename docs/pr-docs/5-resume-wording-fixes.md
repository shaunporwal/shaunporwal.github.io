# PR 5: Resume Wording Fixes, NTU Research Entry, and One Experience Record

Status: underway

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

## Smoke Tests

Manual checks Shaun performs in the rendered/previewed site.

- [ ] Run `make dev`. Open `/resume.html`. Each changed line shows the new wording.
- [ ] Open the page at phone width. No horizontal scroll appears. The new entry wraps cleanly.
- [ ] Print to PDF. No entry, short section, or heading breaks across pages.
- [ ] Copy the page text into a plain-text field. The species name appears with no asterisks.
- [ ] Open `docs/all-experiences.md`. It shows every entry, including entries that are not on the resume.
- [ ] Change one bullet in `data/experiences.json` and commit. The resume and the record both show the change.

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

The old resume file and the old record disagreed on these facts. The record now uses the resume value. Shaun must check each one.

- Location: "Metuchen, NJ" (the record said "New York, NY").
- Mount Sinai degree date: February 2021 (the record said March 2021).
- NTU certificate name: "Certificate in Advanced Mandarin Chinese" (the record said "Certificate in Advanced Chinese").
- Hindi: fluent (the record said native).
- Japanese: conversational (the record said basic/conversational).
- Spanish: conversational (the record said basic).

The record keeps one internal conflict as it is. The no-more-sql project says "serving 50+ Data Scientists". The MSKCC entry says no usage data supports a user count.

## Scope

- Four wording changes in `data/resume.json`.
- One new inline markup token (`*italic*`) with tests.
- One new Experience entry for the NTU research.
- One matching fix in `docs/all-experiences.md` for the scholarship facts.
- `AGENTS.md` as the only instruction file, with `CLAUDE.md` removed.
- Four workflow rules in `AGENTS.md`, from Shaun's corrections.
- A print layout check that replaces the 2-page cap test.
- One experience record, `data/experiences.json`, that generates the resume and `docs/all-experiences.md`.

## Non-Goals

- No change to layout, styles, links, dates, or any other resume text.
- No new claims beyond the confirmed NTU entry.
- No rewording of record bullets during the move. The record keeps its own wording.
- No new check that the Experience list stays in date order.

## Related Docs

- None.
