from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.sensors.filesystem import FileSensor
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.smtp.notifications.smtp import send_smtp_notification


default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="first_task",
    default_args=default_args,
    start_date=datetime(2026, 10, 1),
    schedule="* */4 * * *",
    catchup=False,
    on_failure_callback=send_smtp_notification(
        to="muradneciyev9@gmail.com",
        subject="Airflow Task Failed",
        html_content="<h3>Airflow error!</h3>",
        smtp_conn_id="email_conn_id",
    ),
) as dag:

    checksensor = FileSensor(
        task_id="wait_for_file_async",
        filepath="/opt/airflow/files/orders.csv",
        poke_interval=2,
        timeout=10,
        mode="reschedule",
    )

    execute_query = SQLExecuteQueryOperator(
    task_id="execute_query",
    conn_id="pg_conn_id",
    sql="""
        DROP TABLE IF EXISTS orders;

        CREATE TABLE orders (
    order_id VARCHAR(10),
    full_name VARCHAR(100),
    city VARCHAR(50),
    registration_date DATE,
    membership_level VARCHAR(20)
);

COPY orders
FROM '/opt/airflow/files/orders.csv'
WITH (
    FORMAT csv,
    HEADER true,
    DELIMITER E'\t'
);"""
)

    checksensor >> execute_query
