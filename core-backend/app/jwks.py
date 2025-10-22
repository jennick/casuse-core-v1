from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .db import get_db
from .models import JwkKey

router = APIRouter()

@router.get("/oauth/.well-known/openid-configuration")
def discovery():
    return {
        "issuer": "http://core.local",
        "authorization_endpoint": "/auth/authorize",
        "token_endpoint": "/auth/token",
        "jwks_uri": "/oauth/jwks.json",
        "scopes_supported": ["openid", "profile", "email"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
    }

@router.get("/oauth/jwks.json")
def jwks(db: Session = Depends(get_db)):
    keys = db.query(JwkKey).filter_by(active=True, alg="RS256").all()
    jwks = {"keys": []}
    for k in keys:
        jwks["keys"].append({
            "kid": k.kid,
            "kty": k.kty,
            "alg": k.alg,
            "use": "sig",
            "n": k.n,
            "e": k.e,
        })
    return jwks
