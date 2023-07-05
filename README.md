# ETL Project From MySQL To BigQuery

## Introduction
This project basically demonstrates how we can Extract, Transform and Load data from MySQL databases to Google Bigquery Datawarehouse.  
In this project, data is going to be extracted, transformed and loaded using the full load technique as well as the incremental load approach while all of this will be orchestrated using Apache Airflow.   
Finally, a CI/CD pipeline will be created to deliver and deploy new code changes to the airflow environment as new releases.

## Tools and Environment
1. Visual Studio Code
2. Apache Airflow
3. MySQL
4. Google BigQuery
5. Git and Github

## Environmental SetUp
To set up the necessary connections in Apache Airflow for MySQL and BigQuery, i defined the connections via the Airflow web UI and created the connection below:

##### MySQL and BigQuery Connection:
```
from airflow import settings
from airflow.models import Connection
import json
import os

#Read configuration from config.json file
path = '/Users/Jaykay/Downloads/config.json
with open(path, 'r') as config_file;
  config = json.loads(config_file)

#Retrieve MySQL connection from environment variables
username = os.environ.get(config['user'])
password = os.environ.get(config['password'])

# Create MySQL connection
mysql_conn = Connection(
    conn_id='mysql_conn',
    conn_type='mysql',
    host=config['host'],
    port=config['port'],
    schema='Employee',
    login=username,
    password=password
)

# Add MySQL connection to Airflow
session = settings.Session()
session.add(mysql_conn)
session.commit()
session.close()

# Create BigQuery connection
bigquery_conn = Connection(
    conn_id='bigquery_conn',
    conn_type='bigquery',
    project_id='my_project_id',
    keyfile_path='/Users/Jaykay/Downloads/keyfile.json'
)

# Add BigQuery connection to Airflow
session = settings.Session()
session.add(bigquery_conn)
session.commit()
session.close()
```

## Create DAG for full and Incremental Load
The Next step is to Write the DAGs for the full load and incremental load. I Defined the scheduling requirements, dependencies, and operators/tasks for each DAG and used  the MySQL and BigQuery operators in Airflow to interact with the databases.
```
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'Joshua',
    'depends_on_past': False,
    'start_date': datetime(2023, 7, 5),
    'email': ['jk.gbegudu@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Full Load DAG
full_load_dag = DAG(
    'full_load_dag',
    default_args=default_args,
    schedule_interval='0 0 * * *',  # This Runs once daily at midnight
    catchup = False
)

# Incremental Load DAG
incremental_load_dag = DAG(
    'incremental_load_dag',
    default_args=default_args,
    schedule_interval='0 0 * * *',  # This Runs once daily at midnight
    catcthup = False
)

# MySQL to BigQuery Operators and Tasks

# Task to extract data from MySQL
mysql_to_bigquery_task = MySqlOperator(
    task_id='mysql_to_bigquery_task',
    mysql_conn_id='mysql_conn',
    sql='SELECT * FROM employees', 
    dag=full_load_dag  
)

# Task to transform data (e.g., gender column) before loading into BigQuery
transform = '''WITH transformed_employees AS (
  SELECT
    id,
    name,
    CASE
      WHEN gender = 'M' THEN 'Male'
      WHEN gender = 'F' THEN 'Female'
      ELSE gender
    END AS gender_transformed,
    age,
    email
  FROM {{ ref('employees') }}
)'''
transform_task = MySqlOperator(
    task_id='transform_task',
    sql = transform
    dag=full_load_dag
)

# Task to load data into BigQuery
load_to_bigquery_task1 = BigQueryOperator(
    task_id='load_to_bigquery_task',
    sql='INSERT INTO mydb.employees_table SELECT * FROM Employees', 
    destination_dataset_table='mydb.employees_table', 
    write_disposition='WRITE_TRUNCATE',  # Replace with the desired write disposition
    bigquery_conn_id='bigquery_conn',
    dag=full_load_dag
)

# For Incremental Load
# Task to load data into BigQuery
load_to_bigquery_task2 = BigQueryOperator(
    task_id='load_to_bigquery_task',
    sql='INSERT INTO mydb.employees_table SELECT * FROM Employees', 
    destination_dataset_table='mydb.employees_table', 
    write_disposition='APPEND',  # Replace with the desired write disposition
    bigquery_conn_id='bigquery_conn',
    dag=incremental_load_dag 

# Define the task dependencies for the Full Load DAG
mysql_to_bigquery_task >> transform_task >> load_to_bigquery_task1

# Define the task dependencies for the Incremental Load DAG
mysql_to_bigquery_task >> transform_task >> load_to_bigquery_task2
```

Finnally, I Commit and push the code changes to the GitHub repository. 
