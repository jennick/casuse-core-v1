from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    roles = Column(String(255), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OAuthClient(Base):
    __tablename__ = "oauth_clients"
    id = Column(Integer, primary_key=True)
    client_id = Column(String(100), unique=True, nullable=False)
    client_name = Column(String(200), nullable=False)
    redirect_uri = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuthCode(Base):
    __tablename__ = "auth_codes"
    id = Column(Integer, primary_key=True)
    code = Column(String(200), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_id = Column(String(100), nullable=False)
    code_challenge = Column(String(128), nullable=False)
    code_challenge_method = Column(String(20), default="S256")
    scope = Column(String(255), default="openid profile email")
    expires_at = Column(DateTime, nullable=False)
    user = relationship("User")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    jti = Column(String(64), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    user = relationship("User")

class JwkKey(Base):
    __tablename__ = "jwk_keys"
    id = Column(Integer, primary_key=True)
    kid = Column(String(64), unique=True, nullable=False)
    alg = Column(String(10), nullable=False)
    kty = Column(String(10), nullable=False)
    n = Column(Text, nullable=True)
    e = Column(Text, nullable=True)
    d = Column(Text, nullable=True)  # in prod versleuteld bewaren
    crv = Column(String(20), nullable=True)
    x = Column(Text, nullable=True)
    y = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
