#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${1:-backups}"
CONTAINER_NAME="${2:-core-db}"
DB_USER="${POSTGRES_USER:-casuse}"
DB_NAME="${POSTGRES_DB:-casuse_core}"
STAMP="$(date +%F_%H%M%S)"
OUT="${BACKUP_DIR}/pgdump-${DB_NAME}-${STAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"
echo "==> Creating backup from container '$CONTAINER_NAME' (db=$DB_NAME user=$DB_USER)"
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$OUT"
echo "OK  ${OUT}"
