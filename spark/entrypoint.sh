#!/bin/bash

_REST_CATALOG_ENDPOINT=${REST_CATALOG_ENDPOINT:?}

_AWS_ENDPOINT=${AWS_ENDPOINT:?}
_AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:?}
_AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:?}
_AWS_DEFAULT_BUCKET=${AWS_DEFAULT_BUCKET:?}

_SPARK_LOG_DIR=${SPARK_LOG_DIR:-/tmp/spark-events}

_MARQUEZ_API_ENDPOINT=${MARQUEZ_API_ENDPOINT:-}

if [[ "$_SPARK_LOG_DIR" != /* ]]; then
    mkdir -p ${_SPARK_LOG_DIR}
fi

cat <<EOF >/opt/spark/conf/spark-defaults.conf
spark.master=spark://$(hostname):7077

spark.log.level=WARN

# Spark memory
spark.driver.memory=500m
spark.executor.memory=500m
spark.executor.cores=1

# Spark shuffle
spark.shuffle.service.enabled=false

spark.dynamicAllocation.enabled=true
spark.dynamicAllocation.executorIdleTimeout=60
spark.dynamicAllocation.minExecutors=0
spark.dynamicAllocation.schedulerBacklogTimeout=1

spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions

spark.sql.catalogImplementation=in-memory

spark.sql.catalog.brewery=org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.brewery.type=rest
spark.sql.catalog.brewery.io-impl=org.apache.iceberg.aws.s3.S3FileIO
spark.sql.catalog.brewery.uri=${_REST_CATALOG_ENDPOINT}
spark.sql.catalog.brewery.s3.endpoint=${_AWS_ENDPOINT}
spark.sql.catalog.brewery.warehouse=s3a://${_AWS_DEFAULT_BUCKET}/tablespace

spark.sql.defaultCatalog=brewery

spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.committer.name=directory
fs.s3a.connection.ssl.enabled=false
spark.hadoop.fs.s3a.endpoint=${_AWS_ENDPOINT}
spark.hadoop.fs.s3a.access.key=${_AWS_ACCESS_KEY_ID}
spark.hadoop.fs.s3a.secret.key=${_AWS_SECRET_ACCESS_KEY}

spark.eventLog.enabled=true
spark.eventLog.dir=${_SPARK_LOG_DIR}
spark.history.fs.logDirectory=${_SPARK_LOG_DIR}
EOF

if [ ! -z "${_MARQUEZ_API_ENDPOINT}" ]; then
    cat <<EOF >>/opt/spark/conf/spark-defaults.conf

spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener

spark.openlineage.transport.url=${_MARQUEZ_API_ENDPOINT}
spark.openlineage.transport.type=http
spark.openlineage.namespace=spark-namespace
spark.openlineage.transport.endpoint=/api/v1/lineage
EOF
fi

start-master.sh -p 7077
start-worker.sh spark://$(hostname):7077

tail -f /opt/spark/logs/*.out
