from datetime import datetime
from tracemalloc import start

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.docker.operators.docker import DockerOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="open-brewery-db-pipeline",
    default_args=default_args,
    description="A DAG to run the brewery pipeline",
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["brewery"],
) as dag:
    start = EmptyOperator(task_id="start")

    run_pipeline = DockerOperator(
        task_id="run_brewery_pipeline",
        image="brewery/brewery-pipeline:latest",
        container_name="brewery-pipeline",
        network_mode="breweries-net",
        api_version="auto",
        auto_remove="force",
        entrypoint="brewery-cli",
        command="pipeline",
        docker_url="unix://var/run/docker.sock",
        environment={
            "BREWERY_MINIO_ENDPOINT": "minio:9000",
            "BREWERY_MINIO_SECRET_KEY": "breweries",
        }
    )

    finish = EmptyOperator(task_id="finish")

    start >> run_pipeline >> finish  # type: ignore[operator]
