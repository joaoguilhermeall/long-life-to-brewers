FROM docker.io/apache/airflow:2.10.5-python3.10

USER root

RUN apt-get update && \
  apt-get install -y --no-install-recommends build-essential vim && \
  apt-get autoremove -yqq --purge && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /opt/airflow/dags/*

USER airflow

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
