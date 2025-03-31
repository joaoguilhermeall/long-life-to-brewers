FROM docker.io/python:3.10-bullseye

ARG SPARK_VERSION=3.4.4
ARG SPARK_MAJOR_VERSION=${SPARK_VERSION%.*}
ARG ICEBERG_VERSION=1.8.1

WORKDIR /tmp

ENV SPARK_HOME=/opt/spark

RUN apt-get update --yes && \
  apt-get install --yes --no-install-recommends \
  openjdk-11-jre-headless \
  ca-certificates-java \
  sudo \
  wget \
  vim \
  unzip \
  build-essential \
  software-properties-common \
  ssh && \
  apt-get clean && rm -rf /var/lib/apt/lists/* && \
  # Download Spark
  wget --progress=dot:giga https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
  tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
  chown -R root:root spark-${SPARK_VERSION}-bin-hadoop3 && \
  mv spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark && \
  rm -rf /tmp/*

# Spark additional jars
RUN wget --progress=dot:giga https://repo1.maven.org/maven2/org/apache/spark/spark-hadoop-cloud_2.12/${SPARK_VERSION}/spark-hadoop-cloud_2.12-${SPARK_VERSION}.jar && \
  # Iceberg Jars
  wget --progress=dot:giga https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-${SPARK_MAJOR_VERSION}_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-${SPARK_MAJOR_VERSION}_2.12-${ICEBERG_VERSION}.jar && \
  wget --progress=dot:giga  https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar && \
  # FS Jars - NEVER USE THE LATEST VERSION.  I hate Hadoop 3.4.1. S2 Hadoop 3.3.4
  wget --progress=dot:giga https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
  wget --progress=dot:giga https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.782/aws-java-sdk-bundle-1.12.782.jar && \
  # OpenLineage Jars
  wget --progress=dot:giga https://repo1.maven.org/maven2/io/openlineage/openlineage-spark_2.12/1.30.1/openlineage-spark_2.12-1.30.1.jar && \
  chmod 644 *.jar && \
  mv *.jar /opt/spark/jars/ && \
  rm -rf /tmp/*

# Optional env variables
ENV SPARK_HOME=/opt/spark
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip \
  PATH="${SPARK_HOME}/sbin:${SPARK_HOME}/bin:${PATH}"

WORKDIR ${SPARK_HOME}
RUN chmod u+x /opt/spark/sbin/* && chmod u+x /opt/spark/bin/*

ARG NOTEBOOKS_DIR=/opt/spark/notebooks

RUN mkdir -p ${NOTEBOOKS_DIR} && \
  pip install --no-cache-dir notebook==7.3.3 && \
  echo '#! /bin/sh' >> /bin/notebook && \
  echo 'export PYSPARK_DRIVER_PYTHON=jupyter-notebook' >> /bin/notebook && \
  echo "export PYSPARK_DRIVER_PYTHON_OPTS=\"--notebook-dir=${NOTEBOOKS_DIR} --ip='*' --NotebookApp.token='' --NotebookApp.password='' --port=8888 --no-browser --allow-root\"" >> /bin/notebook && \
  echo "pyspark" >> /bin/notebook && \
  chmod u+x /bin/notebook

COPY ./conf/spark-defaults.conf /opt/spark/conf
COPY entrypoint.sh /opt/spark/bin

ENTRYPOINT ["/opt/spark/bin/entrypoint.sh"]
CMD [ "notebook" ]
