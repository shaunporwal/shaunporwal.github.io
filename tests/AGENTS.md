# tests/

This directory holds the unit tests for `scripts/`, the lint checks, and the resume print layout check. Run all of them with `make test`.

## Files

- `context.py`: puts `scripts/` on the import path and holds the shared fixtures. Every test file imports it first.
- `test_<module>.py`: the tests for `scripts/<module>.py`.
- `test_code_shape.py`: fails on a nested function or a lambda in `scripts/` or `tests/`.
- `test_css_tokens.py`: fails on a color literal outside a `:root` block in any stylesheet in `site/styles/`.
- `test_media_refs.py`: fails if a file in `site/media/` is not used by a page, the stylesheet, or a data file.
- `test_site_contract.py`: fails if a page has no `<main id="main">`, or if a discovery file or structured data holds the email address.
- `test_media_sizes.py`: fails if a rendered icon or the social image has the wrong size, or if a card picture is over its size budget.
- `test_site_cards.py`: fails if a Work card has no picture file, differs from the data, says "software", holds an email address or claims compliance.
- `test_card_css.py`: fails if the card picture rules lose the 16:10 plate, a token color, or the reduced motion switch.
- `test_motion_pictures.py`: fails if `site/js/motion.js` loses the on-screen, visible-tab, reduced motion and `saveData` rules for the card pictures.
- `test_theme_contrast.py`: fails if a theme color pair falls below WCAG AA in the light or dark mode.
- `test_js_shape.py`: fails if `site/js/` breaks the code-shape rules.
- `test_agents_docs.py`: fails if a top-level directory has no `AGENTS.md`, or if the root `AGENTS.md` does not link to it.
- `test_resume_print_layout.py`: prints the real resume to PDF with Chrome, through the same code as the publish step, reads it with `pdftotext`, and checks the page breaks.
- `pdf_support.py`: prints the real resume to PDF once per run and reads it with poppler's tools. The PDF tests share it.
- `test_resume_pdf_matches_record.py`: prints the real resume to PDF and fails if the PDF lacks an item of the resume view, holds an item that the record keeps off the resume, reads out of the order of the page, breaks a heading into letters, is not Letter size, is over the page limit, or embeds a typeface that `site/fonts/` does not ship.
- `test_lib_pdfcheck.py`: tests the pure checks behind it, in `scripts/lib_pdfcheck.py`.
- `test_render_pdf.py`: tests how `scripts/render_pdf.py` finds Chrome, builds its command and reports a failure.
- `test_resume_pdf.py`: fails if the download button, `.gitignore`, `make pdf`, the publish workflow and the discovery files disagree on the one PDF that `data/pages.json` names, or if git tracks a PDF.
- `test_resume_css.py`: fails if the print rules stop hiding the site header, the footer and the download button, or if the font files, the stylesheet and the preload links disagree.
- `test_update_dcurves_downloads.sh`: checks the dcurves download count updater.

## Rules

- Write a failing test before you change behavior.
- Use `context.temp_repo(self)` for a temporary repo. It has `site/`, a fake `data/site.json`, and a fake `data/pages.json`. Add `context.write_record_fixture` when a test needs the experience record.
- Use the shared fixtures in `context.py`. Do not copy a fixture into a test file.
- A test that changes the output of `make sync` must also change the matching source in `data/` or `templates/`.
- The resume PDF checks need Chrome and poppler (`pdftotext`, `pdfinfo` and `pdffonts`). `scripts/render_pdf.py` finds Chrome: set `CHROME` to use another binary. Install poppler without asking (`brew install poppler`). CI uses the runner's Google Chrome and installs poppler in `.github/workflows/test.yaml`.
