#!/bin/bash

cat <<EOF >>/opt/spark/conf/spark-defaults.conf

spark.master=spark://$(hostname):7077
EOF

mkdir -p /tmp/spark-events

start-master.sh -p 7077
start-worker.sh spark://$(hostname):7077
start-history-server.sh
start-thriftserver.sh --driver-java-options "-Dderby.system.home=/tmp/derby"

tail -f /opt/spark/logs/*.out
