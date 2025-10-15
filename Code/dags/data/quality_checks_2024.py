import json
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.state import DagRunState

def run_quality_checks():
    hook = PostgresHook(postgres_conn_id="estimo_postgres")
    conn = hook.get_conn()
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS qa;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS qa.check_results(
      id BIGSERIAL PRIMARY KEY,
      check_name TEXT,
      status TEXT,
      observed NUMERIC,
      threshold NUMERIC,
      details TEXT,
      ts TIMESTAMPTZ DEFAULT now()
    );
    """)
    conn.commit()

    checks = [
        {"name":"dvf_full_raw_exists","sql":"SELECT COUNT(*) FROM dvf_full_raw;","cmp":"gt","threshold":0},
        {"name":"communes_market_2024_exists","sql":"SELECT COUNT(*) FROM communes_market_2024;","cmp":"gt","threshold":0},
        {"name":"communes_market_2024_not_nulls","sql":"SELECT COUNT(*) FROM communes_market_2024 WHERE insee_commune IS NULL;","cmp":"eq","threshold":0},
        {"name":"prix_m2_range","sql":"SELECT COALESCE(SUM(CASE WHEN prix_m2_moyen BETWEEN 330 AND 20000 THEN 0 ELSE 1 END),0) FROM communes_market_2024;","cmp":"eq","threshold":0},
        {"name":"surface_moy_range","sql":"SELECT COALESCE(SUM(CASE WHEN surface_moy_m2 BETWEEN 10 AND 500 THEN 0 ELSE 1 END),0) FROM communes_market_2024;","cmp":"eq","threshold":0},
        {"name":"props_range","sql":"SELECT COALESCE(SUM(CASE WHEN prop_maison BETWEEN 0 AND 100 AND prop_appart BETWEEN 0 AND 100 THEN 0 ELSE 1 END),0) FROM communes_market_2024;","cmp":"eq","threshold":0},
    ]

    fails = []
    for c in checks:
        cur.execute(c["sql"])
        val = cur.fetchone()[0]
        ok = (val > c["threshold"]) if c["cmp"] == "gt" else (val == c["threshold"])
        cur.execute(
            "INSERT INTO qa.check_results(check_name,status,observed,threshold,details) VALUES (%s,%s,%s,%s,%s);",
            (c["name"], "PASS" if ok else "FAIL",
             float(val) if val is not None else None,
             float(c["threshold"]), json.dumps({"cmp":c["cmp"]}))
        )
        if not ok:
            fails.append((c["name"], val, c["threshold"]))
    conn.commit()
    if fails:
        raise Exception("QA failed: " + "; ".join([f"{n}: {v} vs {t}" for n,v,t in fails]))

with DAG(
    dag_id="quality_checks_2024",
    start_date=datetime(2024,1,1),
    schedule="@daily",
    catchup=False,
    default_args={"owner":"airflow","retries":0,"retry_delay":timedelta(minutes=5)}
) as dag:
    wait_ingest = ExternalTaskSensor(
        task_id="wait_ingest",
        external_dag_id="ingest_dvf_full",
        allowed_states=[DagRunState.SUCCESS],
        failed_states=[DagRunState.FAILED],
        poke_interval=30,
        timeout=60*60
    )
    wait_agg = ExternalTaskSensor(
        task_id="wait_agg",
        external_dag_id="build_communes_market_2024",
        allowed_states=[DagRunState.SUCCESS],
        failed_states=[DagRunState.FAILED],
        poke_interval=30,
        timeout=60*60
    )
    run_checks = PythonOperator(task_id="run_checks", python_callable=run_quality_checks)
    wait_ingest >> wait_agg >> run_checks