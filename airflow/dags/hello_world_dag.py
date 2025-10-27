"""
Hello World DAG for Week 1 testing.

This is a simple DAG to verify Airflow is working correctly.
"""

from datetime import datetime, timedelta

import psycopg2
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator


def hello_world():
    """Simple hello world function."""
    print("Hello from Airflow! Week 1 is working.")
    return "success"


def check_services():
    """Check if other services are accessible."""
    try:
        # Check API health
        response = requests.get("http://rag-api:8000/api/v1/health", timeout=5)
        print(f"API Health: {response.status_code}")

        # Check database connection
        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            database="rag_db",
            user="rag_user",
            password="rag_password"
        )
        print("Database: Connected successfully")
        conn.close()

        return "Services are accessible"
    except Exception as e:
        print(f"Service check failed: {e}")
        raise


# DAG configuration
default_args = {
    'owner': 'rag',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'hello_world_week1',
    default_args=default_args,
    description='Hello World DAG for Week 1',
    schedule=None,  # Manual trigger only (schedule parameter introduced in Airflow 2.4+)
    catchup=False,
    tags=['week1', 'testing'],
)

# Define tasks
hello_task = PythonOperator(
    task_id='hello_world',
    python_callable=hello_world,
    dag=dag,
)

service_check_task = PythonOperator(
    task_id='check_services',
    python_callable=check_services,
    dag=dag,
)

# Set task dependencies
hello_task >> service_check_task