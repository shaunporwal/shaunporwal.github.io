"""One source names the resume PDF: the resume entry in data/pages.json. The download button, the .gitignore
line, `make pdf` and the publish step all follow it, and no discovery file lists it."""
import re
import subprocess
import unittest

import context
from lib_site import load_pages, pdf_of
from test_site_contract import DISCOVERY_FILES

RENDER_SCRIPT = "scripts/render_pdf.py"
SITE_DIR = context.REPO_ROOT / "site"
PDF_NAME = pdf_of(load_pages(context.REPO_ROOT), "resume.html")
MAKE_RECIPE = re.compile(r"^pdf:\n((?:\t.*\n?)+)", re.MULTILINE)


def make_recipe(makefile: str) -> str:
    match = MAKE_RECIPE.search(makefile)
    return match.group(1) if match else ""


def publish_steps(workflow: str) -> list[str]:
    return workflow.split("      - name: ")[1:]


def tracked_pdfs() -> list[str]:
    command = ["git", "ls-files", "site/*.pdf"]
    return subprocess.run(command, cwd=context.REPO_ROOT, check=True, capture_output=True, text=True).stdout.split()


def step_running(steps: list[str], command: str) -> int:
    return next((index for index, step in enumerate(steps) if command in step), -1)


class TestResumePdf(unittest.TestCase):
    def test_finds_the_recipe_of_the_pdf_target(self):
        self.assertEqual(make_recipe("a:\n\tx\n\npdf:\n\t$(PYTHON) y\n\nb:\n\tz\n"), "\t$(PYTHON) y\n")

    def test_the_resume_download_button_links_to_the_pdf(self):
        self.assertIn(f'href="{PDF_NAME}"', (SITE_DIR / "resume.html").read_text())

    def test_git_ignores_the_pdf(self):
        lines = (context.REPO_ROOT / ".gitignore").read_text().splitlines()
        self.assertIn(f"/site/{PDF_NAME}", lines)

    def test_make_pdf_runs_the_render_script(self):
        self.assertIn(RENDER_SCRIPT, make_recipe((context.REPO_ROOT / "Makefile").read_text()))

    def test_the_publish_workflow_prints_the_pdf_before_it_publishes(self):
        steps = publish_steps((context.REPO_ROOT / ".github" / "workflows" / "publish.yaml").read_text())
        printing, publishing = step_running(steps, RENDER_SCRIPT), step_running(steps, "actions-gh-pages")
        self.assertGreaterEqual(printing, 0, "no publish step runs the render script")
        self.assertLess(printing, publishing)

    def test_the_publish_workflow_does_not_restate_the_pdf_name(self):
        workflow = (context.REPO_ROOT / ".github" / "workflows" / "publish.yaml").read_text()
        self.assertNotIn(".pdf", workflow)

    def test_no_discovery_file_lists_the_pdf(self):
        listed = [name for name in DISCOVERY_FILES if PDF_NAME in (SITE_DIR / name).read_text()]
        self.assertEqual(listed, [])

    def test_git_tracks_no_pdf(self):
        self.assertEqual(tracked_pdfs(), [], "Remove the PDF from git. The publish step prints it.")


if __name__ == "__main__":
    unittest.main()
