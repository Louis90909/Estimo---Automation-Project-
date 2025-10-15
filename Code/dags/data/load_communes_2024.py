import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

CSV_SRC = "/opt/airflow/data/communesdvf2024.csv"

def check_csv():
    if not os.path.exists(CSV_SRC):
        raise FileNotFoundError(CSV_SRC)

with DAG(
    dag_id="load_communes_2024",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"owner": "airflow", "retries": 0},
):
    PythonOperator(task_id="check_csv", python_callable=check_csv)
