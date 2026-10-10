import unittest

import context  # noqa: F401
from lib_schema import SchemaError, validate

PERSON = {
    "$defs": {
        "name": {"type": "string", "pattern": "^[A-Z]"},
    },
    "type": "object",
    "required": ["name"],
    "additionalProperties": False,
    "properties": {
        "name": {"$ref": "#/$defs/name"},
        "level": {"enum": ["native", "fluent"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "resume": {"anyOf": [{"type": "boolean"}, {"type": "string"}]},
    },
}


class TestValidate(unittest.TestCase):
    def assert_rejected(self, instance, path):
        with self.assertRaises(SchemaError) as caught:
            validate(instance, PERSON)
        self.assertEqual(caught.exception.path, path)

    def test_accepts_a_valid_instance(self):
        validate({"name": "Ada", "level": "fluent", "tags": ["a"], "resume": True}, PERSON)

    def test_rejects_a_wrong_type(self):
        self.assert_rejected({"name": "Ada", "tags": "a"}, "$.tags")

    def test_rejects_a_missing_required_key(self):
        self.assert_rejected({}, "$.name")

    def test_rejects_an_unknown_key(self):
        self.assert_rejected({"name": "Ada", "extra": 1}, "$.extra")

    def test_follows_a_ref(self):
        self.assert_rejected({"name": "ada"}, "$.name")

    def test_rejects_a_value_outside_the_enum(self):
        self.assert_rejected({"name": "Ada", "level": "basic"}, "$.level")

    def test_checks_each_array_item(self):
        self.assert_rejected({"name": "Ada", "tags": ["a", 2]}, "$.tags[1]")

    def test_any_of_needs_one_match(self):
        self.assert_rejected({"name": "Ada", "resume": 3}, "$.resume")

    def test_boolean_is_not_an_integer_or_a_string(self):
        self.assert_rejected({"name": True}, "$.name")

    def test_rejects_an_unsupported_keyword(self):
        with self.assertRaises(SchemaError):
            validate(1, {"minimum": 0})


if __name__ == "__main__":
    unittest.main()
