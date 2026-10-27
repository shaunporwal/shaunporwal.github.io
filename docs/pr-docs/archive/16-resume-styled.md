# PR 16: Styled Resume, One Source for the Page and the PDF

Status: done

Branch: `feature/resume-styled`

## Goal

Give the resume a designed look on the screen and in the PDF. One page of markup and one stylesheet must feed both, so the two cannot drift.

## Context

- Shaun, 2026-10-27: the PDF is the resume. Keep Letter size and keep the email address in the PDF. The page need not be a bland resume.
- PR 13 put the resume in the site theme and added the PDF print. The PDF looked plain and had no page limit.
- CI prints the PDF with the runner's Chrome. The runner has none of the fonts of this Mac.

## Implementation Checklist

### Tier 1 - Data and markup

- [x] The resume view holds `period` and `place` beside `meta`. `gen_resume.py` writes each in its own element. The dash bullets and the spacer stay.
- [x] `pdf_max_pages` in `data/pages.json` and its schema.

### Tier 2 - Look

- [x] Phone: one column. 768 px and up: a left rail of dates. Print: one column, dates at the right of the title row.
- [x] Inter and Source Serif 4 as static woff2 files in `site/fonts/`, with their licence texts and preload links.
- [x] Print: Letter, `@page` margin of 0.5 in by 0.6 in, accent headings, code chips.

### Tier 3 - Checks

- [x] `lib_pdfcheck.py` (pure) and `tests/test_resume_pdf_matches_record.py`: items present, no unlisted item, order, headings whole, Letter, page limit, embedded fonts.
- [x] `tests/test_resume_css.py`: font files, `@font-face` rules and preload links agree.
- [x] The CI step installs poppler (`pdftotext`, `pdfinfo`, `pdffonts`).

## Smoke Tests

Checks on the live site after the merge. An agent ran them at 360, 390, 820 and 1440 px and on the downloaded PDF.

- [x] **Resume on a phone** · open `/resume.html`
  1. Open the page at phone width.

  **Pass if:** one column, nothing scrolls sideways, and the Download PDF button is easy to tap.

- [x] **Resume on a desktop** · open `/resume.html`
  1. Open the page in a wide window.

  **Pass if:** dates sit in a rail at the left of each entry.

- [x] **PDF** · press Download PDF
  1. Open the PDF.

  **Pass if:** it has 2 Letter pages, the email address shows, and the text copies cleanly.

## Product Decisions

- The PDF is one column. A dates rail needed 3 pages. A rail stays for the screen only.
- The accent colors the section headings only. Orange organization names looked too heavy.
- The PDF keeps the email address. This is Shaun's choice. No other generated file holds it.
- Heading letter spacing in print stays below 0.1 em. At 0.1 em, `pdftotext` returns "S E L E C T E D".
- The fonts are third-party files under the SIL Open Font License (Inter 5.3.0, Source Serif 4 5.3.1 from fontsource).

## Scope

- The resume page, its stylesheet, the PDF print, the fonts, the data fields and the checks for them.

## Non-Goals

- No change to the text of the resume or to `data/experiences.json`.
- No italic font file. The browser synthesizes the italic.
- No colored links in the PDF. Links stay clickable.

## Related Docs

- [PR 13: Resume in the Site Theme, With a PDF Download](./13-resume-in-theme.md)
