#!/usr/bin/env python3
import json
import sys
from pathlib import Path

TEXT_LANGS = {"zh-Hant", "zh-Hans", "en", "ja", "ko", "th"}
TEXT_RENDER_MODES = {"p5-text", "text-outline", "mixed"}


def main(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ids = set()
    errors = []

    canvas = data.get("canvas", {})
    if canvas.get("width", 0) <= 0 or canvas.get("height", 0) <= 0:
        errors.append("canvas width/height must be positive")

    if "seed" not in data:
        errors.append("fixed seed is required")

    renderer = data.get("renderer")
    build = data.get("build", "p5")
    if renderer not in {"p5", "p5-brush", "hybrid"}:
        errors.append("invalid renderer")
    if build not in {"p5", "standalone"}:
        errors.append("invalid build")

    for layer in data.get("layers", []):
        lid = layer.get("id")
        if not lid:
            errors.append("layer missing id")
        elif lid in ids:
            errors.append(f"duplicate id: {lid}")
        else:
            ids.add(lid)

        for el in layer.get("elements", []):
            eid = el.get("id")
            if not eid:
                errors.append("element missing id")
            elif eid in ids:
                errors.append(f"duplicate id: {eid}")
            else:
                ids.add(eid)

            bbox = el.get("bbox")
            if bbox is not None:
                if len(bbox) != 4:
                    errors.append(f"{eid}: bbox must have 4 values")
                else:
                    x, y, w, h = bbox
                    if w <= 0 or h <= 0:
                        errors.append(f"{eid}: bbox w/h must be positive")
                    if not el.get("allowCrop", False) and (x < 0 or y < 0 or x + w > 1 or y + h > 1):
                        errors.append(f"{eid}: bbox outside normalized canvas")

            if el.get("type") == "text" or el.get("drawStrategy") == "text":
                t = el.get("text") or {}
                content = t.get("content")
                language = t.get("language")
                render_mode = t.get("renderMode", "p5-text")
                font = t.get("font") or {}

                if not isinstance(content, str) or content == "":
                    errors.append(f"{eid}: text.content is required for text elements")
                if language not in TEXT_LANGS:
                    errors.append(f"{eid}: unsupported or missing text.language")
                if render_mode not in TEXT_RENDER_MODES:
                    errors.append(f"{eid}: invalid text.renderMode")
                if font and "size" in font and font["size"] <= 0:
                    errors.append(f"{eid}: text.font.size must be positive")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print("OK: scene plan passed static validation")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_scene.py scene-plan.json")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
