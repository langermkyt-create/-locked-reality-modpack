#!/usr/bin/env python3
"""Resolve compatible Modrinth mods, verify downloads and build a .mrpack."""
from __future__ import annotations
import hashlib, json, os, pathlib, shutil, sys, time, urllib.parse, urllib.request, zipfile

ROOT = pathlib.Path(__file__).resolve().parent
BUILD = ROOT / "build"
MODS = BUILD / "mods"
API = "https://api.modrinth.com/v2"
GAME = "1.20.1"
LOADERS = ["forge"]
USER_AGENT = "LockedRealityModpack/0.1 (pack-builder)"

def request_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))

def get_version(project: str):
    query = urllib.parse.urlencode({
        "game_versions": json.dumps([GAME]),
        "loaders": json.dumps(LOADERS),
    })
    versions = request_json(f"{API}/project/{project}/version?{query}")
    stable = [v for v in versions if v.get("version_type") == "release"]
    if not stable:
        raise RuntimeError(f"No stable Forge {GAME} release found for {project}")
    return stable[0]

def get_exact_version(version_id: str):
    return request_json(f"{API}/version/{version_id}")

def choose_file(version):
    files = version.get("files", [])
    primary = next((f for f in files if f.get("primary")), None)
    if primary is None:
        primary = next((f for f in files if f.get("filename","").endswith(".jar")), None)
    if primary is None:
        raise RuntimeError(f"No JAR file in Modrinth version {version.get('id')}")
    return primary

def resolve_projects():
    manifest = json.loads((ROOT / "pack/mods.json").read_text(encoding="utf-8"))
    resolved, queue = {}, list(manifest["projects"])
    while queue:
        project = queue.pop(0)
        version = get_version(project)
        canonical_id = version.get("project_id") or project
        if canonical_id in resolved:
            continue
        resolved[canonical_id] = version
        for dep in version.get("dependencies", []):
            if dep.get("dependency_type") != "required":
                continue
            if dep.get("version_id"):
                dep_version = get_exact_version(dep["version_id"])
                project_id = dep_version.get("project_id")
                if project_id and project_id not in resolved:
                    # Exact version is cached directly under its project ID.
                    resolved[project_id] = dep_version
                    for nested in dep_version.get("dependencies", []):
                        if nested.get("dependency_type") == "required" and nested.get("project_id") and nested["project_id"] not in resolved:
                            queue.append(nested["project_id"])
            elif dep.get("project_id") and dep["project_id"] not in resolved:
                queue.append(dep["project_id"])
    return manifest, resolved

def download_file(file_meta):
    filename = file_meta["filename"]
    target = MODS / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(file_meta["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90) as response, target.open("wb") as out:
        shutil.copyfileobj(response, out)
    hashes = file_meta.get("hashes", {})
    for algorithm in ("sha1", "sha512"):
        expected = hashes.get(algorithm)
        if expected:
            digest = hashlib.new(algorithm, target.read_bytes()).hexdigest()
            if digest.lower() != expected.lower():
                target.unlink(missing_ok=True)
                raise RuntimeError(f"{algorithm} mismatch for {filename}")
    return target

def main():
    shutil.rmtree(BUILD, ignore_errors=True)
    MODS.mkdir(parents=True)
    manifest, projects = resolve_projects()
    index_files = []
    report = []
    for project_id, version in sorted(projects.items()):
        file_meta = choose_file(version)
        # Do not package client-only files in the server-tested mod set.
        env = version.get("game_versions", [])
        if GAME not in env:
            raise RuntimeError(f"Incompatible game version for {version.get('name')}")
        path = download_file(file_meta)
        server_side = version.get("server_side", "required")
        client_side = version.get("client_side", "required")
        index_files.append({
            "path": f"mods/{path.name}",
            "hashes": file_meta.get("hashes", {}),
            "env": {
                "client": "required" if client_side == "required" else "optional",
                "server": "required" if server_side == "required" else "optional"
            },
            "downloads": [file_meta["url"]],
            "fileSize": file_meta["size"]
        })
        report.append({
            "project_id": project_id,
            "name": version.get("name"),
            "version": version.get("version_number"),
            "file": path.name
        })
    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": "0.1.0",
        "name": "Запертая реальность",
        "summary": "Сюжетное приключение Minecraft 1.20.1 Forge",
        "files": index_files,
        "dependencies": {"minecraft": GAME, "forge": "47.4.28"}
    }
    pack_path = BUILD / "locked-reality-0.1.0.mrpack"
    with zipfile.ZipFile(pack_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("modrinth.index.json", json.dumps(index, ensure_ascii=False, indent=2))
        for folder in ("kubejs", "config", "defaultconfigs"):
            source = ROOT / folder
            if source.exists():
                for item in source.rglob("*"):
                    if item.is_file():
                        zf.write(item, pathlib.Path("overrides") / item.relative_to(ROOT))
    (BUILD / "resolved-mods.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"pack": str(pack_path), "mods": report}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        raise
