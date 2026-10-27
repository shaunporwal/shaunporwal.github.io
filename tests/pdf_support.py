"""Prints site/resume.html to a PDF with the same Chrome and code as the publish step, once per test run,
and reads the PDF with poppler's tools. The PDF checks share it, so Chrome prints the page one time."""
import functools
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

import context
import render_pdf

RESUME_PATH = context.REPO_ROOT / "site" / "resume.html"
POPPLER_TOOLS = ("pdftotext", "pdfinfo", "pdffonts")
PROFILE_FLAG = "--user-data-dir={}"


def missing_tools() -> tuple[str | None, list[str]]:
    """The Chrome binary, or None, and the names of the tools that are missing."""
    try:
        chrome = render_pdf.find_chrome(os.environ, shutil.which, pathlib.Path.home())
    except render_pdf.ChromeNotFound:
        chrome = None
    absent = [name for name in POPPLER_TOOLS if not shutil.which(name)]
    return chrome, ([] if chrome else ["Chrome"]) + absent


def require_tools(test: unittest.TestCase) -> str:
    """The Chrome binary. Skips the test without the tools, and fails it in CI, where they must exist."""
    chrome, missing = missing_tools()
    if missing and os.environ.get("CI"):
        test.fail(f"CI must provide: {', '.join(missing)}")
    if missing:
        test.skipTest(f"needs {', '.join(missing)} (pdftotext, pdfinfo and pdffonts come with poppler)")
    return chrome


@functools.cache
def printed_pdf(chrome: str) -> bytes:
    """The resume page printed to a PDF. Raises render_pdf.PrintFailed when Chrome fails."""
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = pathlib.Path(tmp) / "resume.pdf"
        flags = (*render_pdf.extra_flags(os.environ), PROFILE_FLAG.format(pathlib.Path(tmp) / "profile"))
        render_pdf.run_job(render_pdf.PrintJob(chrome, flags, RESUME_PATH, pdf_path), subprocess.run)
        return pdf_path.read_bytes()


def run_poppler(command: list[str], pdf: bytes, tail: tuple[str, ...] = ()) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = pathlib.Path(tmp) / "resume.pdf"
        pdf_path.write_bytes(pdf)
        return subprocess.run([*command, str(pdf_path), *tail], check=True, capture_output=True, text=True).stdout


def layout_text(pdf: bytes) -> str:
    """The text with its place on the page kept, and a form feed between pages."""
    return run_poppler(["pdftotext", "-layout"], pdf, ("-",))


def plain_text(pdf: bytes) -> str:
    """The text in reading order, as a parser that reads columns and words would return it."""
    return run_poppler(["pdftotext"], pdf, ("-",))


def raw_text(pdf: bytes) -> str:
    """The text in the order the PDF stores it, which is the order of the page markup."""
    return run_poppler(["pdftotext", "-raw"], pdf, ("-",))


def info(pdf: bytes) -> str:
    return run_poppler(["pdfinfo"], pdf)


def fonts(pdf: bytes) -> str:
    return run_poppler(["pdffonts"], pdf)
