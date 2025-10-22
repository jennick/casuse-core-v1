# core-backend/app/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from secrets import token_urlsafe

from .db import get_db, Base, engine
from .models import User, OAuthClient, AuthCode, RefreshToken
from .security import password_hash, password_verify, make_jwt
from .utils import verify_pkce
from .config import settings

router = APIRouter()

# Zorg dat de tabellen bestaan (dev/demo)
Base.metadata.create_all(bind=engine)

def utcnow() -> datetime:
    # Naive UTC (consistent in hele file)
    return datetime.utcnow()

def seed_dev(db: Session):
    """Seed minimal dev-data (client + admin user) idempotent."""
    if not db.query(OAuthClient).first():
        db.add(OAuthClient(
            client_id="core-fe",
            client_name="Core Frontend",
            redirect_uri="/"   # FE root
        ))
    if not db.query(User).filter_by(email="admin.one@casuse.local").first():
        db.add(User(
            email="admin.one@casuse.local",
            password_hash=password_hash("Casuse!2025"),
            roles="admin"
        ))
    db.commit()

@router.get("/auth/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    code_challenge: str,
    code_challenge_method: str = "S256",
    db: Session = Depends(get_db),
):
    """
    Vereenvoudigde authorization endpoint voor code + PKCE.
    - Valideert client & redirect_uri prefix
    - Maakt een Authorization Code met 5 min geldigheid (naive UTC)
    - Redirect terug naar redirect_uri met ?code=...&state=...
    """
    seed_dev(db)

    if response_type != "code":
        raise HTTPException(status_code=400, detail="unsupported_response_type")

    client = db.query(OAuthClient).filter_by(client_id=client_id).first()
    if not client or not redirect_uri.startswith(client.redirect_uri):
        raise HTTPException(status_code=400, detail="invalid_client_or_redirect")

    # DEMO: “ingelogde” user is seeded admin (prod zou hier een echte session/mfa zitten)
    user = db.query(User).filter_by(email="admin.one@casuse.local").first()
    if not user:
        raise HTTPException(status_code=400, detail="user_missing")

    code = token_urlsafe(32)
    db.add(AuthCode(
        code=code,
        user_id=user.id,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        scope=scope,
        expires_at=utcnow() + timedelta(minutes=5),  # naive UTC
    ))
    db.commit()

    return RedirectResponse(url=f"{redirect_uri}?code={code}&state={state}")

@router.post("/auth/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(None),
    redirect_uri: str = Form(None),
    client_id: str = Form(...),
    code_verifier: str = Form(None),
    refresh_token: str = Form(None),
    db: Session = Depends(get_db),
):
    """
    Token endpoint:
    - authorization_code + PKCE
    - refresh_token
    Retourneert: { token_type, access_token, expires_in, refresh_token? }
    """
    now = utcnow()

    if grant_type == "authorization_code":
        if not code or not code_verifier or not redirect_uri:
            raise HTTPException(status_code=400, detail="missing_params")

        ac = db.query(AuthCode).filter_by(code=code).first()

        # Expiratie-check: alles naive UTC
        if not ac or ac.expires_at is None or ac.expires_at < now:
            raise HTTPException(status_code=400, detail="invalid_code")

        # PKCE-verify
        if not verify_pkce(code_verifier, ac.code_challenge):
            raise HTTPException(status_code=400, detail="invalid_verifier")

        # Client check (redirect check deden we in /authorize; hier minimaal client_id match)
        if ac.client_id != client_id:
            raise HTTPException(status_code=400, detail="invalid_client")

        user = ac.user
        access, jti = make_jwt(
            db,
            sub=str(user.id),
            email=user.email,
            roles=user.roles.split(","),
        )

        rt = RefreshToken(
            jti=token_urlsafe(24),
            user_id=user.id,
            expires_at=now + timedelta(days=settings.refresh_ttl_days),  # naive UTC
            revoked=False,
        )

        # Code single-use maken
        db.add(rt)
        db.delete(ac)
        db.commit()

        return {
            "token_type": "Bearer",
            "access_token": access,
            "expires_in": 60 * settings.access_ttl_min,
            "refresh_token": rt.jti,
        }

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(status_code=400, detail="missing_refresh_token")

        rt = db.query(RefreshToken).filter_by(jti=refresh_token, revoked=False).first()
        if not rt or rt.expires_at is None or rt.expires_at < now:
            raise HTTPException(status_code=400, detail="invalid_refresh")

        user = rt.user
        access, jti = make_jwt(
            db,
            sub=str(user.id),
            email=user.email,
            roles=user.roles.split(","),
        )
        # (optioneel) rotating refresh tokens: nieuwe RT uitgeven en oude revoken.
        # Voor demo laten we dezelfde RT staan.

        return {
            "token_type": "Bearer",
            "access_token": access,
            "expires_in": 60 * settings.access_ttl_min,
            "refresh_token": refresh_token,
        }

    else:
        raise HTTPException(status_code=400, detail="unsupported_grant")

@router.post("/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Eenvoudige login-check (alleen om de demo-flow te starten).
    In prod zou dit een echte sessie + MFA + consent route triggeren.
    """
    seed_dev(db)
    user = db.query(User).filter_by(email=email).first()
    if not user or not password_verify(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
    return {"ok": True}
