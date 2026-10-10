import unittest

import context
import gen_script_index

AGENTS_TEMPLATE = "# scripts\n\nIntro.\n\n<!-- SCRIPTS:START -->\nold\n<!-- SCRIPTS:END -->\n"


class TestSummaries(unittest.TestCase):
    def test_python_summary_is_the_first_sentence_of_the_docstring(self):
        source = '"""Builds the\nthing. More detail here.\n\nSecond paragraph."""\n'
        self.assertEqual(gen_script_index.python_summary(source), "Builds the thing.")

    def test_shell_summary_is_the_first_sentence_of_the_leading_comment(self):
        source = "#!/usr/bin/env bash\n# Refreshes a count\n# from the web. Extra.\nset -e\n"
        self.assertEqual(gen_script_index.shell_summary(source), "Refreshes a count from the web.")

    def test_markup_is_shown_as_code(self):
        self.assertEqual(
            gen_script_index.as_markdown("Writes the <!-- X:START --> block into <nav>."),
            "Writes the `<!-- X:START -->` block into `<nav>`.",
        )


class TestSync(unittest.TestCase):
    def setUp(self):
        self.repo_root = context.temp_repo(self)
        scripts = self.repo_root / "scripts"
        scripts.mkdir()
        (scripts / "b_tool.py").write_text('"""Does B."""\n')
        (scripts / "a_tool.sh").write_text("#!/usr/bin/env bash\n# Does A.\n")
        (scripts / "AGENTS.md").write_text(AGENTS_TEMPLATE)

    def test_lists_every_script_in_name_order(self):
        gen_script_index.sync(self.repo_root)
        text = (self.repo_root / "scripts" / "AGENTS.md").read_text()
        expected = "<!-- SCRIPTS:START -->\n- `a_tool.sh`: Does A.\n- `b_tool.py`: Does B.\n<!-- SCRIPTS:END -->"
        self.assertIn(expected, text)
        self.assertIn("Intro.", text)

    def test_second_run_changes_nothing(self):
        gen_script_index.sync(self.repo_root)
        self.assertFalse(gen_script_index.sync(self.repo_root))


if __name__ == "__main__":
    unittest.main()
