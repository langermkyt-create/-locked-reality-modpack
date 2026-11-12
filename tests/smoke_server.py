#!/usr/bin/env python3
"""Install the pinned Forge server, load resolved mods, and wait for Done."""
import os, pathlib, shutil, subprocess, sys, time, urllib.request, selectors

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
SERVER = BUILD / "server"
FORGE = "1.20.1-47.4.28"
INSTALLER = BUILD / f"forge-{FORGE}-installer.jar"
URL = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{FORGE}/forge-{FORGE}-installer.jar"

def main():
    if not (BUILD / "mods").is_dir():
        raise SystemExit("Run build.py before the server smoke test")
    BUILD.mkdir(exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent":"LockedReality CI"})
    with urllib.request.urlopen(req, timeout=120) as response, INSTALLER.open("wb") as out:
        shutil.copyfileobj(response, out)
    SERVER.mkdir(parents=True, exist_ok=True)
    subprocess.run(["java", "-jar", str(INSTALLER), "--installServer"], cwd=SERVER, check=True, timeout=300)
    mods_dir = SERVER / "mods"
    mods_dir.mkdir(exist_ok=True)
    for jar in (BUILD / "mods").glob("*.jar"):
        shutil.copy2(jar, mods_dir / jar.name)
    source_kubejs = ROOT / "kubejs"
    if source_kubejs.exists():
        shutil.copytree(source_kubejs, SERVER / "kubejs", dirs_exist_ok=True)
    (SERVER / "server.properties").write_text(
        "level-name=world\ndifficulty=normal\ngamemode=survival\nspawn-protection=0\n",
        encoding="utf-8"
    )
    (SERVER / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    run_script = SERVER / "run.sh"
    if not run_script.exists():
        raise SystemExit("Forge installer did not create run.sh")
    proc = subprocess.Popen(["bash", "run.sh", "--nogui"], cwd=SERVER, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines, started = [], False
    deadline = time.time() + 300
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    try:
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            events = selector.select(timeout=1)
            for key, _ in events:
                line = key.fileobj.readline()
                if line:
                    lines.append(line)
                    print(line, end="")
                    if "Done (" in line:
                        started = True
                        break
            if started:
                break
        if not started:
            raise RuntimeError("Forge server did not reach the Done state within 300 seconds")
        output = "".join(lines)
        if "00_intro.js" not in output or "Loaded script server_scripts:00_intro.js" not in output:
            raise RuntimeError("The custom KubeJS story script was not loaded by the server")
        if "00_intro.js" in output and "0 errors" not in output:
            raise RuntimeError("KubeJS reported an error while loading the story script")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        (BUILD / "server-smoke.log").write_text("".join(lines), encoding="utf-8")
    print("Forge server smoke test: PASS")

if __name__ == "__main__":
    main()
