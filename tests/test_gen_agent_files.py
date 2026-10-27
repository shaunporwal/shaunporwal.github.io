"""Tests for scripts/gen_agent_files.py."""
import json
import unittest

import context
import gen_agent_files


class TestGenAgentFiles(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        self.changed = gen_agent_files.sync(self.repo_root)
        self.site_dir = self.repo_root / "site"

    def test_agents_txt_lists_the_rules_and_the_links(self):
        text = (self.site_dir / "agents.txt").read_text()
        self.assertIn("Name: Test Person\nSite: https://example.com/\n", text)
        self.assertIn("Allow: Read each public page.\nDisallow: Post a form.\n", text)
        self.assertIn("Contact: https://cal.com/testperson\n", text)
        self.assertTrue(text.endswith("LLMs: https://example.com/llms.txt\n"))

    def test_agents_json_matches_the_same_rules(self):
        data = json.loads((self.site_dir / ".well-known" / "agents.json").read_text())
        self.assertEqual(data["mayDo"], ["Read each public page."])
        self.assertEqual(data["mayNotDo"], ["Post a form."])
        self.assertEqual(data["sitemap"], "https://example.com/sitemap.xml")

    def test_no_file_holds_the_email_address(self):
        for name in gen_agent_files.FILES:
            self.assertNotIn("test@example.com", (self.site_dir / name).read_text())

    def test_first_run_writes_both_files_and_the_second_run_none(self):
        self.assertEqual(sorted(self.changed), [".well-known/agents.json", "agents.txt"])
        self.assertEqual(gen_agent_files.sync(self.repo_root), [])


if __name__ == "__main__":
    unittest.main()
