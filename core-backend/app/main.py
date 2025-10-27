import os, asyncio, random
from datetime import datetime, timezone
from typing import Optional, List, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

APP_NAME = "casuse-core-dashboard"
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
API_PREFIX = os.getenv("API_PREFIX", "/core")

app = FastAPI(title="Casuse-Core Dashboard API", version=APP_VERSION)

ALLOWED_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",")] if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Latency(BaseModel):
    p50: int = 40
    p95: int = 120
    p99: int = 250

class DBStatus(BaseModel):
    connections: int = 8
    status: str = "ok"

class QueueStatus(BaseModel):
    incoming: int = 0
    outgoing: int = 0
    oldest_s: int = 0

class ModuleStatus(BaseModel):
    name: str
    env: str = "dev"
    version: str = "0.0.0+dev"
    health: str = "UP"
    uptime_s: int = 0
    rps: float = 0.0
    latency_ms: Latency = Latency()
    errors_5xx_per_min: float = 0.0
    db: DBStatus = DBStatus()
    queue: QueueStatus = QueueStatus()
    last_deploy_ts: Optional[str] = None
    feature_flags: Dict[str, bool] = {}

class SummaryKPIs(BaseModel):
    active_users: int
    requests_per_min: int
    success_rate_pct: float
    latency_ms_p50: int
    latency_ms_p95: int
    errors_last_hour: int
    modules_up: int
    modules_total: int

class Alert(BaseModel):
    ts: str
    sev: str
    source: str
    title: str
    status: str = "open"
    owner: Optional[str] = None

class DashboardSummary(BaseModel):
    ts: str
    kpis: SummaryKPIs
    modules: list[ModuleStatus]
    alerts: list[Alert]

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

MODULES = ["core", "website", "sales", "billing", "inventory"]

def mock_module_status(name: str) -> ModuleStatus:
    up = random.random() > 0.05
    health = "UP" if up else ("DEGRADED" if random.random() > 0.5 else "DOWN")
    return ModuleStatus(
        name=name,
        env=os.getenv("ENVIRONMENT", "dev"),
        version=f"1.0.{random.randint(0,5)}+{random.choice(['abcd','ef01','dead','beef'])}",
        health=health,
        uptime_s=random.randint(1000, 100000),
        rps=round(random.uniform(2, 40), 1),
        latency_ms=Latency(p50=random.randint(25, 60), p95=random.randint(80, 200), p99=random.randint(150, 450)),
        errors_5xx_per_min=round(random.uniform(0, 3), 2) if health != "DOWN" else 0.0,
        db=DBStatus(connections=random.randint(3, 20), status="ok" if health == "UP" else "warn"),
        queue=QueueStatus(incoming=random.randint(0, 10), outgoing=random.randint(0, 10), oldest_s=random.randint(0, 60)),
        last_deploy_ts=_now_iso(),
        feature_flags={"ff_example": random.random() > 0.5}
    )

def mock_alerts() -> list[Alert]:
    pool = [
        ("SEV2", "website", "Error rate > 2% (5 min)"),
        ("SEV3", "billing", "Payment provider timeout spikes"),
        ("SEV1", "core", "JWT key rotation overdue"),
    ]
    out: list[Alert] = []
    if random.random() > 0.6:
        sev, src, title = random.choice(pool)
        out.append(Alert(ts=_now_iso(), sev=sev, source=src, title=title))
    return out

def mock_summary() -> DashboardSummary:
    modules = [mock_module_status(m) for m in MODULES]
    up = sum(1 for m in modules if m.health == "UP")
    active_users = random.randint(2, 35)
    rpm = int(sum(m.rps for m in modules) * 60)
    p50 = int(sum(m.latency_ms.p50 for m in modules) / len(modules))
    p95 = int(sum(m.latency_ms.p95 for m in modules) / len(modules))
    kpis = SummaryKPIs(
        active_users=active_users,
        requests_per_min=rpm,
        success_rate_pct=round(100 - random.uniform(0, 2.5), 2),
        latency_ms_p50=p50,
        latency_ms_p95=p95,
        errors_last_hour=random.randint(0, 100),
        modules_up=up,
        modules_total=len(modules),
    )
    return DashboardSummary(ts=_now_iso(), kpis=kpis, modules=modules, alerts=mock_alerts())

@app.get("/healthz")
def healthz():
    return {"status": "ok", "ts": _now_iso(), "app": APP_NAME, "version": APP_VERSION}

@app.get("/readyz")
def readyz():
    return {"status": "ready", "ts": _now_iso()}

@app.get(f"{API_PREFIX}/dashboard/summary")
def get_summary():
    return mock_summary().model_dump()

@app.get(f"{API_PREFIX}/modules")
def get_modules():
    return [m.model_dump() for m in mock_summary().modules]

@app.get(f"{API_PREFIX}/alerts")
def get_alerts():
    return [a.model_dump() for a in mock_summary().alerts]

@app.get(f"{API_PREFIX}/sessions/active")
def get_active_sessions():
    import string
    n = random.randint(4, 18)
    users = [{
        "user": f"user{i}@example.com",
        "role": "manager" if i % 5 == 0 else "seller",
        "module": random.choice(MODULES),
        "route": "/",
        "last_seen_ts": _now_iso(),
        "session_id": "s_" + ''.join(random.choices(string.ascii_lowercase+string.digits, k=8)),
        "ip_country": random.choice(["MX", "BE", "US"])
    } for i in range(n)]
    return {"ts": _now_iso(), "count": len(users), "sessions": users}

clients: list[WebSocket] = []

@app.websocket(f"{API_PREFIX}/stream")
async def ws_stream(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await asyncio.sleep(2.0)
            s = mock_summary()
            payload = {
                "ts": s.ts,
                "kpis": s.kpis.model_dump(),
                "modules": [{
                    "name": m.name, "health": m.health, "rps": m.rps,
                    "latency_ms": m.latency_ms.model_dump(), "errors_5xx_per_min": m.errors_5xx_per_min
                } for m in s.modules],
                "alerts": [a.model_dump() for a in s.alerts],
            }
            await ws.send_json(payload)
    except WebSocketDisconnect:
        pass
    finally:
        if ws in clients:
            clients.remove(ws)
