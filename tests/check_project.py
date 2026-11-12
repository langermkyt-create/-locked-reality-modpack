#!/usr/bin/env python3
"""Lightweight structural validation for the Locked Reality project."""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    manifest_path = ROOT / "pack" / "pack.json"
    if not manifest_path.is_file():
        fail("pack/pack.json is missing")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"pack.json is invalid JSON: {exc}")

    required = {
        "name": str,
        "id": str,
        "minecraft": str,
        "loader": str,
        "java": int,
        "mods": list,
    }
    for key, expected_type in required.items():
        if key not in manifest:
            fail(f"manifest field is missing: {key}")
        if not isinstance(manifest[key], expected_type):
            fail(f"manifest field {key!r} must be {expected_type.__name__}")

    if manifest["minecraft"] != "1.20.1":
        fail("this project currently targets Minecraft 1.20.1")
    if manifest["loader"].lower() != "forge":
        fail("this project currently targets Forge")
    if manifest["java"] != 17:
        fail("Minecraft 1.20.1 Forge environment must use Java 17")

    seen = set()
    for index, mod in enumerate(manifest["mods"]):
        if not isinstance(mod, dict):
            fail(f"mods[{index}] must be an object")
        mod_id = mod.get("id")
        if not isinstance(mod_id, str) or not mod_id.strip():
            fail(f"mods[{index}] must have a non-empty string id")
        if mod_id in seen:
            fail(f"duplicate mod id: {mod_id}")
        seen.add(mod_id)

    print("Project manifest: OK")
    print(f"Target: Minecraft {manifest['minecraft']} / {manifest['loader']} / Java {manifest['java']}")
    print(f"Declared mods: {len(manifest['mods'])}")
    print("Note: this is a metadata check, not a Minecraft launch test.")


if __name__ == "__main__":
    main()
