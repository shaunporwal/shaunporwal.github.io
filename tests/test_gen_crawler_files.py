import unittest

import context
import gen_crawler_files

POST_HTML = """<main class="page">
  <h1 class="page-title">{title}</h1>
  <p class="page-meta">March 5, 2025</p>
<p>An intro to {title}.</p>
</main>
"""


class TestGenCrawlerFiles(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        context.write_record_fixture(self.repo_root, context.SAMPLE_RECORD)
        self.site_dir = self.repo_root / "site"
        self.make_post("published", "Published Post")
        self.make_post("hidden", "Hidden Post", draft=True)
        self.changed = gen_crawler_files.sync(self.repo_root)

    def make_post(self, slug: str, title: str, draft: bool = False) -> None:
        post_dir = self.site_dir / "posts" / slug
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(POST_HTML.format(title=title))
        if draft:
            (post_dir / ".draft").touch()

    def read(self, name: str) -> str:
        return (self.site_dir / name).read_text()

    def test_cname_is_the_base_url_host(self):
        self.assertEqual(self.read("CNAME"), "example.com\n")

    def test_robots_names_the_sitemap_on_the_base_url(self):
        self.assertIn("User-agent: *\nAllow: /", self.read("robots.txt"))
        self.assertIn("Sitemap: https://example.com/sitemap.xml", self.read("robots.txt"))

    def test_robots_allows_each_named_crawler(self):
        self.assertIn("User-agent: TestBot\nAllow: /", self.read("robots.txt"))

    def test_llms_has_summary_and_current_role(self):
        self.assertIn("# Test Person\n\n> A test summary. Currently Engineer at Acme Company.", self.read("llms.txt"))

    def test_llms_lists_sitemap_pages_with_descriptions(self):
        line = "- [About — Test Person](https://example.com/about.html): About Test Person."
        self.assertIn(line, self.read("llms.txt"))

    def test_llms_lists_published_posts_only(self):
        llms = self.read("llms.txt")
        self.assertIn("- [Published Post](https://example.com/posts/published/): An intro to Published Post.", llms)
        self.assertNotIn("Hidden Post", llms)

    def test_llms_lists_the_work(self):
        self.assertIn("- [Acme Company](https://acme.example/): Makes widgets.", self.read("llms.txt"))

    def test_llms_lists_the_other_profiles_and_no_email_address(self):
        llms = self.read("llms.txt")
        self.assertIn("- [GitHub](https://github.com/testperson)\n- [X](https://x.com/testperson)", llms)
        self.assertIn("- [Book a call](https://cal.com/testperson)", llms)
        self.assertNotIn("test@example.com", llms)

    def test_llms_links_the_full_text_the_feed_and_the_agent_rules(self):
        llms = self.read("llms.txt")
        self.assertIn("- [Full text of every post](https://example.com/llms-full.txt)", llms)
        self.assertIn("- [Atom feed](https://example.com/feed.xml)", llms)
        self.assertIn("- [Rules for agents](https://example.com/agents.txt)", llms)

    def test_first_run_writes_every_file(self):
        self.assertEqual(sorted(self.changed), ["CNAME", "llms.txt", "robots.txt"])

    def test_second_run_changes_nothing(self):
        self.assertEqual(gen_crawler_files.sync(self.repo_root), [])


if __name__ == "__main__":
    unittest.main()
