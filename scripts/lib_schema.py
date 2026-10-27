"""Validates JSON data against a JSON Schema, with the standard library only.

Supports the subset of JSON Schema that the files in data/ use:
type (object, array, string, boolean, number), properties, required,
additionalProperties (false), items, enum, pattern, anyOf, and local $ref
("#/$defs/<name>"). An unsupported keyword
raises SchemaError, so the schema can never ask for a check that silently
does not run.
"""
import re

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "number": (int, float),
}

ANNOTATIONS = {"$schema", "$id", "$defs", "title", "description"}


class SchemaError(ValueError):
    def __init__(self, path: str, message: str):
        super().__init__(f"{path}: {message}")
        self.path = path


def validate(instance, schema: dict) -> None:
    """Raises SchemaError at the first part of instance that schema rejects."""
    _check(instance, schema, schema, "$")


def _check(instance, schema: dict, root: dict, path: str) -> None:
    for keyword, value in schema.items():
        if keyword in ANNOTATIONS or keyword in OWNED_BY_PROPERTIES:
            continue
        if keyword not in KEYWORDS:
            raise SchemaError(path, f"unsupported schema keyword {keyword!r}")
        KEYWORDS[keyword](instance, value, schema, root, path)


def _check_type(instance, name, schema, root, path) -> None:
    if not isinstance(instance, TYPES[name]) or (name != "boolean" and isinstance(instance, bool)):
        raise SchemaError(path, f"expected {name}")


def _check_properties(instance, properties, schema, root, path) -> None:
    for key, value in instance.items():
        if key in properties:
            _check(value, properties[key], root, f"{path}.{key}")
        elif schema.get("additionalProperties", True) is False:
            raise SchemaError(f"{path}.{key}", "unknown key")


def _check_required(instance, required, schema, root, path) -> None:
    for key in required:
        if key not in instance:
            raise SchemaError(f"{path}.{key}", "missing required key")


def _check_items(instance, item_schema, schema, root, path) -> None:
    for index, item in enumerate(instance):
        _check(item, item_schema, root, f"{path}[{index}]")


def _check_enum(instance, allowed, schema, root, path) -> None:
    # Compares types too, because Python treats 1 == True.
    if not any(type(instance) is type(option) and instance == option for option in allowed):
        raise SchemaError(path, f"expected one of {allowed}")


def _check_pattern(instance, pattern, schema, root, path) -> None:
    if not re.search(pattern, instance):
        raise SchemaError(path, f"does not match {pattern!r}")


def _check_any_of(instance, options, schema, root, path) -> None:
    for option in options:
        if _matches(instance, option, root, path):
            return
    raise SchemaError(path, "matches no anyOf option")


def _matches(instance, schema: dict, root: dict, path: str) -> bool:
    try:
        _check(instance, schema, root, path)
    except SchemaError:
        return False
    return True


def _check_ref(instance, ref, schema, root, path) -> None:
    name = ref.removeprefix("#/$defs/")
    _check(instance, root["$defs"][name], root, path)


KEYWORDS = {
    "type": _check_type,
    "properties": _check_properties,
    "required": _check_required,
    "items": _check_items,
    "enum": _check_enum,
    "pattern": _check_pattern,
    "anyOf": _check_any_of,
    "$ref": _check_ref,
}

# Read by _check_properties, so the main loop skips them.
OWNED_BY_PROPERTIES = {"additionalProperties"}
