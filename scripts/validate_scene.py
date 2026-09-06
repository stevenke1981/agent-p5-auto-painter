#!/usr/bin/env python3
"""Read-only Draft 2020-12 and semantic validation for agent scene documents."""
from __future__ import annotations

import argparse
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 10 * 1024 * 1024
EPSILON = 1e-9


def pointer(parts: Any) -> str:
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: str) -> Any:
    if path == "-":
        text = sys.stdin.read(MAX_BYTES + 1)
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise ValueError("input exceeds 10 MiB")
    else:
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("input exceeds 10 MiB")
        text = raw.decode("utf-8-sig")
    return json.loads(text.lstrip("\ufeff"), parse_constant=reject_constant,
                      object_pairs_hook=unique_object)


def nonfinite_paths(value: Any, path: tuple = ()) -> list[str]:
    if isinstance(value, float) and not math.isfinite(value):
        return [f"{pointer(path)}: number must be finite"]
    if isinstance(value, dict):
        return [e for k, v in value.items() for e in nonfinite_paths(v, (*path, k))]
    if isinstance(value, list):
        return [e for k, v in enumerate(value) for e in nonfinite_paths(v, (*path, k))]
    return []


@lru_cache(maxsize=2)
def schema_validator(kind: str):
    from jsonschema import Draft202012Validator
    if kind not in {"plan", "analysis"}:
        raise ValueError("kind must be plan or analysis")
    schema = json.loads((ROOT / "schemas" / f"scene-{kind}.schema.json").read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_document(data: Any, kind: str = "plan") -> list[str]:
    """Return deterministic diagnostics; never mutate input or run scene code."""
    validator = schema_validator(kind)
    errors = nonfinite_paths(data)
    if errors:
        return errors
    errors = [f"{pointer(e.absolute_path)}: {e.message}" for e in validator.iter_errors(data)]
    if errors:  # Do not assume types are usable until the schema has passed.
        return sorted(errors)
    ids: dict[str, str] = {}

    def check_item(item: dict[str, Any], path: tuple, bbox: bool = True) -> None:
        name = item["id"]
        location = pointer((*path, "id"))
        if name in ids:
            errors.append(f"{location}: duplicate id {name!r}; first at {ids[name]}")
        else:
            ids[name] = location
        if bbox and "bbox" in item and not item.get("allowCrop", False):
            x, y, w, h = item["bbox"]
            if x < -EPSILON or y < -EPSILON or x + w > 1 + EPSILON or y + h > 1 + EPSILON:
                errors.append(f"{pointer((*path, 'bbox'))}: outside normalized canvas; use allowCrop explicitly")

    if kind == "plan":
        if data.get("build", "p5") == "standalone" and data["renderer"] != "p5-brush":
            errors.append("/build: standalone requires renderer p5-brush")
        for i, layer in enumerate(data["layers"]):
            check_item(layer, ("layers", i), bbox=False)
            for j, element in enumerate(layer["elements"]):
                check_item(element, ("layers", i, "elements", j))
    else:
        source = data["source"]
        if not math.isclose(source["aspectRatio"], source["width"] / source["height"], rel_tol=1e-3):
            errors.append("/source/aspectRatio: inconsistent with width / height (tolerance 0.1%)")
        for i, element in enumerate(data["elements"]):
            check_item(element, ("elements", i))
    return sorted(errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="UTF-8 JSON file, or - for stdin")
    parser.add_argument("--kind", choices=("plan", "analysis"), default="plan")
    parser.add_argument("--json", action="store_true", dest="as_json", help="machine-readable diagnostics")
    args = parser.parse_args(argv)
    code = 0
    try:
        data = read_json(args.path)
        errors = validate_document(data, args.kind)
        code = 1 if errors else 0
    except ImportError:
        errors = ["missing jsonschema; run: python -m pip install -r requirements.txt"]
        code = 2
    except (OSError, ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        errors = [str(exc)]
        code = 2
    result = {"valid": code == 0, "kind": args.kind, "path": args.path, "errors": errors}
    if args.as_json:
        # ASCII escaping is deliberate: JSON round-trips Unicode even in legacy Windows consoles.
        print(json.dumps(result, ensure_ascii=True))
    elif errors:
        for error in errors:
            message = f"ERROR: {error}"
            encoding = sys.stderr.encoding or "utf-8"
            print(message.encode(encoding, errors="backslashreplace").decode(encoding), file=sys.stderr)
    else:
        print(f"OK: scene {args.kind} passed schema and semantic validation")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
