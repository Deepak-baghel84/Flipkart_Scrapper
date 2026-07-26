from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from ETL import run_etl


default_args = {
    "owner": "Deepak",
    "retries": 1
}


with DAG(
    dag_id="flipkart_etl_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,          # Run manually for now
    catchup=False,
    tags=["etl", "flipkart"],
) as dag:

    scrape_task = PythonOperator(
        task_id="scrape_flipkart",
        python_callable=run_etl
    )


    scrape_task