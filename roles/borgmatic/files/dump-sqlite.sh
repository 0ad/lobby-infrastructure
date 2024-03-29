#!/bin/sh

# Helper script for borgmatic to dump SQLite databases.
#
# Necessary as the version of borgmatic in Debian/bookworm doesn't
# support backing up SQLite databases natively and we do want to use
# the "backup" command instead of the "dump" command used by borgmatic
# anyway.

set -e

DB_PATH="$1"
DB_NAME="$2"

if [ "$DB_PATH" = "" ]; then
  echo "Usage: $0 database_path database_name"
  exit 1
fi

if [ ! -f "$DB_PATH" ]; then
  echo "Invalid database path"
  exit 1
fi

if [ "$DB_NAME" = "" ]; then
  echo "Missing database name."
  exit 1
fi

mkdir -p /tmp/borgmatic/sqlite/

sqlite3 "$DB_PATH" ".timeout 10000" ".backup /tmp/borgmatic/sqlite/$DB_NAME.sqlite"
