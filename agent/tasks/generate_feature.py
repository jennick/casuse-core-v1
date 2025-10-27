import os, re, json, pathlib, datetime
from ruamel.yaml import YAML
from jinja2 import Environment, FileSystemLoader, StrictUndefined

yaml = YAML()
ROOT = pathlib.Path('.').resolve()
OUT  = ROOT / '.agent_out'
TEMPL = ROOT / 'agent' / 'templates'

def parse_comment_to_spec(body: str) -> dict:
    m = re.search(r"""```yaml(.*?)```""", body, re.S)
    if m:
        return yaml.load(m.group(1))
    # minimal default
    return {
        "feature": {
            "name": "feature",
            "api_prefix": "/api/feature",
            "model": {"table": "feature", "fields": [
                {"name":"id","type":"uuid","primary":True},
                {"name":"name","type":"str","required":True},
                {"name":"email","type":"email","unique":True,"required":True},
                {"name":"status","type":"str","default":"active"}
            ]},
            "security": {"read_scopes":["read"],"write_scopes":["write"]},
            "endpoints":[{"method":"GET","path":"/","action":"list"}],
            "frontend":{"route":"/feature","operations":["list"]},
            "tests":{"api":[{"name":"list_ok"}]}
        }
    }

def render(env, tpl, **ctx):
    return env.get_template(tpl).render(**ctx)

def write(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def main():
    body = os.environ.get("ISSUE_BODY","")
    actor = os.environ.get("ACTOR","agent")
    issue = os.environ.get("ISSUE_NUMBER","")
    OUT.mkdir(exist_ok=True)
    spec = parse_comment_to_spec(body)
    feat = spec["feature"]
    name = feat["name"]
    ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

    env = Environment(
        loader=FileSystemLoader(str(TEMPL)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    ctx = {"spec": spec, "now": datetime.datetime.utcnow().isoformat()+"Z"}

    import yaml as _pyyaml
    with open("agent/policies/scaffolder.yml","r",encoding="utf-8") as f:
        paths = _pyyaml.safe_load(f)

    def fmt(p): return p.format(name=name, ts=ts)

    write(ROOT / fmt(paths["paths"]["backend"]["router"]),    render(env,"backend/router.py.j2", **ctx))
    write(ROOT / fmt(paths["paths"]["backend"]["models"]),    render(env,"backend/models.py.j2", **ctx))
    write(ROOT / fmt(paths["paths"]["backend"]["schemas"]),   render(env,"backend/schema.py.j2", **ctx))
    write(ROOT / fmt(paths["paths"]["backend"]["services"]),  render(env,"backend/service.py.j2", **ctx))
    write(ROOT / fmt(paths["paths"]["backend"]["repos"]),     render(env,"backend/repository.py.j2", **ctx))
    write(ROOT / fmt(paths["paths"]["backend"]["migration"]), render(env,"backend/migration.py.j2", **ctx))
    write(ROOT / fmt(paths["paths"]["backend"]["tests_api"]), render(env,"backend/tests_api.py.j2", **ctx))

    write(ROOT / fmt(paths["paths"]["frontend"]["page"]),     render(env,"frontend/page.tsx.j2", **ctx))
    write(ROOT / fmt(paths["paths"]["frontend"]["client"]),   render(env,"frontend/client.ts.j2", **ctx))

    # Try to wire router into app/main.py (best effort)
    main_py = ROOT / "app" / "main.py"
    if main_py.exists():
        txt = main_py.read_text(encoding="utf-8")
        imp = f"from app.api import {name} as {name}_router"
        if "from fastapi import FastAPI" in txt and imp not in txt:
            txt = txt.replace("from fastapi import FastAPI", f"from fastapi import FastAPI\n{imp}")
        if f"app.include_router({name}_router.router)" not in txt:
            txt += f"\napp.include_router({name}_router.router)\n"
        main_py.write_text(txt, encoding="utf-8")

    (OUT / "branch.txt").write_text(f"agent/impl/{name}-{ts}", encoding="utf-8")
    (OUT / "title.txt").write_text(f"feat({name}): scaffold via agent", encoding="utf-8")
    with open(OUT / "body.md","w",encoding="utf-8") as f:
        yaml.dump(spec, f)

if __name__ == "__main__":
    main()
