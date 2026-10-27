import pathlib
import subprocess
import unittest

import context
import render_pdf

PDF_FLAG = "--print-to-pdf="


def pdf_path_of(command: list[str]) -> pathlib.Path:
    flag = next(part for part in command if part.startswith(PDF_FLAG))
    return pathlib.Path(flag.removeprefix(PDF_FLAG))


def never_found(name: str) -> None:
    return None


def found_only(*names: str):
    return {name: f"/usr/bin/{name}" for name in names}.get


class FakeRun:
    """Stands in for subprocess.run. It records each command and writes the PDF, as Chrome does."""

    def __init__(self, writes_pdf: bool = True, fails: bool = False):
        self.commands = []
        self.writes_pdf = writes_pdf
        self.fails = fails

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        if self.fails:
            raise subprocess.CalledProcessError(1, command, stderr="chrome crashed")
        if self.writes_pdf:
            pdf_path_of(command).write_bytes(b"%PDF-1.4")


class TestFindChrome(unittest.TestCase):
    def setUp(self):
        self.home = context.temp_repo(self)

    def find(self, env=None, which=never_found):
        return render_pdf.find_chrome(env or {}, which, self.home)

    def test_the_chrome_variable_wins(self):
        env = {"CHROME": "/opt/my-chrome"}
        self.assertEqual(self.find(env, found_only("google-chrome")), "/opt/my-chrome")

    def test_finds_chrome_on_the_path(self):
        self.assertEqual(self.find(which=found_only("google-chrome")), "/usr/bin/google-chrome")

    def test_finds_an_installed_app(self):
        app = self.home / "Chrome"
        app.write_text("binary")
        original = render_pdf.APP_PATHS
        render_pdf.APP_PATHS = (str(app),)
        self.addCleanup(setattr, render_pdf, "APP_PATHS", original)
        self.assertEqual(self.find(), str(app))

    def test_finds_the_newest_chromium_that_playwright_downloaded(self):
        for version in ("chromium-1187", "chromium-1248"):
            binary = self.home / ".cache" / "ms-playwright" / version / "chrome-linux" / "chrome"
            binary.parent.mkdir(parents=True)
            binary.write_text("binary")
        self.assertTrue(self.find().endswith("chromium-1248/chrome-linux/chrome"))

    def test_says_so_when_there_is_no_chrome(self):
        original = render_pdf.APP_PATHS
        render_pdf.APP_PATHS = ()
        self.addCleanup(setattr, render_pdf, "APP_PATHS", original)
        with self.assertRaises(render_pdf.ChromeNotFound) as caught:
            self.find()
        self.assertEqual(caught.exception.event, "render_pdf.chrome_not_found")
        self.assertIn("CHROME", str(caught.exception))


class TestCommand(unittest.TestCase):
    def test_prints_the_page_to_the_pdf_with_no_header_or_footer(self):
        job = render_pdf.PrintJob("chrome", ("--no-sandbox",), pathlib.Path("/s/resume.html"), pathlib.Path("/s/r.pdf"))
        command = render_pdf.command(job)
        self.assertEqual(command[0], "chrome")
        self.assertIn("--headless", command)
        self.assertIn("--no-pdf-header-footer", command)
        self.assertIn("--no-sandbox", command)
        self.assertIn("--print-to-pdf=/s/r.pdf", command)
        self.assertEqual(command[-1], "file:///s/resume.html")

    def test_reads_extra_flags_from_the_environment(self):
        env = {"CHROME_ARGS": "--no-sandbox --disable-gpu"}
        self.assertEqual(render_pdf.extra_flags(env), ("--no-sandbox", "--disable-gpu"))
        self.assertEqual(render_pdf.extra_flags({}), ())


class TestRunJob(unittest.TestCase):
    def setUp(self):
        folder = context.temp_repo(self)
        self.job = render_pdf.PrintJob("chrome", (), folder / "page.html", folder / "page.pdf")

    def test_passes_when_chrome_writes_the_pdf(self):
        render_pdf.run_job(self.job, FakeRun())
        self.assertTrue(self.job.pdf.is_file())

    def test_fails_when_chrome_exits_with_an_error(self):
        with self.assertRaises(render_pdf.PrintFailed) as caught:
            render_pdf.run_job(self.job, FakeRun(fails=True))
        self.assertEqual(caught.exception.event, "render_pdf.print_failed")
        self.assertIn("chrome crashed", str(caught.exception))

    def test_fails_when_chrome_writes_no_pdf(self):
        with self.assertRaises(render_pdf.PrintFailed):
            render_pdf.run_job(self.job, FakeRun(writes_pdf=False))


class TestRenderAll(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)

    def test_prints_each_page_that_names_a_pdf_into_site(self):
        run = FakeRun()
        written = render_pdf.render_all(self.repo_root, "chrome", (), run)
        self.assertEqual(written, [self.repo_root / "site" / "resume.pdf"])
        self.assertTrue(written[0].is_file())
        self.assertTrue(run.commands[0][-1].endswith("/site/resume.html"))

    def test_uses_a_fresh_profile_so_a_running_chrome_cannot_take_the_job(self):
        run = FakeRun()
        render_pdf.render_all(self.repo_root, "chrome", (), run)
        self.assertTrue(any(part.startswith("--user-data-dir=") for part in run.commands[0]))


if __name__ == "__main__":
    unittest.main()
