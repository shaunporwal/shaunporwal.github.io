# PR 13: Resume in the Site Theme, With a PDF Download

Status: underway

Branch: `feature/resume-in-theme`

## Goal

`/resume.html` stays the one link to share. It now looks like the rest of the site: shared header, footer and theme, in the light and the dark mode. A Download PDF button gives a PDF of the same page. The publish workflow prints the PDF, so it never drifts from `data/experiences.json` and git never holds it.

## Context

- Shaun, 2026-10-27: sharing a link is simple now. A PDF would save four to six steps. He said "yes, do it".
- `resume.html` was a standalone page with its own inline styles, no header and no footer. The reader printed it by hand.
- The page serves copy and paste into LinkedIn. The markup keeps the dash text, the spacer between bullets and the block `div` bullets.
- The print layout test used `npx --yes playwright pdf`. That path differed from what a browser prints, because Playwright sets its own margins.

## Implementation Checklist

Ordered from least consequential to most consequential. Tests come first.

### Tier 1 - One name for the PDF

- [x] Test, then add a `pdf` key to the page schema and to the resume entry in `data/pages.json`. Add `pdf_pages` and `pdf_of` to `scripts/lib_site.py`.
- [x] Test, then set the resume `nav` switch on and the nav link to the same tab.

### Tier 2 - The page

- [x] Test, then rename the resume heading class to `resume-heading`, because `.section` is a site class. Update `scripts/lib_pagebreaks.py`.
- [x] Test, then let `scripts/lib_resume.py` open each link in a new tab. The page no longer sets a base target.
- [x] Test, then change `scripts/gen_resume.py`: drop the print note, add the Download PDF button, and name the downloaded file after the person.
- [x] Move the page onto the theme: `site/styles/resume.css` reads the site tokens. The page gets `<main id="main">`, the nav block and the footer block.
- [x] Test that the print rules hide the header, the footer and the button, and use a light palette. Test that every stylesheet holds no color literal outside `:root`.
- [x] Test, then make the home Resume button open in the same tab.

### Tier 3 - The PDF

- [x] Test, then add `scripts/render_pdf.py`: it finds Chrome, prints each page that names a PDF, and logs a stable event on failure.
- [x] Add `make pdf`. Add `/site/resume.pdf` to `.gitignore`.
- [x] Print the PDF in `.github/workflows/publish.yaml` before the publish step.
- [x] Test that the button, `.gitignore`, `make pdf` and the workflow follow the one name in `data/pages.json`. Test that no discovery file lists the PDF and that git tracks no PDF.
- [x] Print the layout test with the same script. Remove the Node and Playwright steps from `.github/workflows/test.yaml`.
- [x] Update `docs/development.md`, `site/AGENTS.md`, `tests/AGENTS.md`, `data/AGENTS.md` and the root `AGENTS.md`.

## Smoke Tests

- [x] Open `/resume.html` at 360, 390, 430, 820 and 1440 px in the light and the dark mode. The header and footer show. The page has no sideways scroll. The button is 44 px high.
- [x] Open the phone menu. The Resume link is current and opens in the same tab.
- [x] Run `make pdf`. The PDF has two pages and selectable text. It shows no header, no footer and no button. Its links work.
- [ ] After the merge, open `https://www.shaunporwal.com/resume.pdf`. It returns 200 and `application/pdf`.
- [ ] After the merge, press Download PDF on the live page. The file is named `Shaun-Porwal-Resume.pdf`.

## Product Decisions

- The PDF keeps the printed look of the old resume: sans type, dark ink and blue titles on white. The page margin is 0.5 in. The page size is the browser default.
- The PDF is printed at publish and never committed. A committed PDF can drift from the data.
- The heading class changed from `section` to `resume-heading`. The site stylesheet already uses `.section` for page bands.
- External links in the resume open in a new tab, as before. Each link now says so, because the page no longer sets `<base target>`.
- The Chrome finder also accepts the Chromium that Playwright downloaded, so `make test` and `make pdf` work on a machine with no Google Chrome.
- CI and the publish step run Chrome with `--no-sandbox`. The runner is a throwaway machine and the page is ours.

## Scope

- The resume page, its stylesheet, the PDF script and its checks, and the docs for them.

## Non-Goals

- No change to the experience data or the resume wording.
- No PDF in the sitemap, `llms.txt` or any other discovery file.
- No analytics on the PDF download.

## Related Docs

- [PR 5: Resume Wording Fixes](./archive/5-resume-wording-fixes.md)
- [PR 4: Rebuild as Plain Static HTML + Resume Page](./archive/4-static-resume-site.md)
