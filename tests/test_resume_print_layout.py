"""Prints site/resume.html to a PDF with the same Chrome and code as the publish step, and checks where pages break.

The resume has no page limit. It must never split an entry or a short
section across pages, or leave a heading alone at the bottom of a page.
Needs Chrome (see scripts/render_pdf.py for where it looks) and `pdftotext` (poppler).
Skips without them locally; fails in CI, where they must exist.
"""
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

import context
import render_pdf
from lib_pagebreaks import blocks_from_html, find_problems

RESUME_PATH = context.REPO_ROOT / "site" / "resume.html"
PROFILE_FLAG = "--user-data-dir={}"


def pdf_text(pdf_path: pathlib.Path) -> str:
    command = ["pdftotext", "-layout", str(pdf_path), "-"]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def printed_resume_text(chrome: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = pathlib.Path(tmp) / "resume.pdf"
        flags = (*render_pdf.extra_flags(os.environ), PROFILE_FLAG.format(pathlib.Path(tmp) / "profile"))
        render_pdf.run_job(render_pdf.PrintJob(chrome, flags, RESUME_PATH, pdf_path), subprocess.run)
        return pdf_text(pdf_path)


def missing_tools() -> tuple[str | None, list[str]]:
    """The Chrome binary, or None, and the names of the tools that are missing."""
    try:
        chrome = render_pdf.find_chrome(os.environ, shutil.which, pathlib.Path.home())
    except render_pdf.ChromeNotFound:
        chrome = None
    missing = [] if chrome else ["Chrome"]
    return chrome, missing + ([] if shutil.which("pdftotext") else ["pdftotext"])


class TestResumePrintLayout(unittest.TestCase):
    def setUp(self):
        self.chrome, missing = missing_tools()
        if missing and os.environ.get("CI"):
            self.fail(f"CI must provide: {', '.join(missing)}")
        if missing:
            self.skipTest(f"needs {', '.join(missing)} (pdftotext comes with poppler)")

    def test_every_section_is_wrapped_so_the_check_sees_it(self):
        page_html = RESUME_PATH.read_text()
        headings = [b for b in blocks_from_html(page_html) if b.kind == "heading"]
        self.assertEqual(len(headings), page_html.count('<h2 class="resume-heading"'))

    def test_page_breaks_never_split_a_block(self):
        blocks = blocks_from_html(RESUME_PATH.read_text())
        try:
            text = printed_resume_text(self.chrome)
        except render_pdf.PrintFailed as error:
            self.fail(f"PDF render failed: {error}")
        self.assertEqual(find_problems(text, blocks), [])


if __name__ == "__main__":
    unittest.main()
