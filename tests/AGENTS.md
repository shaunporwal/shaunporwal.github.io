# tests/

This directory holds the unit tests for `scripts/`, the lint checks, and the resume print layout check. Run all of them with `make test`.

## Files

- `context.py`: puts `scripts/` on the import path and holds the shared fixtures. Every test file imports it first.
- `test_<module>.py`: the tests for `scripts/<module>.py`.
- `test_code_shape.py`: fails on a nested function or a lambda in `scripts/` or `tests/`.
- `test_css_tokens.py`: fails on a color literal outside the `:root` block of `site/styles/site.css`.
- `test_media_refs.py`: fails if a file in `site/media/` is not used by a page, the stylesheet, or a data file.
- `test_agents_docs.py`: fails if a top-level directory has no `AGENTS.md`, or if the root `AGENTS.md` does not link to it.
- `test_resume_print_layout.py`: prints the real resume to PDF with Playwright Chromium, reads it with `pdftotext`, and checks the page breaks.
- `test_update_dcurves_downloads.sh`: checks the dcurves download count updater.

## Rules

- Write a failing test before you change behavior.
- Use `context.temp_repo(self)` for a temporary repo. It has `site/`, a fake `data/site.json`, and a fake `data/pages.json`. Add `context.write_record_fixture` when a test needs the experience record.
- Use the shared fixtures in `context.py`. Do not copy a fixture into a test file.
- A test that changes the output of `make sync` must also change the matching source in `data/` or `templates/`.
- The print layout check needs `npx` with Playwright Chromium and `pdftotext` (poppler). Install them without asking. CI installs them in `.github/workflows/test.yaml`.
