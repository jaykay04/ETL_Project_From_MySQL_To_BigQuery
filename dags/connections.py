from airflow import settings
from airflow.models import Connection
import json
import os

#Read configuration from config.json file
path = '/Users/Jaykay/Downloads/Code Challenge/config.json
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