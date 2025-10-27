# agent/tasks/audit_core.py
import json
import os
import pathlib
import subprocess
import sys
from typing import List, Dict, Any


def sh(cmd: List[str]) -> int:
    """Run a command, echo it, return exit code."""
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=False).returncode


def exists(p: str) -> bool:
    return pathlib.Path(p).exists()


def discover_python_targets() -> List[str]:
    """
    Detecteer python targets voor type- en securitychecks.
    - Ondersteunt core-backend/app, core_backend/app, kale app/
    - Zoekt ook modules/*/backend/app
    """
    candidates = [
        "core-backend/app",
        "core_backend/app",
        "app",
        "modules",  # glob hieronder
    ]
    out: List[str] = []

    for c in candidates:
        if c == "modules" and exists("modules"):
            for d in pathlib.Path("modules").glob("*/backend/app"):
                if d.is_dir():
                    out.append(str(d))
        elif exists(c):
            out.append(c)

    # unique, order-preserving
    seen = set()
    uniq: List[str] = []
    for t in out:
        if t not in seen:
            uniq.append(t)
            seen.add(t)
    return uniq


def run() -> int:
    rc = 0
    summary: Dict[str, Any] = {"steps": {}, "targets": []}

    # 1) Ruff lint (E/F/I via .ruff.toml; E401 stubs genegeerd; Bugbear uit)
    ruff_rc = sh(["ruff", "check", "."])
    summary["steps"]["ruff"] = {"rc": ruff_rc}
    rc |= ruff_rc

    # 2) mypy per target (voorkomt duplicate-module botsingen)
    targets = discover_python_targets()
    summary["targets"] = targets

    mypy_total_rc = 0
    for t in targets:
        mypy_cmd = ["mypy", "--explicit-package-bases", "--namespace-packages", t]
        mrc = sh(mypy_cmd)
        mypy_total_rc |= mrc
    summary["steps"]["mypy"] = {"rc": mypy_total_rc}
    rc |= mypy_total_rc

    # 3) Bandit security scan (rapporterend; blokkeert setup niet)
    if targets:
        # Rapporteer resultaten (kwartet-stilte) maar blokkeer niet.
        bandit_cmd = ["bandit", "-q", "-r", *targets, "--exit-zero"]
        bsrc = sh(bandit_cmd)
        summary["steps"]["bandit"] = {"rc": bsrc, "blocking": False}
        # rc |= bsrc  # NIET optellen: we blokkeren niet op bandit in setup
    else:
        summary["steps"]["bandit"] = {"skipped": True}

    # 4) Compose parse (alleen als docker-compose.yml bestaat)
    if os.path.exists("docker-compose.yml"):
        dcrc = sh(["docker", "compose", "config"])
        summary["steps"]["compose_config"] = {"rc": dcrc}
        rc |= dcrc
    else:
        summary["steps"]["compose_config"] = {"skipped": True}

    ok = rc == 0
    print(json.dumps({"ok": ok, **summary}, indent=2))
    return 0 if ok else rc


if __name__ == "__main__":
    sys.exit(run())
