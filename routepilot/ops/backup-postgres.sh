#!/usr/bin/env sh
set -eu
BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
API_CID="$(docker compose ps -q api)"
[ -n "$API_CID" ] || { echo "RoutePilot API container is not running" >&2; exit 1; }
docker compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$BACKUP_DIR/routepilot_$STAMP.dump"
docker run --rm --volumes-from "$API_CID" -v "$PWD/$BACKUP_DIR:/backup" alpine:3.20 sh -c "tar -czf /backup/routepilot_proofs_$STAMP.tar.gz -C /data/proofs ."
test -s "$BACKUP_DIR/routepilot_$STAMP.dump"
test -s "$BACKUP_DIR/routepilot_proofs_$STAMP.tar.gz"
echo "Database and proof-file backups created in $BACKUP_DIR"
