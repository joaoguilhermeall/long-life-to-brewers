#!/bin/bash

# - All variables exported here are used to run brewery-cli
# - If you want to run the script, please configure the variables and source this file
# - Before running the script make sure you have already run the setup.sh script
# - Only required variables are uncommented

# export BREWERY_LOG_LEVEL=
# export BREWERY_LOG_FORMAT=
# export BREWERY_LOG_FILE=

export BREWERY_MINIO_ENDPOINT=localhost:9000
export BREWERY_MINIO_ACCESS_KEY=minio
export BREWERY_MINIO_SECRET_KEY=${BREWERIES_PASSWORD:?}
export BREWERY_MINIO_BUCKET_NAME="breweries-data"
# export BREWERY_MINIO_SECURE=0

# export BREWERY_EXTRACT_NUM_PARALLEL_TASKS=10

# export BREWERY_BRONZE_PATH=bronze
# export BREWERY_BRONZE_OVERWRITE=1
