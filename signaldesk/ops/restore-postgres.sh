#!/usr/bin/env sh
set -eu
: "${POSTGRES_USER:?Set POSTGRES_USER in the environment}"
: "${DB_NAME:?Set DB_NAME in the environment}"
if [ "$#" -ne 1 ] || [ ! -s "$1" ]; then
  echo "Usage: $0 path/to/backup.dump" >&2
  exit 2
fi
echo "WARNING: this replaces objects in database '$DB_NAME'."
printf "Type RESTORE to continue: "
read answer
[ "$answer" = "RESTORE" ] || { echo "Restore cancelled."; exit 1; }
docker compose exec -T postgres pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$DB_NAME" < "$1"
echo "Restore completed. Verify application health and tenant data."
