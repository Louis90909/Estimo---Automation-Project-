from datetime import datetime
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.state import DagRunState

with DAG(
    dag_id="estimo_master",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"owner": "airflow", "retries": 0},
) as dag:
    t_ingest = TriggerDagRunOperator(
        task_id="trigger_ingest_dvf_full",
        trigger_dag_id="ingest_dvf_full",
        reset_dag_run=True,
        wait_for_completion=False,
    )

    w_ingest = ExternalTaskSensor(
        task_id="wait_ingest_done",
        external_dag_id="ingest_dvf_full",
        allowed_states=[DagRunState.SUCCESS],
        failed_states=[DagRunState.FAILED],
        poke_interval=30,
        timeout=60*60,
        mode="reschedule",
    )

    t_agg = TriggerDagRunOperator(
        task_id="trigger_build_communes_market_2024",
        trigger_dag_id="build_communes_market_2024",
        reset_dag_run=True,
        wait_for_completion=False,
    )

    w_agg = ExternalTaskSensor(
        task_id="wait_agg_done",
        external_dag_id="build_communes_market_2024",
        allowed_states=[DagRunState.SUCCESS],
        failed_states=[DagRunState.FAILED],
        poke_interval=30,
        timeout=60*60,
        mode="reschedule",
    )

    t_ingest >> w_ingest >> t_agg >> w_agg