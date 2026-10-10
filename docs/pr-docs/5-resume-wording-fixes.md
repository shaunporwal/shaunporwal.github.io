# PR 5: Resume Wording Fixes and NTU Research Entry

Status: underway

Branch: `fix/resume-wording`

## Goal

Make the resume text match the real status of each claim. Fix two overclaims, shorten one bullet, merge the duplicate scholarship line, and add the NTU research entry.

## Context

The resume page `site/resume.html` is generated from `data/resume.json`. The change must go in the JSON file, then `make sync` regenerates the HTML.

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

### Tier 3 — NTU research entry (blocked until Shaun confirms the details)

- [ ] Shaun confirms the entry details listed under Open Items.
- [ ] Add one Experience entry between "Inorganic Manufacturing Associate — SPEX CertiPrep" and "Quality Control Intern — Tokyo Chemical Industry". The list stays in reverse-chronological order.
- [ ] Entry format: title "Research Intern", org "Lab of Prof. Jiun-Hong Chen, National Taiwan University", meta "Summer 2017 · Taipei, Taiwan", one bullet.
- [ ] Bullet text: "Performed whole-mount in situ hybridization to map gene expression during regeneration in the freshwater annelid *Aeolosoma viride*".
- [ ] Run `make sync` and `make test`. The page count may grow. The print layout check must pass.

## Smoke Tests

Manual checks Shaun performs in the rendered/previewed site.

- [ ] Run `make dev`. Open `/resume.html`. Each changed line shows the new wording.
- [ ] Open the page at phone width. No horizontal scroll appears. The new entry wraps cleanly.
- [ ] Print to PDF. No entry, short section, or heading breaks across pages.
- [ ] Copy the page text into a plain-text field. The species name appears with no asterisks.

## Product Decisions

- Edit `data/resume.json`, never the generated block in `site/resume.html`. The JSON file is the single source of truth.
- Keep the Huayu scholarship line on the NTU entry only. Shaun confirms the Rutgers line and the NTU line name the same scholarship.
- Add an italic token to the parser instead of hand-writing HTML. All resume markup stays in one place.
- The resume has no page limit. Page breaks must be clean. Shaun set this rule.
- A short section moves whole to the next page. Only Experience may span pages, and only between entries.

## Open Items

Shaun must confirm these details before Tier 3 starts. Shaun gave the PI surname "Chen". A second AI tool supplied the other details. No one has verified them.

- Full PI name: "Jiun-Hong Chen".
- Dates: "Summer 2017".
- Method: whole-mount in situ hybridization.
- Subject: gene expression during regeneration in *Aeolosoma viride*.
- Title: "Research Intern".

If Shaun does not confirm the details, Tier 3 does not ship. Tiers 1 and 2 still ship.

## Scope

- Four wording changes in `data/resume.json`.
- One new inline markup token (`*italic*`) with tests.
- One new Experience entry, after confirmation.
- One matching fix in `docs/all-experiences.md` for the scholarship facts.
- `AGENTS.md` as the only instruction file, with `CLAUDE.md` removed.
- Four workflow rules in `AGENTS.md`, from Shaun's corrections.
- A print layout check that replaces the 2-page cap test.

## Non-Goals

- No change to layout, styles, links, dates, or any other resume text.
- No new claims beyond the confirmed NTU entry.
- No other change to `docs/all-experiences.md`. The Junto, skills, and NTU research wording stay as they are in that record.
- No new check that the Experience list stays in date order.

## Related Docs

- None.
