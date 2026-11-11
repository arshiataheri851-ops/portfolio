#!/usr/bin/env sh
set -eu
: "${POSTGRES_USER:?Set POSTGRES_USER in the environment}"
: "${DB_NAME:?Set DB_NAME in the environment}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$BACKUP_DIR/${DB_NAME}_$STAMP.dump"
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$DB_NAME" -Fc > "$OUT"
test -s "$OUT"
echo "Backup created: $OUT"
