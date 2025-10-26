import subprocess, sys, json, os, pathlib

def sh(cmd):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=False).returncode

def run():
    rc = 0

    # 1) Ruff op de hele repo (mag altijd)
    rc |= sh(["ruff", "check", "."])

    # 2) Python targets detecteren (alleen bestaande paden)
    candidates = ["app", "core-backend/app", "core_backend/app", "modules"]
    py_targets = [p for p in candidates if pathlib.Path(p).exists()]

    # 3) mypy/bandit alleen draaien als er targets zijn
    if py_targets:
        rc |= sh(["mypy", *py_targets])
        rc |= sh(["bandit", "-q", "-r", *py_targets])
    else:
        print("No python targets found for mypy/bandit — skipping.")

    # 4) Compose-parse alleen als bestand bestaat
    if os.path.exists("docker-compose.yml"):
        rc |= sh(["docker", "compose", "config"])

    print(json.dumps({"ok": rc == 0, "mypy_targets": py_targets}, indent=2))
    return rc

if __name__ == "__main__":
    sys.exit(run())
