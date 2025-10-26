import os, sys, json, yaml

POL = "agent/policies/ports.yml"

def check():
    with open(POL, "r", encoding="utf-8") as f:
        pol = yaml.safe_load(f)
    findings = []
    for fname in ["docker-compose.yml","docker-compose.prod.yml","docker-compose.ci.yml"]:
        if not os.path.exists(fname): 
            continue
        with open(fname, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        services = (data or {}).get("services", {})
        for svc_name, rule in pol.get("services", {}).items():
            if svc_name in services:
                cont = services[svc_name]
                ports = cont.get("ports", [])
                labels = cont.get("labels", {})
                findings.append({"file": fname, "service": svc_name, "ports": ports, "labels": labels})
    print(json.dumps({"findings": findings}, indent=2))

if __name__ == "__main__":
    check()
