#!/usr/bin/env sh
set -eu
BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$BACKUP_DIR/signaldesk_$STAMP.dump"
test -s "$BACKUP_DIR/signaldesk_$STAMP.dump"
echo "Database backup created: $BACKUP_DIR/signaldesk_$STAMP.dump"
