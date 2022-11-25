import io
import json
import requests
import pendulum
import requests
import pandas as pd

from airflow.models import DAG, Variable, XCom
from airflow.operators.python import PythonOperator
from airflow.operators.docker_operator import DockerOperator

with DAG(
    'dag_secomp22',
    default_args={'retries': 2},
    description='Data Pipeline secomp22',
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=['example'],
) as dag:

  

  def extract(**kwargs):
    ti = kwargs['ti']
    url="https://raw.githubusercontent.com/cs109/2014_data/master/countries.csv"
    
    content=requests.get(url).content
    dataframe=pd.read_csv(io.StringIO(content.decode('utf-8')))
    ti.xcom_push('dataset', dataframe.to_json(orient='records'))
  
  
  def transform(**kwargs):
    ti = kwargs['ti']
    
    dataset = ti.xcom_pull(task_ids='extract', key='dataset')
    df = pd.DataFrame(json.loads(dataset))
    group_df = df.groupby('Region', as_index=False).agg({'Country': 'count'})
    Variable.set("dataset", group_df.to_json(orient='records'))

  extract_task = PythonOperator(
        task_id='extract',
        python_callable=extract,
    )

  transform_task = PythonOperator(
        task_id='transform',
        python_callable=transform,
    )

  load_task = DockerOperator(
        task_id="docker",
        image="alpine",
        container_name="alpine_airflow",
        api_version="auto",
        auto_remove=True,
        command=["printenv"],
        environment={
            "XCOM" : Variable.get("dataset" , "None"),
        },
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

  extract_task >> transform_task >> load_task