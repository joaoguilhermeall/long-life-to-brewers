#!/bin/bash
set -e

POSTGRES_DBS_LIST="${POSTGRES_DBS_LIST:?}"

# Iter over the list of databases
for db in $(echo "${POSTGRES_DBS_LIST:?}" | tr ',' ' '); do
    # Check if database exists
    if psql -lqt | cut -d \| -f 1 | grep -qw "$db"; then
        echo "Database $db already exists, skipping creation."
        continue
    fi

    # Create the database
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        CREATE DATABASE $db;
        GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
done
