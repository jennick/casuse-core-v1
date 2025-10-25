from fastapi import FastAPI, Depends, HTTPException, status, Request
from pydantic import BaseModel
import os, jwt

# === Config ===
JWT_SECRET      = os.environ.get("JWT_SECRET", "devsupersecret_change_me")
JWT_ALG         = os.environ.get("JWT_ALG", "HS256")
MODULE_NAME     = os.environ.get("MODULE_NAME", "billing")     # << module-ident
REQUIRED_ROLE   = os.environ.get("REQUIRED_ROLE", "billing")   # << RBAC default
PORT            = int(os.environ.get("PORT", "8000"))          # uvicorn-port hint (cosmetisch)

app = FastAPI(
    title=f"{MODULE_NAME.capitalize()} Service",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url=None,
)

# === Auth / claims helpers ===
class Claims(BaseModel):
    sub: str
    role: str | None = None

def get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return auth.split(" ", 1)[1].strip()

def decode_and_validate(token: str) -> Claims:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    sub = payload.get("sub")
    role = payload.get("role")
    if not sub:
        raise HTTPException(status_code=401, detail="Missing sub in token")
    return Claims(sub=sub, role=role)

def require_role(claims: Claims) -> None:
    if claims.role != REQUIRED_ROLE:
        raise HTTPException(status_code=403, detail=f"Forbidden for role '{claims.role}', requires '{REQUIRED_ROLE}'")

def current_claims(request: Request) -> Claims:
    token = get_bearer_token(request)
    return decode_and_validate(token)

def role_guard(claims: Claims = Depends(current_claims)) -> Claims:
    require_role(claims)
    return claims

# === Health & ready ===
@app.get("/healthz")
def healthz():
    return {"ok": True, "module": MODULE_NAME, "port": PORT}

@app.get("/readyz")
def readyz():
    # hier kun je DB/queue checks toevoegen
    return {"ready": True, "module": MODULE_NAME}

@app.get("/api/healthz")
def api_healthz():
    return {"ok": True, "scope": "api", "module": MODULE_NAME}

# === Demo endpoints ===
@app.get("/whoami")
def whoami(claims: Claims = Depends(current_claims)):
    return {"sub": claims.sub, "role": claims.role}

@app.get("/secure/ping")
def secure_ping(claims: Claims = Depends(role_guard)):
    return {"ok": True, "role": claims.role, "msg": f"Hello {claims.sub} from {MODULE_NAME} module!"}

@app.get("/")
def root():
    return {
        "service": f"module-{MODULE_NAME}-backend",
        "health": "/healthz",
        "ready": "/readyz",
        "api_health": "/api/healthz",
        "secure": "/secure/ping",
    }
