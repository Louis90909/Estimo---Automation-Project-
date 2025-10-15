import os, gzip, io
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

CSV_PATH = os.environ.get("DVF_CSV_PATH", "/opt/airflow/data/full.csv.gz")
COPY_SQL = """
COPY dvf_full_raw FROM STDIN
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', ENCODING 'UTF8');
"""

def load_dvf():
    hook = PostgresHook(postgres_conn_id="estimo_postgres")
    conn = hook.get_conn()
    cur = conn.cursor()
    with gzip.open(CSV_PATH, "rb") as gz:
        text = io.TextIOWrapper(gz, encoding="utf-8", newline="")
        cur.copy_expert(COPY_SQL, file=text)
    conn.commit()
    cur.close(); conn.close()

with DAG(
    dag_id="ingest_dvf_full",
    start_date=days_ago(1),
    schedule=None,
    catchup=False,
    default_args={"owner": "airflow"},
) as dag:
    PythonOperator(task_id="load_dvf", python_callable=load_dvf)