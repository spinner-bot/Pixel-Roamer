"""Format catalog JSON with readable vector commands and pixel rows."""
import json
from pathlib import Path
import sys


def primitive(value):
    return not isinstance(value, (list, dict))


def compact_item(value):
    return primitive(value) or (isinstance(value, list) and all(primitive(v) for v in value))


def formatted(value, level=0):
    indent = "  " * level
    child = "  " * (level + 1)
    if isinstance(value, list):
        if not value or all(compact_item(v) for v in value):
            return json.dumps(value, ensure_ascii=False, allow_nan=False)
        return "[\n" + ",\n".join(child + formatted(v, level + 1) for v in value) + "\n" + indent + "]"
    if isinstance(value, dict):
        if not value:
            return "{}"
        return "{\n" + ",\n".join(
            child + json.dumps(k, ensure_ascii=False) + ": " + formatted(v, level + 1)
            for k, v in value.items()) + "\n" + indent + "}"
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]] or sorted(
        (Path(__file__).resolve().parents[1] / "data/catalogs").glob("*.json"))
    for path in paths:
        path.write_text(formatted(json.loads(path.read_text())) + "\n")
