import unittest
import xml.etree.ElementTree as ET

import context
import gen_feed

POST_HTML = """<main class="page">
  <h1 class="page-title">{title}</h1>
  <p class="page-meta">{date} &middot; <span class="cat">Habits</span></p>
<p>An intro to {title} &amp; more.</p>
</main>
"""
NS = {"a": "http://www.w3.org/2005/Atom"}


class TestGenFeed(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.make_post("old", "Old Post", "January 2, 2024")
        self.make_post("new", "New Post", "March 5, 2025")
        self.make_post("hidden", "Hidden Post", "May 5, 2025", draft=True)
        self.make_post("undated", "Undated Post", "sometime")
        gen_feed.sync(self.repo_root)
        self.feed = ET.fromstring((self.repo_root / "site" / "feed.xml").read_text())

    def make_post(self, slug: str, title: str, date: str, draft: bool = False) -> None:
        post_dir = self.repo_root / "site" / "posts" / slug
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(POST_HTML.format(title=title, date=date))
        if draft:
            (post_dir / ".draft").touch()

    def titles(self) -> list[str]:
        return [entry.findtext("a:title", namespaces=NS) for entry in self.feed.findall("a:entry", NS)]

    def test_lists_dated_published_posts_newest_first(self):
        self.assertEqual(self.titles(), ["New Post", "Old Post"])

    def test_the_feed_is_dated_by_its_newest_post(self):
        self.assertEqual(self.feed.findtext("a:updated", namespaces=NS), "2025-03-05T00:00:00Z")

    def test_an_entry_has_a_link_a_summary_and_a_category(self):
        entry = self.feed.find("a:entry", NS)
        self.assertEqual(entry.find("a:link", NS).get("href"), "https://example.com/posts/new/")
        self.assertEqual(entry.findtext("a:summary", namespaces=NS), "An intro to New Post & more.")
        self.assertEqual(entry.find("a:category", NS).get("term"), "Habits")

    def test_second_run_changes_nothing(self):
        self.assertFalse(gen_feed.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
