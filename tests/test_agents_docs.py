"""Every top-level directory has an AGENTS.md, and the root AGENTS.md links
to each one, so an agent can find the instructions for the place it works."""
import unittest

import context

SKIPPED_DIRS = {"__pycache__"}


def agent_dirs() -> list[str]:
    return sorted(
        path.name
        for path in context.REPO_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name not in SKIPPED_DIRS
    )


class TestAgentsDocs(unittest.TestCase):
    def test_every_top_level_directory_has_agents_md(self):
        missing = [name for name in agent_dirs() if not (context.REPO_ROOT / name / "AGENTS.md").exists()]
        self.assertEqual(missing, [])

    def test_root_agents_md_links_each_directory_file(self):
        root = (context.REPO_ROOT / "AGENTS.md").read_text()
        unlinked = [name for name in agent_dirs() if f"]({name}/AGENTS.md)" not in root]
        self.assertEqual(unlinked, [])


if __name__ == "__main__":
    unittest.main()
