from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

with DAG(
    dag_id="estimation_input_daily",
    start_date=datetime(2024,1,1),
    schedule=None,
    catchup=False,
    default_args={"owner":"airflow","retries":0},
) as dag:
    seed_estimation_input = PostgresOperator(
        task_id="seed_estimation_input",
        postgres_conn_id="estimo_postgres",
        sql="""
WITH base AS (
  SELECT
    gs AS i,
    (ARRAY['APT','HSE'])[1 + (random()*1)::int] AS property_type_code,
    (ARRAY['75111','75011','33063','69123','34172'])[1 + (random()*4)::int] AS insee_commune,
    (ARRAY['75011','75011','33000','69003','34000'])[1 + (random()*4)::int] AS postal_code,
    (10 + round(random()*140,1))::numeric AS surface_habitable,
    1 + (random()*5)::int AS rooms,
    1900 + (random()*120)::int AS year_built,
    (ARRAY['A','B','C','D','E','F','G'])[1 + (random()*6)::int] AS energy_label_code,
    (20000 + (random()*800000))::int AS listing_price_eur
  FROM generate_series(1,500) gs
),
buckets AS (
  SELECT *,
    CASE
      WHEN surface_habitable < 30 THEN '0-30'
      WHEN surface_habitable < 50 THEN '30-50'
      WHEN surface_habitable < 70 THEN '50-70'
      WHEN surface_habitable < 100 THEN '70-100'
      WHEN surface_habitable < 150 THEN '100-150'
      ELSE '150+'
    END AS surface_bucket,
    CASE
      WHEN rooms <= 1 THEN '1'
      WHEN rooms = 2 THEN '2'
      WHEN rooms = 3 THEN '3'
      WHEN rooms = 4 THEN '4'
      ELSE '5+'
    END AS rooms_bucket,
    CASE
      WHEN year_built < 1948 THEN '<1948'
      WHEN year_built <= 1974 THEN '1949-1974'
      WHEN year_built <= 2000 THEN '1975-2000'
      ELSE '2001+'
    END AS built_period,
    CASE
      WHEN energy_label_code IN ('A','B') THEN 'A-B'
      WHEN energy_label_code IN ('C','D') THEN 'C-D'
      ELSE 'E-G'
    END AS energy_bucket
  FROM base
)
INSERT INTO estimation_input(
  postal_code,insee_commune,zone_key,
  property_type_code,surface_habitable,rooms,year_built,energy_label_code,
  listing_price_eur,surface_bucket,rooms_bucket,built_period,energy_bucket
)
SELECT
  postal_code,insee_commune,insee_commune,
  property_type_code,surface_habitable,rooms,year_built,energy_label_code,
  listing_price_eur,surface_bucket,rooms_bucket,built_period,energy_bucket
FROM buckets;
"""
    )

    run_quality_checks = PostgresOperator(
        task_id="run_quality_checks",
        postgres_conn_id="estimo_postgres",
        sql="""
CREATE SCHEMA IF NOT EXISTS qa;
CREATE TABLE IF NOT EXISTS qa.check_results(
  id BIGSERIAL PRIMARY KEY,
  check_name TEXT NOT NULL,
  status TEXT NOT NULL,
  observed NUMERIC,
  threshold NUMERIC,
  details JSONB,
  ts TIMESTAMPTZ DEFAULT now()
);

INSERT INTO qa.check_results(check_name,status,observed,threshold,details)
SELECT 'dvf_full_raw_exists', CASE WHEN COUNT(*)>0 THEN 'PASS' ELSE 'FAIL' END, COUNT(*), 0, NULL FROM dvf_full_raw;

INSERT INTO qa.check_results(check_name,status,observed,threshold,details)
SELECT 'communes_market_2024_exists', CASE WHEN COUNT(*)>0 THEN 'PASS' ELSE 'FAIL' END, COUNT(*), 0, NULL FROM communes_market_2024;

INSERT INTO qa.check_results(check_name,status,observed,threshold,details)
SELECT 'prix_m2_range',
       CASE WHEN COUNT(*)=0 THEN 'PASS' ELSE 'FAIL' END,
       COUNT(*), 0, NULL
FROM dvf_full_raw
WHERE date_mutation >= '2024-01-01' AND date_mutation < '2025-01-01'
AND (valeur_fonciere/NULLIF(surface_reelle_bati,0)) NOT BETWEEN 330 AND 15000;
"""
    )

    mark_grafana_refresh = PostgresOperator(
        task_id="mark_grafana_refresh",
        postgres_conn_id="estimo_postgres",
        sql="""
CREATE TABLE IF NOT EXISTS grafana_refresh(
  id INT PRIMARY KEY DEFAULT 1,
  last_refreshed TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'ok'
);
INSERT INTO grafana_refresh(id) VALUES(1) ON CONFLICT (id) DO NOTHING;
UPDATE grafana_refresh SET last_refreshed=now(), status='ok' WHERE id=1;
"""
    )

    seed_estimation_input >> run_quality_checks >> mark_grafana_refresh