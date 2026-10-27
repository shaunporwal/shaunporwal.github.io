"""Tests for scripts/sync_home.py."""
import unittest

import context
import sync_home

INDEX = "<main>\n<!-- HERO:START -->\nold\n<!-- HERO:END -->\n<!-- WORK:START -->\nold\n<!-- WORK:END -->\n</main>\n"


class TestRender(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.site_dir = self.repo_root / "site"
        (self.site_dir / "media").mkdir()
        (self.site_dir / "media" / "avatar.jpg").write_bytes(context.PNG_8X8)
        context.write_project_media(self.site_dir)

    def test_hero_has_the_role_the_name_the_lead_and_three_links(self):
        hero = sync_home.render_hero(context.FAKE_SITE, context.SAMPLE_RECORD, self.site_dir)
        self.assertIn('<p class="eyebrow rise rise-0">Engineer at Acme Company</p>', hero)
        self.assertIn('<h1 class="display rise rise-1">Test Person</h1>', hero)
        self.assertIn('<p class="lead rise rise-2">A test lead.</p>', hero)
        self.assertIn('href="https://cal.com/testperson" target="_blank" rel="noopener">Book a call</a>', hero)
        self.assertIn('href="resume.html">Resume</a>', hero)
        self.assertIn('rel="me noopener">GitHub</a>', hero)

    def test_hero_has_a_decorative_dot_field_and_a_lit_layer_that_screen_readers_skip(self):
        hero = sync_home.render_hero(context.FAKE_SITE, context.SAMPLE_RECORD, self.site_dir)
        art = (
            '<div class="hero-art" aria-hidden="true">'
            '<span class="hero-dots"></span><span class="hero-lit"></span></div>'
        )
        self.assertIn(art, hero)

    def test_only_the_book_a_call_button_has_the_edge_light(self):
        hero = sync_home.render_hero(context.FAKE_SITE, context.SAMPLE_RECORD, self.site_dir)
        self.assertEqual(hero.count("btn-sheen"), 1)
        self.assertIn('class="btn btn-primary btn-sheen"', hero)

    def test_hero_portrait_has_alt_text_and_its_size(self):
        hero = sync_home.render_hero(context.FAKE_SITE, context.SAMPLE_RECORD, self.site_dir)
        self.assertIn('<img src="media/avatar.jpg" alt="Portrait of Test Person" width="8" height="8"', hero)

    def test_work_has_one_card_per_project_that_reveals_on_scroll(self):
        work = sync_home.render_work(context.FAKE_SITE, self.site_dir)
        self.assertEqual(work.count('<li class="card lift" data-reveal-item>'), 2)
        self.assertIn('href="https://gadget.example/"', work)
        self.assertIn("Makes gadgets.", work)

    def test_each_card_leads_with_its_picture_then_the_name_then_the_summary(self):
        card = sync_home.render_card(context.FAKE_SITE["projects"][0], self.site_dir)
        parts = ('class="card-media', 'class="card-title"', 'class="card-text"')
        positions = [card.index(part) for part in parts]
        self.assertEqual(positions, sorted(positions))

    def test_the_name_keeps_its_arrow_and_the_whole_card_is_one_link(self):
        card = sync_home.render_card(context.FAKE_SITE["projects"][0], self.site_dir)
        self.assertIn(f"Acme Company{sync_home.ARROW}</h3>", card)
        self.assertEqual(card.count("<a "), 1)
        self.assertEqual(card.count("</a>"), 1)

    def test_the_title_and_the_summary_sit_in_one_body_under_the_picture(self):
        card = sync_home.render_card(context.FAKE_SITE["projects"][0], self.site_dir)
        self.assertRegex(card, r'</div>\s*<div class="card-body">\s*<h3 class="card-title">')

    def test_each_kind_of_picture_reaches_its_card(self):
        work = sync_home.render_work(context.FAKE_SITE, self.site_dir)
        self.assertIn('class="card-media card-media-logo"', work)
        self.assertIn('class="card-media card-media-clip"', work)

    def test_the_cards_hold_no_email_address(self):
        work = sync_home.render_work(context.FAKE_SITE, self.site_dir)
        self.assertNotIn(context.FAKE_SITE["email"], work)
        self.assertNotIn("@", work)

    def test_text_is_escaped(self):
        project = {**context.FAKE_SITE["projects"][0], "name": "A & B", "summary": "<b>"}
        card = sync_home.render_card(project, self.site_dir)
        self.assertIn("A &amp; B", card)
        self.assertIn("&lt;b&gt;", card)


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        context.write_record_fixture(self.repo_root, context.SAMPLE_RECORD)
        (self.repo_root / "site" / "media").mkdir()
        (self.repo_root / "site" / "media" / "avatar.jpg").write_bytes(context.PNG_8X8)
        context.write_project_media(self.repo_root / "site")
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
