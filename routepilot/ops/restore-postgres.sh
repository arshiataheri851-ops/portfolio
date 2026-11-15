#!/usr/bin/env sh
set -eu
if [ "$#" -ne 2 ] || [ ! -s "$1" ] || [ ! -s "$2" ]; then
  echo "Usage: $0 database.dump proofs.tar.gz" >&2
  exit 2
fi
echo "WARNING: this replaces the RoutePilot database and proof-file volume."
printf "Type RESTORE to continue: "
read answer
[ "$answer" = "RESTORE" ] || { echo "Restore cancelled."; exit 1; }
API_CID="$(docker compose ps -q api)"
[ -n "$API_CID" ] || { echo "RoutePilot API container is not running" >&2; exit 1; }
docker compose exec -T postgres sh -c 'pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$1"
docker run --rm --volumes-from "$API_CID" -v "$PWD/$(dirname "$2"):/backup:ro" alpine:3.20 sh -c "tar -xzf /backup/$(basename "$2") -C /data/proofs"
echo "Restore commands completed. Verify readiness and proof downloads before resuming traffic."
