#!/usr/bin/env python3
"""Prints each page that names a `pdf` in data/pages.json to that PDF in site/, with headless Chrome.

The resume page names `resume.pdf`, so the PDF always matches the page. The publish workflow and
`make pdf` run this script. Nobody commits the PDF: `.gitignore` lists it.

- Chrome comes from the `CHROME` variable, then Google Chrome or Chromium on the PATH, then a Chrome
  app in /Applications, then the Chromium that Playwright downloaded. The script stops with a message
  when it finds none.
- `CHROME_ARGS` adds flags, for example `--no-sandbox` on a CI runner.
- Each run uses a fresh profile, so a Chrome that is already open cannot take the job.
"""
import glob
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from lib_site import REPO_ROOT, load_pages, pdf_pages

CHROME_VARIABLE = "CHROME"
ARGS_VARIABLE = "CHROME_ARGS"
PATH_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")
APP_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)
CACHE_GLOBS = (
    "Library/Caches/ms-playwright/chromium-*/chrome-mac*/*.app/Contents/MacOS/*",
    ".cache/ms-playwright/chromium-*/chrome-linux*/chrome",
)
FIXED_FLAGS = ("--headless", "--no-pdf-header-footer")
TIMEOUT_SECONDS = 120
STDERR_TAIL = 300
NOT_FOUND = f"No Chrome found. Install Google Chrome, or set {CHROME_VARIABLE} to a Chrome or Chromium binary."


class RenderError(Exception):
    """A failure with a stable event name for the log."""

    event = "render_pdf.failed"


class ChromeNotFound(RenderError):
    event = "render_pdf.chrome_not_found"


class PrintFailed(RenderError):
    event = "render_pdf.print_failed"


@dataclass(frozen=True)
class PrintJob:
    chrome: str
    flags: tuple[str, ...]
    page: pathlib.Path
    pdf: pathlib.Path


def from_variable(env: Mapping, which: Callable, home: pathlib.Path) -> str | None:
    return env.get(CHROME_VARIABLE)


def from_path(env: Mapping, which: Callable, home: pathlib.Path) -> str | None:
    return next(filter(None, map(which, PATH_NAMES)), None)


def from_apps(env: Mapping, which: Callable, home: pathlib.Path) -> str | None:
    return next((path for path in APP_PATHS if pathlib.Path(path).is_file()), None)


def from_playwright(env: Mapping, which: Callable, home: pathlib.Path) -> str | None:
    found = sorted(match for pattern in CACHE_GLOBS for match in glob.glob(str(home / pattern)))
    return found[-1] if found else None


SOURCES = (from_variable, from_path, from_apps, from_playwright)


def find_chrome(env: Mapping, which: Callable, home: pathlib.Path) -> str:
    """The Chrome binary to use. Raises ChromeNotFound when there is none."""
    for source in SOURCES:
        found = source(env, which, home)
        if found:
            return found
    raise ChromeNotFound(NOT_FOUND)


def extra_flags(env: Mapping) -> tuple[str, ...]:
    return tuple(shlex.split(env.get(ARGS_VARIABLE, "")))


def command(job: PrintJob) -> list[str]:
    return [job.chrome, *FIXED_FLAGS, *job.flags, f"--print-to-pdf={job.pdf}", job.page.as_uri()]


def failure_detail(job: PrintJob, error: Exception) -> str:
    stderr = getattr(error, "stderr", None) or ""
    return f"{job.page.name}: {type(error).__name__} {stderr[-STDERR_TAIL:]}".strip()


def has_output(pdf: pathlib.Path) -> bool:
    return pdf.is_file() and pdf.stat().st_size > 0


def run_job(job: PrintJob, run: Callable) -> None:
    """Prints one page. Raises PrintFailed when Chrome fails or writes no PDF."""
    try:
        run(command(job), check=True, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as error:
        raise PrintFailed(failure_detail(job, error)) from error
    if not has_output(job.pdf):
        raise PrintFailed(f"{job.page.name}: Chrome wrote no PDF")


def jobs_for(repo_root: pathlib.Path, chrome: str, flags: tuple[str, ...]) -> list[PrintJob]:
    site_dir = repo_root / "site"
    return [
        PrintJob(chrome, flags, site_dir / page["file"], site_dir / page["pdf"])
        for page in pdf_pages(load_pages(repo_root))
    ]


def render_all(repo_root: pathlib.Path, chrome: str, flags: tuple[str, ...], run: Callable) -> list[pathlib.Path]:
    """Prints every page that names a PDF. Returns the PDFs it wrote."""
    with tempfile.TemporaryDirectory() as profile:
        jobs = jobs_for(repo_root, chrome, (*flags, f"--user-data-dir={profile}"))
        for job in jobs:
            run_job(job, run)
    return [job.pdf for job in jobs]


def main() -> int:
    try:
        chrome = find_chrome(os.environ, shutil.which, pathlib.Path.home())
        written = render_all(REPO_ROOT, chrome, extra_flags(os.environ), subprocess.run)
    except RenderError as error:
        print(f"ERROR event={error.event} detail={error}", file=sys.stderr)
        return 1
    for pdf in written:
        print(f"wrote {pdf.relative_to(REPO_ROOT)} ({pdf.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
