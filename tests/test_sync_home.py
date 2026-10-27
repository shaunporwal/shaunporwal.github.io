"""Tests for scripts/sync_home.py."""
import struct
import unittest

import context
import sync_home
from lib_images import PNG_SIGNATURE

PNG_8X8 = PNG_SIGNATURE + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 8, 8) + b"\x08\x06\x00\x00\x00"
INDEX = "<main>\n<!-- HERO:START -->\nold\n<!-- HERO:END -->\n<!-- WORK:START -->\nold\n<!-- WORK:END -->\n</main>\n"


class TestRender(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.site_dir = self.repo_root / "site"
        (self.site_dir / "media").mkdir()
        (self.site_dir / "media" / "avatar.jpg").write_bytes(PNG_8X8)

    def test_hero_has_the_role_the_name_the_lead_and_three_links(self):
        hero = sync_home.render_hero(context.FAKE_SITE, context.SAMPLE_RECORD, self.site_dir)
        self.assertIn('<p class="eyebrow rise rise-0">Engineer at Acme Company</p>', hero)
        self.assertIn('<h1 class="display rise rise-1">Test Person</h1>', hero)
        self.assertIn('<p class="lead rise rise-2">A test lead.</p>', hero)
        self.assertIn('href="https://cal.com/testperson" target="_blank" rel="noopener">Book a call</a>', hero)
        self.assertIn('href="resume.html" target="_blank" rel="noopener">Resume</a>', hero)
        self.assertIn('rel="me noopener">GitHub</a>', hero)

    def test_hero_portrait_has_alt_text_and_its_size(self):
        hero = sync_home.render_hero(context.FAKE_SITE, context.SAMPLE_RECORD, self.site_dir)
        self.assertIn('<img src="media/avatar.jpg" alt="Portrait of Test Person" width="8" height="8"', hero)

    def test_work_has_one_card_per_project_that_reveals_on_scroll(self):
        work = sync_home.render_work(context.FAKE_SITE)
        self.assertEqual(work.count('<li class="card lift" data-reveal-item>'), 2)
        self.assertIn('href="https://gadget.example/"', work)
        self.assertIn("Makes gadgets.", work)

    def test_text_is_escaped(self):
        project = {"name": "A & B", "url": "https://x.example/", "summary": "<b>"}
        card = sync_home.render_card(project)
        self.assertIn("A &amp; B", card)
        self.assertIn("&lt;b&gt;", card)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        context.write_record_fixture(self.repo_root, context.SAMPLE_RECORD)
        (self.repo_root / "site" / "media").mkdir()
        (self.repo_root / "site" / "media" / "avatar.jpg").write_bytes(PNG_8X8)
        self.index = self.repo_root / "site" / "index.html"

    def test_replaces_both_blocks(self):
        self.index.write_text(INDEX)
        self.assertTrue(sync_home.sync(self.repo_root))
        text = self.index.read_text()
        self.assertNotIn("old", text)
        self.assertIn('class="hero"', text)
        self.assertIn('class="card-grid"', text)

    def test_second_run_changes_nothing(self):
        self.index.write_text(INDEX)
        sync_home.sync(self.repo_root)
        self.assertFalse(sync_home.sync(self.repo_root))

    def test_a_missing_index_is_not_a_change(self):
        self.assertFalse(sync_home.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
