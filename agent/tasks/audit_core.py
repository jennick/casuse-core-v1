# agent/tasks/audit_core.py
import json
import os
import pathlib
import subprocess
import sys
from typing import List, Dict, Any


def sh(cmd: List[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=False).returncode


def exists(p: str) -> bool:
    return pathlib.Path(p).exists()


def discover_python_targets() -> List[str]:
    """
    Detecteer python targets in een multi-module repo.
    Ondersteunt:
      - core-backend/app
      - core_backend/app
      - app
      - modules/*/backend/app
    """
    candidates = ["core-backend/app", "core_backend/app", "app", "modules"]
    out: List[str] = []
    for c in candidates:
        if c == "modules" and exists("modules"):
            for d in pathlib.Path("modules").glob("*/backend/app"):
                if d.is_dir():
                    out.append(str(d))
        elif exists(c):
            out.append(c)
    # de-dup met behoud van volgorde
    seen = set()
    uniq: List[str] = []
    for t in out:
        if t not in seen:
            uniq.append(t)
            seen.add(t)
    return uniq


def run() -> int:
    # “Advice mode” = niet-blokkerend op lint/type/security
    strict = os.getenv("AGENT_AUDIT_STRICT", "false").lower() in {"1", "true", "yes"}

    summary: Dict[str, Any] = {"steps": {}, "targets": []}
    hard_rc = 0          # telt alleen “harde” fouten (compose, etc.)
    soft_rc_aggregate = 0  # ruff/mypy/bandit rc’s, alleen rapportage

    # 1) Ruff (E/F/I via .ruff.toml)
    ruff_rc = sh(["ruff", "check", "."])
    summary["steps"]["ruff"] = {"rc": ruff_rc}
    if strict:
        hard_rc |= ruff_rc
    else:
        soft_rc_aggregate |= ruff_rc

    # 2) mypy per target (voorkomt duplicate-module collision)
    targets = discover_python_targets()
    summary["targets"] = targets
    mypy_total = 0
    for t in targets:
        mypy_cmd = ["mypy", "--explicit-package-bases", "--namespace-packages", t]
        mypy_total |= sh(mypy_cmd)
    summary["steps"]["mypy"] = {"rc": mypy_total}
    if strict:
        hard_rc |= mypy_total
    else:
        soft_rc_aggregate |= mypy_total

    # 3) Bandit (rapporterend; non-blocking)
    if targets:
        bsrc = sh(["bandit", "-q", "-r", *targets, "--exit-zero"])
        summary["steps"]["bandit"] = {"rc": bsrc, "blocking": False}
    else:
        summary["steps"]["bandit"] = {"skipped": True}

    # 4) Compose-config validatie (dit blijft blokkerend)
    if os.path.exists("docker-compose.yml"):
        dcrc = sh(["docker", "compose", "config"])
        summary["steps"]["compose_config"] = {"rc": dcrc}
        hard_rc |= dcrc
    else:
        summary["steps"]["compose_config"] = {"skipped": True}

    # 5) Eindconclusie
    ok = hard_rc == 0
    print(json.dumps({
        "ok": ok,
        "strict": strict,
        "hard_rc": hard_rc,
        "soft_rc": soft_rc_aggregate,
        **summary
    }, indent=2))

    # In niet-strict mode falen we alleen op “harde” fouten.
    return 0 if ok else hard_rc


if __name__ == "__main__":
    sys.exit(run())
