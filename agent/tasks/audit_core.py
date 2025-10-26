# agent/tasks/audit_core.py
import json
import os
import pathlib
import subprocess
import sys
from typing import List


def sh(cmd: List[str]) -> int:
    """Run a command, echo it, return its exit code."""
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=False).returncode


def _existing(p: str) -> bool:
    return pathlib.Path(p).exists()


def _discover_python_targets() -> List[str]:
    """
    Detecteer gangbare paden in deze repo.
    - Ondersteunt core-backend/app, core_backend/app, kale app, en modules/*/backend/app.
    - Retourneert een lijst paden die bestaan.
    """
    base_candidates = [
        "core-backend/app",
        "core_backend/app",
        "app",
        "modules",  # behandelen we speciaal (globbing)
    ]
    targets: List[str] = []

    for c in base_candidates:
        if c == "modules" and _existing("modules"):
            # Zoek alle */backend/app directories
            for d in pathlib.Path("modules").glob("*/backend/app"):
                if d.is_dir():
                    targets.append(str(d))
        elif _existing(c):
            targets.append(c)

    # De-duplicate while preserving order
    seen = set()
    uniq: List[str] = []
    for t in targets:
        if t not in seen:
            uniq.append(t)
            seen.add(t)
    return uniq


def run() -> int:
    rc = 0

    # 1) Ruff lint
    # Met .ruff.toml wordt E/F/I gecheckt; E401 in stubs wordt genegeerd, B904 staat uit.
    rc |= sh(["ruff", "check", "."])

    # 2) Python targets detecteren
    py_targets = _discover_python_targets()

    # 3) mypy & bandit
    #    - Run mypy PER target om duplicate-module collisions te voorkomen.
    #    - Gebruik flags die passen bij multi-package repos.
    if py_targets:
        for t in py_targets:
            mypy_cmd = [
                "mypy",
                "--explicit-package-bases",
                "--namespace-packages",
                t,
            ]
            rc |= sh(mypy_cmd)

        # Bandit mag in 1 run over alle targets
        rc |= sh(["bandit", "-q", "-r", *py_targets])
    else:
        print("No python targets found for mypy/bandit — skipping.")

    # 4) Compose-parse (alleen als bestand bestaat)
    if os.path.exists("docker-compose.yml"):
        rc |= sh(["docker", "compose", "config"])

    # 5) Resultaat
    print(json.dumps({"ok": rc == 0, "mypy_targets": py_targets}, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(run())
