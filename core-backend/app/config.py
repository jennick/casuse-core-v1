from pydantic import BaseModel
import os

class Settings(BaseModel):
    env: str = os.getenv("CORE_ENV", "development")
    issuer: str = os.getenv("CORE_ISSUER", "http://core.local")
    audience: str = os.getenv("CORE_AUDIENCE", "core-api")
    access_ttl_min: int = int(os.getenv("CORE_ACCESS_TTL_MIN", "20"))
    refresh_ttl_days: int = int(os.getenv("CORE_REFRESH_TTL_DAYS", "14"))
    alg: str = os.getenv("CORE_JWT_ALG", "RS256")
    db_dsn: str = (
        f"postgresql+psycopg://{os.getenv('CORE_DB_USER','coreapp')}:"
        f"{os.getenv('CORE_DB_PASSWORD','coreapp_pw')}@{os.getenv('CORE_DB_HOST','core-db')}:"
        f"{os.getenv('CORE_DB_PORT','5432')}/{os.getenv('CORE_DB_NAME','coredb')}"
    )
    db_sslmode: str = os.getenv("CORE_DB_SSLMODE", "disable")
    cors_allowed_origins: list[str] = os.getenv(
        "CORE_CORS_ALLOWED_ORIGINS", "http://localhost:10400,http://localhost:8200"
    ).split(",")

settings = Settings()
