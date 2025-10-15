from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    "check_quality",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
):
    check = PostgresOperator(
        task_id="check_counts",
        postgres_conn_id="estimo_postgres",
        sql="""
        SELECT
          annee,
          COUNT(*) AS communes,
          ROUND(AVG(prix_m2_moyen), 0) AS prix_m2_moyen_moyen,
          ROUND(MAX(prix_m2_moyen), 0) AS prix_m2_max,
          ROUND(MIN(prix_m2_moyen), 0) AS prix_m2_min
        FROM ref.communes_market_yearly
        GROUP BY annee
        ORDER BY annee DESC;
        """,
    )