import unittest

import context
from lib_blocks import replace_block, sync_block, wrap, write_if_changed

PAGE = "<html>\n<!-- X:START -->\nold\n<!-- X:END -->\n</html>\n"


class TestWrap(unittest.TestCase):
    def test_wraps_body_in_named_markers(self):
        self.assertEqual(wrap("X", "body"), "<!-- X:START -->\nbody\n<!-- X:END -->")


class TestWrapCss(unittest.TestCase):
    def test_wraps_body_in_comment_markers(self):
        self.assertEqual(wrap("X", "body", css=True), "/* X:START */\nbody\n/* X:END */")

    def test_replace_block_finds_css_markers(self):
        result = replace_block("a {}\n/* X:START */\nold\n/* X:END */\n", "X", wrap("X", "new", css=True))
        self.assertEqual(result, "a {}\n/* X:START */\nnew\n/* X:END */\n")


class TestReplaceBlock(unittest.TestCase):
    def test_replaces_only_the_named_block(self):
        text = PAGE + "<!-- Y:START -->\nkeep\n<!-- Y:END -->\n"
        result = replace_block(text, "X", wrap("X", "new"))
        self.assertIn("<!-- X:START -->\nnew\n<!-- X:END -->", result)
        self.assertIn("keep", result)

    def test_no_markers_returns_none(self):
        self.assertIsNone(replace_block("<html></html>", "X", wrap("X", "new")))

    def test_backslashes_in_the_block_stay_literal(self):
        body = r"C:\path \1 \g<0>"
        self.assertIn(body, replace_block(PAGE, "X", wrap("X", body)))


class TestWriteIfChanged(unittest.TestCase):
    def setUp(self):
        self.path = context.temp_repo(self) / "file.txt"

    def test_writes_a_new_file(self):
        self.assertTrue(write_if_changed(self.path, "a"))
        self.assertEqual(self.path.read_text(), "a")

    def test_same_text_is_not_a_change(self):
        write_if_changed(self.path, "a")
        self.assertFalse(write_if_changed(self.path, "a"))


class TestSyncBlock(unittest.TestCase):
    def setUp(self):
        self.path = context.temp_repo(self) / "page.html"

    def test_writes_the_new_block(self):
        self.path.write_text(PAGE)
        self.assertTrue(sync_block(self.path, "X", wrap("X", "new")))
        self.assertIn("new", self.path.read_text())

    def test_second_run_is_not_a_change(self):
        self.path.write_text(PAGE)
        sync_block(self.path, "X", wrap("X", "new"))
        self.assertFalse(sync_block(self.path, "X", wrap("X", "new")))

    def test_no_markers_is_not_a_change(self):
        self.path.write_text("<html></html>")
        self.assertFalse(sync_block(self.path, "X", wrap("X", "new")))


if __name__ == "__main__":
    unittest.main()
