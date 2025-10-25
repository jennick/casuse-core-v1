# Modules runbook (local, prod-like)

This repository uses a central Traefik (from core) and lets each module
register itself via Docker labels on the shared external network `casuse_edge`.

## One-time preparation
```bash
docker network create casuse_edge
docker compose up -d core-traefik   # run from repo root; leaves your core as-is
```

## Start a module
Pick one of the generated compose files below and start it independently:
```bash
docker compose -f modules/<module>/<module>.compose.yml up -d --build
```

## Stop a module
```bash
docker compose -f modules/<module>/<module>.compose.yml down
```

## Access locally
- Frontend: http://localhost:10400/<module>/
- API:      http://localhost:10400/<module>/api/...
- Health:   http://localhost:10400/<module>/healthz

## Generated modules
[
  {
    "module": "billing",
    "compose_path": "modules/billing/billing.compose.yml",
    "frontend_port_internal": 18001,
    "backend_port_internal": 19001,
    "postgres_version": "16"
  },
  {
    "module": "sales",
    "compose_path": "modules/sales/sales.compose.yml",
    "frontend_port_internal": 18002,
    "backend_port_internal": 19002,
    "postgres_version": "17"
  },
  {
    "module": "website",
    "compose_path": "modules/website/website.compose.yml",
    "frontend_port_internal": 18003,
    "backend_port_internal": 19003,
    "postgres_version": "18"
  }
]
