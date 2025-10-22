# Casuse Core — v1 Bootstrap (core-backend + core-frontend + Traefik)

Eerste werkende baseline volgens jouw architectuur. Inclusief:
- OIDC (code + PKCE), JWKS & discovery
- Core loginpagina → dashboard
- Traefik (dev) met security headers, rate limiting, retries
- Postgres 15 (core-db)
- Exacte poorten: backend 9000, frontend 8200, traefik 10400

## Snel starten (development)

```bash
docker compose up -d --build
# open: http://localhost:10400
# login: admin.one@casuse.local / Casuse!2025
```

## Productie (korte checklist)
- Traefik TLS/ACME + Host-routes (`core.example.com`)
- `sslmode=require` voor DB
- Secrets via secret manager (geen .env in prod)
- Strikte JWKS-verify op alle protected endpoints
- Key-rotatie CLI toevoegen

## Repo naam (advies)
**casuse-core-v1**

## Push naar GitHub (voorbeeld)
```bash
git init
git add .
git commit -m "feat(core): v1 bootstrap (OIDC+PKCE, JWKS, Traefik, PG15)"
git branch -M main
git remote add origin https://github.com/<jouw-account>/casuse-core-v1.git
git push -u origin main
```
