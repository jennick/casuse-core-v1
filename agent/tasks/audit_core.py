import subprocess, sys, json, os

def sh(cmd):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=False).returncode

def run():
    rc = 0
    rc |= sh(["ruff", "check", "."])
    rc |= sh(["mypy", "app", "modules"])
    rc |= sh(["bandit", "-q", "-r", "app", "modules"])
    if os.path.exists("docker-compose.yml"):
        rc |= sh(["docker", "compose", "config"])
    print(json.dumps({"ok": rc == 0}, indent=2))
    return rc

if __name__ == "__main__":
    sys.exit(run())
