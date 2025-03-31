#!/bin/bash

set -e

SCRIPT_DIR="$(realpath $(dirname "${BASH_SOURCE[0]}"))"

source "$SCRIPT_DIR"/setup.sh

# Building services
docker compose build

# Build local image
echo "Building brewery pipeline image..."

docker image build \
    --build-arg BASE_IMAGE=$SPARK_BASE_IMAGE \
    --tag brewery/brewery-pipeline:latest \
    --tag brewery/brewery-pipeline:"$BREWERIES_VERSION" \
    .

echo "Image brewery/brewery-pipeline:$BREWERIES_VERSION built successfully."

echo "Starting services..."

docker compose up -d spark

case "$1" in
bronze)
    echo "Selecting bronze pipeline stage..."
    stage="bronze"
    ;;
silver)
    echo "Selecting silver pipeline stage..."
    stage="silver"
    ;;
gold)
    echo "Selecting gold pipeline stage..."
    stage="gold"
    ;;
pipeline)
    echo "Selecting pipeline stage..."
    stage="pipeline"
    ;;
*)
    echo "No stage selected... defaulting to pipeline stage."
    stage="pipeline"
    ;;
esac

docker container run \
    --rm \
    --network breweries-net \
    --env BREWERY_MINIO_ENDPOINT=minio:9000 \
    --env BREWERY_MINIO_SECRET_KEY=${BREWERIES_PASSWORD} \
    --name brewery-pipeline \
    --volume ./brewery.log:/brewery/brewery.log \
    brewery/brewery-pipeline:"$BREWERIES_VERSION" \
    $stage

echo "Pipeline completed."
echo "Please check notebook for results: http://localhost:8888/doc/tree/brewery-explore.ipynb"
