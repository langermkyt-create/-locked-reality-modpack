#!/usr/bin/env python3
"""Build a CurseForge-importable modpack archive for Locked Reality."""
from __future__ import annotations
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "build"
OUTPUT = BUILD / "locked-reality-0.1.0-curseforge.zip"

# CurseForge project/file IDs verified against the official project file pages.
# Required libraries are pulled by the CurseForge client from each project's
# dependency metadata; YUNG's API is also listed explicitly for deterministic import.
CURSEFORGE_FILES = [
    {"projectID": 635042, "fileID": 8833730, "required": True},  # Ad Astra 1.15.21 Forge
    {"projectID": 238086, "fileID": 8020595, "required": True},  # KubeJS 2001.6.5-build.26 Forge
    {"projectID": 510089, "fileID": 5271360, "required": True},  # YUNG's Better Dungeons 4.0.4 Forge
    {"projectID": 421850, "fileID": 5769971, "required": True},  # YUNG's API 4.0.6 Forge
    {"projectID": 551586, "fileID": 8246047, "required": True},  # Cataclysm 3.31 Forge
]

def main() -> None:
    pack = json.loads((ROOT / "pack/pack.json").read_text(encoding="utf-8"))
    BUILD.mkdir(exist_ok=True)
    manifest = {
        "minecraft": {
            "version": "1.20.1",
            "modLoaders": [{"id": "forge-47.4.28", "primary": True}]
        },
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": pack["name"],
        "version": "0.1.0",
        "author": "Locked Reality Team",
        "files": CURSEFORGE_FILES,
        "overrides": "overrides"
    }
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for folder in ("kubejs", "config", "defaultconfigs", "resourcepacks", "shaderpacks"):
            source = ROOT / folder
            if source.exists():
                for item in source.rglob("*"):
                    if item.is_file():
                        archive.write(item, pathlib.Path("overrides") / item.relative_to(ROOT))
        readme = ROOT / "README.md"
        if readme.exists():
            archive.write(readme, "overrides/README-ЗАПЕРТАЯ-РЕАЛЬНОСТЬ.md")
    with zipfile.ZipFile(OUTPUT) as archive:
        names = set(archive.namelist())
        assert "manifest.json" in names
        assert any(name.startswith("overrides/kubejs/") for name in names), "KubeJS story files missing"
        loaded = json.loads(archive.read("manifest.json"))
        assert loaded["minecraft"]["version"] == "1.20.1"
        assert len(loaded["files"]) == len(CURSEFORGE_FILES)
    print(f"CurseForge archive created: {OUTPUT}")
    print(f"CurseForge projects: {len(CURSEFORGE_FILES)}; overrides: {sum(1 for n in names if n.startswith('overrides/'))}")

if __name__ == "__main__":
    main()
