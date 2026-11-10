"""Load validated game definitions from versioned JSON catalogs."""
from dataclasses import fields
import json
import math
from pathlib import Path

from block_type import BlockType
from buff_system import BuffType

CATALOG_DIR = Path(__file__).resolve().parent / "data/catalogs"


def _finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("catalog numbers must be finite")
    if isinstance(value, dict):
        for item in value.values():
            _finite_tree(item)
    if isinstance(value, list):
        for item in value:
            _finite_tree(item)


def _read(kind, path=None):
    path = Path(path) if path is not None else CATALOG_DIR / f"{kind}.json"
    with path.open(encoding="utf-8") as source:
        document = json.load(source)
    if (not isinstance(document, dict) or type(document.get("schema_version")) is not int
            or document["schema_version"] != 1 or document.get("kind") != kind):
        raise ValueError(f"{path}: expected version 1 {kind} catalog")
    entries = document.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path}: entries must be a nonempty array")
    _finite_tree(entries)
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or type(entry.get("id")) is not int or entry["id"] < 0:
            raise ValueError(f"{path}: every entry needs a nonnegative integer id")
        if entry["id"] in seen:
            raise ValueError(f"{path}: duplicate id {entry['id']}")
        if not isinstance(entry.get("name"), str) or not entry["name"]:
            raise ValueError(f"{path}: id {entry['id']} needs a name")
        seen.add(entry["id"])
    return document


def _tuples(value):
    if isinstance(value, list):
        return tuple(_tuples(item) for item in value)
    if isinstance(value, dict):
        return {key: _tuples(item) for key, item in value.items()}
    return value


def _color(value):
    if (not isinstance(value, (list, tuple)) or len(value) not in (3, 4)
            or any(type(c) is not int or not 0 <= c <= 255 for c in value)):
        raise ValueError("colors must contain RGB/RGBA bytes")


def _pattern(value):
    if value is None:
        return
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("pattern must contain format, dimensions, and data")
    kind, size, data = value
    if kind == "bitmap":
        if type(size) is not int or not 1 <= size <= 256:
            raise ValueError("bitmap dimensions must be in 1..256")
        if not isinstance(data, list) or len(data) != size or any(len(row) != size for row in data):
            raise ValueError("bitmap rows must match its dimensions")
        for row in data:
            for color in row:
                _color(color)
    elif kind == "vector":
        if (not isinstance(size, list) or len(size) != 2
                or any(type(v) not in (int, float) or not 0 < v <= 256 for v in size)):
            raise ValueError("vector dimensions must be in 0..256")
        if not isinstance(data, list):
            raise ValueError("vector commands must be an array")
        arity = {"fill": 2, "rect": 6, "circle": 5}
        for command in data:
            if (not isinstance(command, list) or not command
                    or command[0] not in arity or len(command) != arity[command[0]]):
                raise ValueError("invalid vector command")
            _color(command[-1])
            if any(type(v) not in (int, float) or abs(v) > 4096 for v in command[1:-1]):
                raise ValueError("vector coordinates must be numeric")
    elif kind != "texture":
        raise ValueError(f"unknown pattern format {kind}")


def _definitions(kind, cls, path=None):
    document = _read(kind, path)
    allowed = {field.name for field in fields(cls)}
    result = {}
    for entry in document["entries"]:
        if set(entry) - allowed:
            raise ValueError(f"{kind} {entry['id']}: unknown fields {set(entry) - allowed}")
        _pattern(entry.get("pattern" if kind == "blocks" else "icon"))
        result[entry["id"]] = cls(**{key: _tuples(value) for key, value in entry.items()})
    return result


def load_blocks(path=None):
    result = _definitions("blocks", BlockType, path)
    for block in result.values():
        _color(block.color)
        if any(type(getattr(block, field)) is not bool for field in ("is_solid", "one_way", "climbable")):
            raise ValueError(f"block {block.id}: collision flags must be boolean")
        if any(type(getattr(block, field)) not in (int, float) or getattr(block, field) < 0
               for field in ("surface_f", "space_f", "k_stamina", "swim_f", "damage_ps")):
            raise ValueError(f"block {block.id}: drag and stamina factors must be nonnegative")
        if block.consumed_type_id is not None and block.consumed_type_id not in result:
            raise ValueError(f"block {block.id}: consumed variant does not exist")
    return result


def load_buffs(path=None):
    result = _definitions("buffs", BuffType, path)
    for buff in result.values():
        if buff.category not in ("positive", "neutral", "negative") or type(buff.max_stacks) is not int or buff.max_stacks < 1:
            raise ValueError(f"buff {buff.id}: invalid category or stack limit")
        if any(other not in result for other in (*buff.conflicts, *buff.cleanup_by)):
            raise ValueError(f"buff {buff.id}: unknown conflict or cleanup id")
    return result


def load_costumes(path=None):
    document = _read("costumes", path)
    result = {}
    for entry in document["entries"]:
        width, height = entry.get("w"), entry.get("h")
        if type(width) is not int or type(height) is not int or not 1 <= width <= 128 or not 1 <= height <= 128:
            raise ValueError("costume dimensions must be in 1..128")
        frames = entry.get("frames")
        if not isinstance(frames, dict) or not frames.get("idle"):
            raise ValueError("costume needs an idle frame")
        for sequence in frames.values():
            if not isinstance(sequence, list) or not sequence:
                raise ValueError("animation needs a nonempty frame list")
            for frame in sequence:
                if len(frame) != height or any(len(row) != width for row in frame):
                    raise ValueError("costume frame dimensions do not match")
                for row in frame:
                    for pixel in row:
                        if pixel != 0:
                            _color(pixel)
        result[entry["id"]] = entry
        entry["pixels"] = frames["idle"][0]
    default_id = document.get("default_id")
    if default_id not in result:
        raise ValueError("default costume id does not exist")
    return result, default_id


def load_interface(path=None):
    path = Path(path) if path is not None else CATALOG_DIR / "interface.json"
    with path.open(encoding="utf-8") as source:
        document = json.load(source)
    if document.get("schema_version") != 1 or document.get("kind") != "interface":
        raise ValueError("expected version 1 interface catalog")
    options = document.get("fps_options")
    if (not isinstance(options, list) or not options or len(options) != len(set(options))
            or any(type(value) is not int or not 15 <= value <= 240 for value in options)
            or options != sorted(options)):
        raise ValueError("fps options must be increasing unique integers in 15..240")
    rows, seen = [], set()
    for field in document.get("editor_fields", []):
        if (not isinstance(field, dict) or set(field) != {"path", "label", "type", "default", "step"}
                or field["type"] not in ("float", "int", "str", "bool")
                or not isinstance(field["path"], str) or field["path"] in seen
                or not isinstance(field["label"], str)):
            raise ValueError("invalid editor field definition")
        section, _, key = field["path"].partition(".")
        if section not in ("world", "player") or not key:
            raise ValueError("editor paths must target world/player fields")
        seen.add(field["path"])
        rows.append(tuple(field[key] for key in ("path", "label", "type", "default", "step")))
    if not rows:
        raise ValueError("editor needs field definitions")
    from map_config import validate_config
    defaults = {"world": {}, "player": {}}
    for field in document["editor_fields"]:
        section, key = field["path"].split(".", 1)
        defaults[section][key] = field["default"]
    validate_config(defaults)
    return options, rows
