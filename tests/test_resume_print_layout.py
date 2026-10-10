"""Renders site/resume.html to a PDF with Chromium and checks where pages break.

The resume has no page limit. It must never split an entry or a short
section across pages, or leave a heading alone at the bottom of a page.
Needs `npx` (Playwright) and `pdftotext` (poppler). Skips without them locally;
fails in CI, where they must exist.
"""
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

import context
from lib_pagebreaks import blocks_from_html, find_problems

RESUME_PATH = context.REPO_ROOT / "site" / "resume.html"
CHROMIUM_HINT = "If Chromium is missing, run: npx playwright install chromium"


def render_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path) -> None:
    command = ["npx", "--yes", "playwright", "pdf", html_path.as_uri(), str(pdf_path)]
    subprocess.run(command, check=True, capture_output=True, text=True)


def pdf_text(pdf_path: pathlib.Path) -> str:
    command = ["pdftotext", "-layout", str(pdf_path), "-"]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def printed_resume_text() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = pathlib.Path(tmp) / "resume.pdf"
        render_pdf(RESUME_PATH, pdf_path)
        return pdf_text(pdf_path)


class TestResumePrintLayout(unittest.TestCase):
    def setUp(self):
        missing = [tool for tool in ("npx", "pdftotext") if shutil.which(tool) is None]
        if missing and os.environ.get("CI"):
            self.fail(f"CI must provide: {', '.join(missing)}")
        if missing:
            self.skipTest(f"needs {', '.join(missing)} (npx comes with Node, pdftotext with poppler)")

    def test_every_section_is_wrapped_so_the_check_sees_it(self):
        page_html = RESUME_PATH.read_text()
        headings = [b for b in blocks_from_html(page_html) if b.kind == "heading"]
        self.assertEqual(len(headings), page_html.count('<h2 class="section"'))

    def test_page_breaks_never_split_a_block(self):
        blocks = blocks_from_html(RESUME_PATH.read_text())
        try:
            text = printed_resume_text()
        except subprocess.CalledProcessError as error:
            self.fail(f"PDF render failed. {CHROMIUM_HINT}\n{error.stderr[-400:]}")
        self.assertEqual(find_problems(text, blocks), [])


if __name__ == "__main__":
    unittest.main()
