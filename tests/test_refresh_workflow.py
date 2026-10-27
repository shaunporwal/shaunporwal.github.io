"""The monthly download refresh must push to main with the least permission and start the publish workflow itself."""
import re
import unittest

import context

WORKFLOWS = context.REPO_ROOT / ".github" / "workflows"
REFRESH = (WORKFLOWS / "refresh-downloads.yaml").read_text()


class TestRefreshWorkflow(unittest.TestCase):
    def test_runs_monthly_and_by_hand(self):
        self.assertRegex(REFRESH, r'cron: "\d+ \d+ 1 \* \*"')
        self.assertIn("workflow_dispatch:", REFRESH)

    def test_holds_only_the_two_permissions_it_needs(self):
        self.assertEqual(re.findall(r"^\s+(\w+): (?:read|write)$", REFRESH, re.M), ["contents", "actions"])

    def test_starts_the_workflow_that_publishes_the_site(self):
        match = re.search(r"gh workflow run (\S+) --ref main", REFRESH)
        self.assertIsNotNone(match)
        self.assertTrue((WORKFLOWS / match.group(1)).exists())

    def test_runs_the_script_that_commits_the_count(self):
        match = re.search(r"run: \./(scripts/\S+)", REFRESH)
        self.assertTrue((context.REPO_ROOT / match.group(1)).exists())


if __name__ == "__main__":
    unittest.main()
