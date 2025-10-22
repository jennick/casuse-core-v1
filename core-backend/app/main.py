from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db, Base, engine
from .jwks import router as jwks_router
from .auth import router as auth_router

app = FastAPI(title="Casuse Core API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(jwks_router)
app.include_router(auth_router)

Base.metadata.create_all(bind=engine)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    db.execute("SELECT 1")
    return {"status": "ready"}

@app.get("/api/tiles")
def tiles(authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing_token")
    token = authorization.split(" ", 1)[1]
    claims = jwt.get_unverified_claims(token)
    return {
        "user": claims.get("email"),
        "kpis": {"modules_up": 1, "alerts": 0, "latency_ms_p95": 120},
    }
