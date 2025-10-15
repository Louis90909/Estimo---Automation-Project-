from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
import os

CSV_PATH = "/opt/airflow/dags/communesdvf2024.csv"

def init_tables():
    hook = PostgresHook(postgres_conn_id="estimo_db")
    with hook.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        CREATE SCHEMA IF NOT EXISTS ref;
        CREATE TABLE IF NOT EXISTS ref.communes_market_yearly (
          insee_commune   TEXT NOT NULL,
          annee           INTEGER NOT NULL,
          nb_mutations    INTEGER,
          nb_maisons      INTEGER,
          nb_apparts      INTEGER,
          prop_maison     DOUBLE PRECISION,
          prop_appart     DOUBLE PRECISION,
          prix_moyen_eur  DOUBLE PRECISION,
          prix_m2_moyen   DOUBLE PRECISION,
          surface_moy_m2  DOUBLE PRECISION,
          PRIMARY KEY (insee_commune, annee)
        );
        DROP TABLE IF EXISTS ref._communes_2024_rawtxt;
        CREATE TABLE ref._communes_2024_rawtxt(
          INSEE_COM    TEXT,
          annee        TEXT,
          nb_mutations TEXT,
          NbMaisons    TEXT,
          NbApparts    TEXT,
          PropMaison   TEXT,
          PropAppart   TEXT,
          PrixMoyen    TEXT,
          Prixm2Moyen  TEXT,
          SurfaceMoy   TEXT
        );
        """)
        conn.commit()

def load_csv():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(CSV_PATH)
    hook = PostgresHook(postgres_conn_id="estimo_db")
    sql_copy = rf"""
    \\copy ref._communes_2024_rawtxt
    FROM '{CSV_PATH}'
    WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8', NULL 'NA')
    """
    hook.run(sql_copy)

def upsert_final():
    hook = PostgresHook(postgres_conn_id="estimo_db")
    with hook.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
        INSERT INTO ref.communes_market_yearly(
          insee_commune, annee, nb_mutations, nb_maisons, nb_apparts,
          prop_maison, prop_appart, prix_moyen_eur, prix_m2_moyen, surface_moy_m2
        )
        SELECT
          TRIM(INSEE_COM),
          CAST(NULLIF(annee,'') AS INTEGER),
          CAST(NULLIF(nb_mutations,'') AS INTEGER),
          CAST(NULLIF(NbMaisons,'') AS INTEGER),
          CAST(NULLIF(NbApparts,'') AS INTEGER),
          CAST(REPLACE(NULLIF(PropMaison,''),  ',', '.') AS DOUBLE PRECISION),
          CAST(REPLACE(NULLIF(PropAppart,''), ',', '.') AS DOUBLE PRECISION),
          CAST(REPLACE(NULLIF(PrixMoyen,''),  ',', '.') AS DOUBLE PRECISION),
          CAST(REPLACE(NULLIF(Prixm2Moyen,''), ',', '.') AS DOUBLE PRECISION),
          CAST(REPLACE(NULLIF(SurfaceMoy,''),  ',', '.') AS DOUBLE PRECISION)
        FROM ref._communes_2024_rawtxt
        WHERE
          INSEE_COM IS NOT NULL AND TRIM(INSEE_COM) <> '' AND UPPER(TRIM(INSEE_COM)) <> 'NA'
          AND annee IS NOT NULL AND TRIM(annee) <> ''
        ON CONFLICT (insee_commune, annee) DO UPDATE
        SET nb_mutations    = EXCLUDED.nb_mutations,
            nb_maisons      = EXCLUDED.nb_maisons,
            nb_apparts      = EXCLUDED.nb_apparts,
            prop_maison     = EXCLUDED.prop_maison,
            prop_appart     = EXCLUDED.prop_appart,
            prix_moyen_eur  = EXCLUDED.prix_moyen_eur,
            prix_m2_moyen   = EXCLUDED.prix_m2_moyen,
            surface_moy_m2  = EXCLUDED.surface_moy_m2;
        """)
        conn.commit()

with DAG(
    dag_id="import_communes_dvf_2024",
    start_date=datetime(2024,1,1),
    schedule_interval=None,   # on déclenche à la main
    catchup=False,
    default_args={"owner": "estimo", "retries": 0},
    description="Charge le CSV communes DVF 2024 dans Postgres",
) as dag:
    start = EmptyOperator(task_id="start")
    init = PythonOperator(task_id="init_tables", python_callable=init_tables)
    load = PythonOperator(task_id="load_csv", python_callable=load_csv)
    upsert = PythonOperator(task_id="upsert_final", python_callable=upsert_final)
    end = EmptyOperator(task_id="end")

    start >> init >> load >> upsert >> end
