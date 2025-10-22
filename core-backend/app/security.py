# core-backend/app/security.py
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy.orm import Session
from .models import JwkKey
from .config import settings
from secrets import token_urlsafe
from Crypto.PublicKey import RSA  # pycryptodome
import bcrypt
import hashlib  # <- gebruik hashlib.sha256 voor pre-hash

PEPPER = os.getenv("CORE_PEPPER", "dev-pepper")

def get_active_rsa(db: Session):
    k = db.query(JwkKey).filter_by(active=True, alg="RS256").first()
    if not k:
        key = RSA.generate(2048)
        n, e, d = key.n, key.e, key.d
        kid = token_urlsafe(8)
        jk = JwkKey(kid=kid, alg="RS256", kty="RSA", n=str(n), e=str(e), d=str(d), active=True)
        db.add(jk); db.commit(); db.refresh(jk)
        k = jk
    return k

def password_hash(password: str) -> str:
    # pre-hash om bcrypt 72-byte limiet te vermijden
    pre = hashlib.sha256((password + PEPPER).encode()).digest()
    return bcrypt.hashpw(pre, bcrypt.gensalt()).decode()

def password_verify(password: str, pw_hash: str) -> bool:
    pre = hashlib.sha256((password + PEPPER).encode()).digest()
    return bcrypt.checkpw(pre, pw_hash.encode())

def make_jwt(db: Session, sub: str, email: str, roles: list[str], ttl_min: int = None) -> tuple[str,str]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ttl_min or settings.access_ttl_min)
    k = get_active_rsa(db)
    private_key = RSA.construct((int(k.n), int(k.e), int(k.d))).export_key()
    claims = {
        "iss": settings.issuer,
        "sub": sub,
        "aud": settings.audience,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "email": email,
        "roles": roles,
    }
    token = jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": k.kid})
    jti = token_urlsafe(16)
    return token, jti
