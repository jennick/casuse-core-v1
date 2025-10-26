import os, yaml, json

POL = "agent/policies/ports.yml"
FILES = ["docker-compose.yml","docker-compose.prod.yml","docker-compose.ci.yml"]

def load_yaml(p):
    import yaml
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_yaml(p, data):
    import yaml
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def ensure_labels(svc, router_name, port):
    labels = svc.setdefault("labels", {})
    labels.setdefault("traefik.enable", "true")
    labels.setdefault(f"traefik.http.routers.{router_name}.entrypoints", "web,websecure")
    labels.setdefault(f"traefik.http.services.{router_name}.loadbalancer.server.port", str(port))

def run():
    with open(POL,"r",encoding="utf-8") as f:
        pol = yaml.safe_load(f)
    changed = []
    for fname in FILES:
        if not os.path.exists(fname): 
            continue
        data = load_yaml(fname)
        services = data.get("services", {})
        touched = False
        for svc_name, rule in pol.get("services", {}).items():
            if svc_name in services:
                svc = services[svc_name]
                # remove forbidden host port mappings (80/443)
                ports = svc.get("ports", [])
                forbid = set(str(x) for x in pol.get("rules",{}).get("forbid_host_ports",[]))
                keep = []
                for p in ports:
                    s = str(p)
                    if any(s.startswith(f"{fp}:") for fp in forbid):
                        touched = True
                        continue
                    keep.append(p)
                if keep != ports:
                    svc["ports"] = keep
                ensure_labels(svc, rule.get("traefik_router", svc_name), rule.get("container_port"))
                touched = True
        if touched:
            save_yaml(fname, data)
            changed.append(fname)
    print(json.dumps({"changed": changed}, indent=2))

if __name__ == "__main__":
    run()
