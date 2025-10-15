from datetime import datetime
from airflow import DAG
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import DagRunState
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    dag_id='build_communes_market_2024',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={'owner': 'airflow', 'retries': 0},
):
    wait_ingest = ExternalTaskSensor(
        task_id='wait_ingest_dvf_full',
        external_dag_id='ingest_dvf_full',
        external_task_id=None,
        allowed_states=[DagRunState.SUCCESS],
        failed_states=[DagRunState.FAILED],
        mode='reschedule',
        poke_interval=30,
        timeout=3600,
    )

    build_table = PostgresOperator(
        task_id='build_table',
        postgres_conn_id='estimo_postgres',
        sql="""
        CREATE TABLE IF NOT EXISTS communes_market_2024 (
          insee_commune   TEXT PRIMARY KEY,
          nb_mutations    INTEGER,
          nb_maisons      INTEGER,
          nb_apparts      INTEGER,
          prop_maison     REAL,
          prop_appart     REAL,
          prix_moyen_eur  REAL,
          prix_m2_moyen   REAL,
          surface_moy_m2  REAL
        );
        """,
    )

    aggregate = PostgresOperator(
        task_id='aggregate',
        postgres_conn_id='estimo_postgres',
        sql="""
        INSERT INTO communes_market_2024 AS t
        SELECT
          code_commune AS insee_commune,
          COUNT(*) AS nb_mutations,
          SUM(CASE WHEN type_local='Maison' THEN 1 ELSE 0 END) AS nb_maisons,
          SUM(CASE WHEN type_local='Appartement' THEN 1 ELSE 0 END) AS nb_apparts,
          CASE WHEN COUNT(*)>0 THEN SUM(CASE WHEN type_local='Maison' THEN 1 ELSE 0 END)::float/COUNT(*) ELSE 0 END AS prop_maison,
          CASE WHEN COUNT(*)>0 THEN SUM(CASE WHEN type_local='Appartement' THEN 1 ELSE 0 END)::float/COUNT(*) ELSE 0 END AS prop_appart,
          AVG(valeur_fonciere) AS prix_moyen_eur,
          AVG(NULLIF(valeur_fonciere,0)/NULLIF(NULLIF(surface_reelle_bati,0),NULL)) AS prix_m2_moyen,
          AVG(NULLIF(surface_reelle_bati,0)) AS surface_moy_m2
        FROM dvf_full_raw
        WHERE date_mutation >= '2024-01-01' AND date_mutation < '2025-01-01'
          AND type_local IN ('Appartement','Maison')
          AND valeur_fonciere BETWEEN 15000 AND 10000000
          AND (valeur_fonciere/NULLIF(surface_reelle_bati,0)) BETWEEN 330 AND 15000
        GROUP BY code_commune
        ON CONFLICT (insee_commune) DO UPDATE SET
          nb_mutations=EXCLUDED.nb_mutations,
          nb_maisons=EXCLUDED.nb_maisons,
          nb_apparts=EXCLUDED.nb_apparts,
          prop_maison=EXCLUDED.prop_maison,
          prop_appart=EXCLUDED.prop_appart,
          prix_moyen_eur=EXCLUDED.prix_moyen_eur,
          prix_m2_moyen=EXCLUDED.prix_m2_moyen,
          surface_moy_m2=EXCLUDED.surface_moy_m2;
        """,
    )

    wait_ingest >> build_table >> aggregate
