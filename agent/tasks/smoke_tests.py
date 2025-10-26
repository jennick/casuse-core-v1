import os, sys, json, urllib.request

def _call(url, method="GET"):
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=8) as r:
        return r.status, r.read()

def run():
    base = os.environ.get("SMOKE_BASE", "http://localhost:9000")
    results = {}
    s,_ = _call(f"{base}/healthz")
    results["healthz"] = (s == 200)
    s,_ = _call(f"{base}/token", method="GET")
    results["token_get_405"] = (s == 405)
    s,_ = _call(f"{base}/tiles")
    results["tiles_ok"] = s in (200, 404)
    ok = all(results.values())
    print(json.dumps({"ok": ok, "checks": results}, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(run())
