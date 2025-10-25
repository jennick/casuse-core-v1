Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..
docker compose down --remove-orphans
