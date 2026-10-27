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
    "projects": [
        {
            "title": "Widget",
            "links": "[widget.com](https://example.com/widget)",
            "description": "A cool widget that does widget things.",
        }
    ],
    "education": [
        {
            "degree": "B.S., Widgetry",
            "school": "Acme University",
            "meta": "2019 · City, ST",
            "sub": "Cum laude",
        }
    ],
    "skills": {"Programming": "Python, Go"},
}

PDF = {"href": "resume.pdf", "filename": "Test-Person-Resume.pdf"}

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
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        self.assertIn("<!-- RESUME:START -->", block)
        self.assertIn("<!-- RESUME:END -->", block)
        self.assertIn("Test Person", block)
        self.assertIn('<a href="https://example.com" target="_blank" rel="noopener">thing</a>', block)
        self.assertIn("Engineer", block)
        self.assertIn("Acme Co", block)
        self.assertIn("Widget", block)
        self.assertIn("Cum laude", block)
        self.assertIn("<dt>Programming</dt><dd>Python, Go</dd>", block)

    def test_each_short_section_is_wrapped_so_print_can_keep_it_whole(self):
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        for heading in ("Selected Projects", "Education", "Skills &amp; Certifications"):
            self.assertIn(f'<section class="resume-section">\n<h2 class="resume-heading">{heading}</h2>', block)

    def test_experience_section_is_marked_long_so_it_may_span_pages(self):
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        expected = '<section class="resume-section resume-section-long">\n<h2 class="resume-heading">Experience</h2>'
        self.assertIn(expected, block)

    def test_the_header_has_a_download_button_for_the_pdf(self):
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        button = '<a class="btn btn-primary" href="resume.pdf" download="Test-Person-Resume.pdf">Download PDF</a>'
        header = block[block.index("<header"):block.index("</header>")]
        self.assertIn(f'<div class="btn-row resume-actions">\n    {button}\n  </div>', header)

    def test_no_print_note_is_left(self):
        self.assertNotIn("print-note", gen_resume.build_html_block(SAMPLE_DATA, PDF))

    def test_every_section_is_closed(self):
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        self.assertEqual(block.count("<section"), block.count("</section>"))

    def test_bullets_carry_a_literal_marker_character(self):
        # CSS list markers (::marker / list-style) aren't real text, so a
        # browser copy/paste (e.g. into LinkedIn) silently drops them. The
        # bullet must be literal text content instead.
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        self.assertIn('<div class="bullet">- Did a', block)

    def test_bullet_break_spacer_between_bullets_not_around(self):
        # CSS margin isn't real text and never survives copy/paste, so a
        # blank-line gap between bullets needs a literal spacer element in
        # the DOM. Exactly one spacer between each pair of bullets, none
        # before the first or after the last.
        data = dict(SAMPLE_DATA)
        data["experience"] = [
            {
                "title": "Engineer",
                "org": "Acme Co",
                "meta": "2020",
                "bullets": ["First", "Second", "Third"],
            }
        ]
        block = gen_resume.build_html_block(data, PDF)
        self.assertEqual(block.count("bullet-break"), 2)
        first_bullet_pos = block.index('<div class="bullet">- First')
        first_break_pos = block.index("bullet-break")
        self.assertGreater(first_break_pos, first_bullet_pos)

    def test_bullets_are_block_siblings_not_a_list(self):
        # LinkedIn's rich-text composer collapses <li> into single-spaced
        # lines on paste but gives block-level siblings real paragraph
        # spacing, so bullets must be separate <div>s, not <li>s in a <ul>.
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        self.assertNotIn("<li>", block)
        self.assertNotIn("<ul", block)

    def test_education_without_sub_only_emits_school_entry_sub(self):
        data = dict(SAMPLE_DATA)
        data["projects"] = []
        data["education"] = [{"degree": "Cert", "school": "Somewhere U", "meta": "2021"}]
        block = gen_resume.build_html_block(data, PDF)
        self.assertIn("Cert", block)
        self.assertEqual(block.count('<div class="entry-sub">'), 1)
        self.assertIn('<div class="entry-sub">Somewhere U</div>', block)

    def test_education_degree_and_dates_share_entry_head_row(self):
        # Regression: degree/school used to be one combined title string, so
        # a long school name wrapping mid-string could push the dates onto
        # their own separate line. School is now its own entry-sub line.
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        self.assertIn('<div class="entry-title">B.S., Widgetry</div>', block)
        self.assertIn('<div class="entry-sub">Acme University</div>', block)

    def test_project_title_and_links_share_entry_head_row(self):
        # Regression: the link used to sit on its own line below the title;
        # it should share the title's row (same pattern as experience/
        # education), with the description as a separate line below.
        block = gen_resume.build_html_block(SAMPLE_DATA, PDF)
        self.assertIn('<div class="entry-title">Widget</div>', block)
        self.assertIn('<a href="https://example.com/widget" target="_blank" rel="noopener">widget.com</a>', block)
        self.assertIn("A cool widget that does widget things.", block)


class TestPdfLink(unittest.TestCase):
    def test_takes_the_pdf_from_the_page_data_and_names_the_file_after_the_person(self):
        link = gen_resume.pdf_link(context.FAKE_PAGES, context.FAKE_SITE)
        self.assertEqual(link, PDF)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        context.write_record_fixture(self.repo_root, context.SAMPLE_RECORD)

    def test_replaces_marker_block(self):
        (self.repo_root / "site" / "resume.html").write_text(RESUME_TEMPLATE)
        changed = gen_resume.sync(self.repo_root)
        self.assertTrue(changed)
        text = (self.repo_root / "site" / "resume.html").read_text()
        self.assertIn("Test Person", text)
        self.assertIn("Short <strong>detail</strong>", text)
        self.assertIn('href="resume.pdf"', text)
        self.assertNotIn("Hidden Co", text)
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
