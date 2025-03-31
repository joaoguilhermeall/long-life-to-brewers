#!/bin/bash

set -ex

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
