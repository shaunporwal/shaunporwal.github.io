"""Tests for scripts/gen_llms_full.py."""
import unittest

import context
import gen_llms_full

POST_HTML = """<main id="main" class="page">
  <h1 class="page-title">{title}</h1>
  <p class="page-meta">March 5, 2025 &middot; <span class="cat">Habits</span></p>
<p>The body of {title}.</p>
</main>
"""


class TestGenLlmsFull(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.make_post("published", "Published Post")
        self.make_post("hidden", "Hidden Post", draft=True)
        gen_llms_full.sync(self.repo_root)
        self.text = (self.repo_root / "site" / "llms-full.txt").read_text()

    def make_post(self, slug: str, title: str, draft: bool = False) -> None:
        post_dir = self.repo_root / "site" / "posts" / slug
        post_dir.mkdir(parents=True)
        (post_dir / "index.html").write_text(POST_HTML.format(title=title))
        if draft:
            (post_dir / ".draft").touch()

    def test_starts_with_the_name_the_summary_and_the_index_link(self):
        self.assertTrue(self.text.startswith("# Test Person: full text\n\n> A test summary.\n\n"))
        self.assertIn("Index: https://example.com/llms.txt", self.text)

    def test_each_published_post_has_a_header_and_its_body(self):
        self.assertIn("## Published Post\nURL: https://example.com/posts/published/\n", self.text)
        self.assertIn("Published: March 5, 2025\nCategories: Habits\n\nThe body of Published Post.", self.text)

    def test_drafts_stay_out(self):
        self.assertNotIn("Hidden Post", self.text)

    def test_second_run_changes_nothing(self):
        self.assertFalse(gen_llms_full.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
