import pathlib
import tempfile
import unittest

import context  # noqa: F401
import gen_resume

SAMPLE_DATA = {
    "name": "Test Person",
    "contact": ["City, ST", "test@example.com"],
    "experience": [
        {
            "title": "Engineer",
            "org": "Acme Co",
            "meta": "Jan 2020 – Present · City, ST",
            "bullets": ["Did a [thing](https://example.com) well"],
        }
    ],
    "projects": [{"title": "Widget", "sub": "A cool [widget](https://example.com/widget)"}],
    "education": [
        {"title": "B.S., Widgetry — Acme University", "meta": "2019 · City, ST", "sub": "Cum laude"}
    ],
    "skills": {"Programming": "Python, Go"},
}

RESUME_TEMPLATE = """<!doctype html>
<html><body>
<!-- RESUME:START -->
OLD CONTENT
<!-- RESUME:END -->
</body></html>
"""

RESUME_WITHOUT_MARKERS = "<html><body>no markers here</body></html>"


class TestBuildHtmlBlock(unittest.TestCase):
    def test_contains_expected_structure(self):
        block = gen_resume.build_html_block(SAMPLE_DATA)
        self.assertIn("<!-- RESUME:START -->", block)
        self.assertIn("<!-- RESUME:END -->", block)
        self.assertIn("Test Person", block)
        self.assertIn('<a href="https://example.com">thing</a>', block)
        self.assertIn("Engineer", block)
        self.assertIn("Acme Co", block)
        self.assertIn("Widget", block)
        self.assertIn("Cum laude", block)
        self.assertIn("<dt>Programming</dt><dd>Python, Go</dd>", block)

    def test_education_without_sub_omits_entry_sub(self):
        data = dict(SAMPLE_DATA)
        data["education"] = [{"title": "Cert — Somewhere", "meta": "2021"}]
        block = gen_resume.build_html_block(data)
        self.assertIn("Cert — Somewhere", block)
        # No entry-sub div should be emitted for this entry.
        self.assertNotIn("<div class=\"entry-sub\">Cum laude</div>", block)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = pathlib.Path(self.tmp.name)
        (self.repo_root / "data").mkdir()
        (self.repo_root / "site").mkdir()
        import json
        (self.repo_root / "data" / "resume.json").write_text(json.dumps(SAMPLE_DATA))

    def test_replaces_marker_block(self):
        (self.repo_root / "site" / "resume.html").write_text(RESUME_TEMPLATE)
        changed = gen_resume.sync(self.repo_root)
        self.assertTrue(changed)
        text = (self.repo_root / "site" / "resume.html").read_text()
        self.assertIn("Test Person", text)
        self.assertNotIn("OLD CONTENT", text)

    def test_no_markers_returns_false(self):
        (self.repo_root / "site" / "resume.html").write_text(RESUME_WITHOUT_MARKERS)
        self.assertFalse(gen_resume.sync(self.repo_root))

    def test_idempotent_second_run(self):
        (self.repo_root / "site" / "resume.html").write_text(RESUME_TEMPLATE)
        gen_resume.sync(self.repo_root)
        self.assertFalse(gen_resume.sync(self.repo_root))


class TestRenderPlaintext(unittest.TestCase):
    def test_links_become_label_and_url(self):
        text = gen_resume.render_plaintext(SAMPLE_DATA)
        self.assertIn("thing (https://example.com)", text)
        self.assertIn("Test Person", text)
        self.assertIn("EXPERIENCE", text)
        self.assertIn("SKILLS & CERTIFICATIONS", text)
        self.assertIn("Programming: Python, Go", text)

    def test_education_sub_included_when_present(self):
        text = gen_resume.render_plaintext(SAMPLE_DATA)
        self.assertIn("Cum laude", text)


if __name__ == "__main__":
    unittest.main()
