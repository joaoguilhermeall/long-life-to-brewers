from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


# Define the function to say hello
def say_hello(task_name):
    print(f"Hello from {task_name}!")

# Define the DAG
with DAG(
    dag_id="say-hello",
    schedule_interval="@daily",
    start_date=datetime(2025, 3, 28),
    catchup=False,
    description="A simple DAG to say hello",
) as dag:
    # Define tasks
    task1 = PythonOperator(
        task_id="say_hello_task1",
        python_callable=say_hello,
        op_args=["Task 1"],
    )

    task2 = PythonOperator(
        task_id="say_hello_task2",
        python_callable=say_hello,
        op_args=["Task 2"],
    )

    task3 = PythonOperator(
        task_id="say_hello_task3",
        python_callable=say_hello,
        op_args=["Task 3"],
    )

    # Set task dependencies
    task1 >> task2 >> task3 # type: ignore[operator]
