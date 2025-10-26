import argparse
from tasks import smoke_tests, audit_core, fix_ports

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", choices=["smoke","audit","fix-ports"])
    args = ap.parse_args()
    if args.task == "smoke":
        return smoke_tests.run()
    if args.task == "audit":
        return audit_core.run()
    if args.task == "fix-ports":
        return fix_ports.check()

if __name__ == "__main__":
    raise SystemExit(main())
