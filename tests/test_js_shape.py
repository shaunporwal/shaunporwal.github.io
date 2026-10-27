"""Code-shape checks for the JavaScript in site/js/, which no linter in this repo covers: a one-line
docstring first, no arrow functions, no anonymous or nested functions, and top-level functions of 15 lines or fewer."""
import re
import unittest

import context

JS_DIR = context.REPO_ROOT / "site" / "js"
MAX_LINES = 15
FUNCTION_START_RE = re.compile(r"^(?:async )?function \w+\(", re.MULTILINE)


def shape_problems(source: str, filename: str) -> list[str]:
    lines = source.splitlines()
    problems = []
    if not lines or not re.fullmatch(r"/\*\* .+ \*/", lines[0]):
        problems.append(f"{filename}:1: the first line must be a one-line /** ... */ docstring")
    for number, line in enumerate(lines, start=1):
        problems += line_problems(line, f"{filename}:{number}")
    return problems + long_functions(lines, filename)


def line_problems(line: str, where: str) -> list[str]:
    code = line.split("//")[0]
    checks = (
        ("=>" in code, "arrow function"),
        (bool(re.search(r"\bfunction\s*\(", code)), "anonymous function"),
        (bool(re.match(r"\s+(?:async )?function\b", code)), "nested function"),
    )
    return [f"{where}: {message}" for found, message in checks if found]


def function_spans(lines: list[str]) -> list[tuple[int, int]]:
    """(first line, closing line) of each top-level function. A top-level function closes at a "}" in column 0."""
    starts = [number for number, line in enumerate(lines, start=1) if FUNCTION_START_RE.match(line)]
    ends = [number for number, line in enumerate(lines, start=1) if line == "}"]
    return [(first, min(end for end in ends if end > first)) for first in starts]


def long_functions(lines: list[str], filename: str) -> list[str]:
    return [
        f"{filename}:{first}: function longer than {MAX_LINES} lines"
        for first, last in function_spans(lines)
        if last - first + 1 > MAX_LINES
    ]


class TestShapeProblems(unittest.TestCase):
    def test_finds_an_arrow_function(self):
        self.assertIn("x.js:2: arrow function", shape_problems("/** Doc. */\nconst f = () => 1\n", "x.js"))

    def test_finds_an_anonymous_function(self):
        self.assertIn("x.js:2: anonymous function", shape_problems("/** Doc. */\nrun(function () {})\n", "x.js"))

    def test_finds_a_nested_function(self):
        source = "/** Doc. */\nfunction a() {\n  function b() {}\n}\n"
        self.assertIn("x.js:3: nested function", shape_problems(source, "x.js"))

    def test_finds_a_missing_docstring(self):
        problems = shape_problems("let x\n", "x.js")
        self.assertIn("x.js:1: the first line must be a one-line /** ... */ docstring", problems)

    def test_finds_a_long_function(self):
        body = "\n".join(["  work()"] * 15)
        source = f"/** Doc. */\nfunction long() {{\n{body}\n}}\n"
        self.assertIn("x.js:2: function longer than 15 lines", shape_problems(source, "x.js"))

    def test_accepts_a_short_named_function(self):
        self.assertEqual(shape_problems("/** Doc. */\nfunction ok() {\n  return 1\n}\n", "x.js"), [])


class TestRepoJavaScript(unittest.TestCase):
    def test_every_script_in_site_js_has_the_shape(self):
        paths = sorted(JS_DIR.glob("*.js"))
        names = [str(path.relative_to(context.REPO_ROOT)) for path in paths]
        problems = [p for path, name in zip(paths, names, strict=True) for p in shape_problems(path.read_text(), name)]
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
