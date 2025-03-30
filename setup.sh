#!/bin/bash

SCRIPT_DIR="$(realpath $(dirname "${BASH_SOURCE[0]}"))"

export COMPOSE_BAKE=true

# Check if docker command is avaliable
[ ! -z "$DOCKER_COMPOSE_COMMAND" ] || {
    command docker compose --version >/dev/null 2>&1
    DOCKER_COMPOSE_COMMAND="docker compose"
} || {
    command docker-compose --version >/dev/null 2>&1
    DOCKER_COMPOSE_COMMAND="docker-compose"
} || {
    echo "docker compose and docker-compose are not installed. Please install or define DOCKER_COMPOSE_COMMAND"
    exit 1
}

# Secrets - Read only - Read from user
if [ -z "$BREWERIES_PASSWORD" ]; then
    # Read from .breweries_password file
    if [[ -f "$SCRIPT_DIR/.breweries_password" && -s "$SCRIPT_DIR/.breweries_password" ]]; then
        echo "Reading BREWERIES_PASSWORD from $SCRIPT_DIR/.breweries_password"
        BREWERIES_PASSWORD=$(cat "$SCRIPT_DIR/.breweries_password")
    else
        # Prompt for password
        echo "Please enter with BREWERIES_PASSWORD (Length 8: breweries): "
        read -s BREWERIES_PASSWORD

        if [ ${#BREWERIES_PASSWORD} -lt 8 ]; then
            echo "A senha deve ter pelo menos 8 caracteres."
            exit 1
        fi

        # Save password to .breweries_password file
        echo "$BREWERIES_PASSWORD" > "$SCRIPT_DIR/.breweries_password"
    fi
fi
export BREWERIES_PASSWORD

# Airflow
export AIRFLOW_VERSION="2.10.5"
export AIRFLOW_PROJ_DIR="$SCRIPT_DIR"/airflow
export AIRFLOW_UID=$(id -u)

# Spark
export SPARK_WAREHOUSE_BUCKET="spark-warehouse"

# Minio
export MINIO_DEFAULT_BUCKETS="breweries-data,$SPARK_WAREHOUSE_BUCKET"

# Postgres
export POSTGRES_DBS_LIST="airflow,lineage,catalog"
