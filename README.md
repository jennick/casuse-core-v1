# Casuse‑Core Dashboard MVP (core-backend/core-frontend structuur)

## Plaatsing in jouw repo
Pak uit naar:
```
C:\dev\casuse-core-v1\
  core-backend\app\main.py
  core-backend\requirements.txt
  core-frontend\package.json
  docker-compose.dashboard.core.yml
```
(als je al `core-backend` en `core-frontend` hebt, kopieer inhoud in die mappen; overschrijf niets wat je wil behouden).

## Lokaal starten zonder Docker
Backend:
```
cd core-backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --port 9000 --reload
```
Frontend:
```
cd core-frontend
npm i
echo VITE_API_BASE=http://localhost:9000 > .env.local
echo VITE_WS_BASE=ws://localhost:9000 >> .env.local
npm run preview  # 8200
```
Open: http://localhost:8200

## Via Traefik (Docker)
```
docker network create traefik_proxy 2>$null || true
docker compose -f docker-compose.dashboard.core.yml up -d --build core_backend core_frontend
```
Open: http://localhost:10400  (frontend), API op /core
