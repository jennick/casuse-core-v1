Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..

# 1) Certs genereren als ze ontbreken
if (-not (Test-Path ".\traefik\certs\core.local.crt") -or -not (Test-Path ".\traefik\certs\core.local.key")) {
  Write-Host "=> Generating self-signed cert..."
  & .\scripts\gen-selfsigned.ps1
}

# 2) Starten met prod-like overlay
docker compose down --remove-orphans
docker compose --env-file .env.prod.local `
  -f docker-compose.yml -f docker-compose.prod.local.yml `
  up -d --build core-traefik core-backend core-frontend core-db

docker compose ps
Write-Host "Open: https://core.127.0.0.1.nip.io:10443/"

