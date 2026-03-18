#!/bin/bash
set -euo pipefail

pg_restore \
  --username="$POSTGRES_USER" \
  --dbname="$POSTGRES_DB" \
  --verbose \
  --no-owner \
  --no-acl \
  /docker-entrypoint-initdb.d/db.dump