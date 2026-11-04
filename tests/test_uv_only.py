"""Python starts only through uv: the Makefile, the pre-commit hook, the tests workflow and each script shebang."""
import re
import unittest

import context

UV_SHEBANG = "#!/usr/bin/env -S uv run --script"
MAKEFILE = (context.REPO_ROOT / "Makefile").read_text()
PRE_COMMIT = (context.REPO_ROOT / ".githooks" / "pre-commit").read_text()
TESTS_WORKFLOW = (context.REPO_ROOT / ".github" / "workflows" / "test.yaml").read_text()
DEFAULT_PYTHON = re.search(r"^PYTHON \?= (.+)$", MAKEFILE, re.MULTILINE)


def shebang_of(path) -> str:
    first = path.read_text().splitlines()[:1]
    return first[0] if first and first[0].startswith("#!") else ""


class TestPythonStartsThroughUv(unittest.TestCase):
    def test_the_makefile_default_runs_python_through_uv(self):
        self.assertIsNotNone(DEFAULT_PYTHON)
        self.assertTrue(DEFAULT_PYTHON.group(1).startswith("uv run "))

    def test_the_pre_commit_hook_does_not_restate_the_default(self):
        self.assertNotIn("PYTHON=", PRE_COMMIT)

    def test_the_tests_workflow_sets_up_uv(self):
        self.assertIn("astral-sh/setup-uv", TESTS_WORKFLOW)

    def test_the_tests_workflow_installs_ruff_through_uv(self):
        self.assertIn("uv tool install", TESTS_WORKFLOW)
        self.assertNotIn("pipx", TESTS_WORKFLOW)

    def test_every_script_shebang_is_the_uv_one(self):
        wrong = [path.name for path in context.SCRIPTS_DIR.glob("*.py") if shebang_of(path) not in ("", UV_SHEBANG)]
        self.assertEqual(wrong, [])


if __name__ == "__main__":
    unittest.main()
