#!/usr/bin/env sh
set -eu
if [ "$#" -ne 1 ] || [ ! -s "$1" ]; then
  echo "Usage: $0 path/to/database.dump" >&2
  exit 2
fi
echo "WARNING: this replaces the SignalDesk database."
printf "Type RESTORE to continue: "
read answer
[ "$answer" = "RESTORE" ] || { echo "Restore cancelled."; exit 1; }
docker compose exec -T postgres sh -c 'pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$1"
echo "Restore command completed. Verify readiness and tenant data before resuming traffic."
