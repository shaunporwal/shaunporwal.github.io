"""Code-shape checks that ruff does not have: no nested functions and no
lambdas in scripts/ or tests/. ruff.toml holds the other limits."""
import ast
import pathlib
import unittest

import context

FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
CHECKED_DIRS = ("scripts", "tests")


def _nested_functions(function: ast.AST) -> list[ast.AST]:
    return [node for node in ast.walk(function) if node is not function and isinstance(node, FUNCTIONS)]


def relative_name(path: pathlib.Path) -> str:
    return str(path.relative_to(context.REPO_ROOT))


def shape_problems(source: str, filename: str) -> list[str]:
    tree = ast.parse(source)
    functions = [node for node in ast.walk(tree) if isinstance(node, FUNCTIONS)]
    nested = [inner for function in functions for inner in _nested_functions(function)]
    lambdas = [node for node in ast.walk(tree) if isinstance(node, ast.Lambda)]
    return [f"{filename}:{node.lineno}: nested function {node.name}" for node in nested] + [
        f"{filename}:{node.lineno}: lambda" for node in lambdas
    ]


class TestShapeProblems(unittest.TestCase):
    def test_finds_a_nested_function(self):
        source = "def outer():\n    def inner():\n        pass\n"
        self.assertEqual(shape_problems(source, "x.py"), ["x.py:2: nested function inner"])

    def test_finds_a_lambda(self):
        self.assertEqual(shape_problems("key = sorted([], key=lambda v: v)\n", "x.py"), ["x.py:1: lambda"])

    def test_allows_methods_in_a_class(self):
        self.assertEqual(shape_problems("class A:\n    def method(self):\n        pass\n", "x.py"), [])


class TestRepoCodeShape(unittest.TestCase):
    def test_repo_has_no_nested_functions_or_lambdas(self):
        paths = [path for name in CHECKED_DIRS for path in sorted((context.REPO_ROOT / name).glob("*.py"))]
        problems = [p for path in paths for p in shape_problems(path.read_text(), relative_name(path))]
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
