#!/bin/bash

set -e

_AWS_ENDPOINT="${AWS_ENDPOINT:?}"
_AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:?}"
_AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:?}"
_AWS_DEFAULT_BUCKETS="${AWS_DEFAULT_BUCKETS:?}"

tries=0
max_tries=10

until (/usr/bin/mc config host add minio $_AWS_ENDPOINT $_AWS_ACCESS_KEY_ID $_AWS_SECRET_ACCESS_KEY); do
    if [ "$tries" == "$max_tries" ]; then
        echo "Max tries reached. Exiting..."
        exit 1
    fi

    echo '...waiting...' && sleep 5 && tries=$((tries + 1))
done

for bucket in $(echo "${_AWS_DEFAULT_BUCKETS:?}" | tr ',' ' '); do
    if ! /usr/bin/mc ls minio/$bucket; then
        /usr/bin/mc mb minio/$bucket
        /usr/bin/mc anonymous set public minio/$bucket
    else
        echo "Bucket $bucket already exists and is public."
    fi
done

echo "Minio initialization complete."
