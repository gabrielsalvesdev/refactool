from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging
import requests

# Callback para notificação no Slack em caso de falha

def notify_slack(context):
    message = f"Falha na DAG '{context.get('task_instance').task_id}': {str(context.get('exception'))}"
    webhook_url = 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'  # Atualize com sua URL do Slack
    try:
        requests.post(webhook_url, json={"text": message})
    except Exception as e:
        logging.error(f"Erro ao enviar notificação para Slack: {e}")

# Argumentos padrão da DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=60),
    'on_failure_callback': notify_slack
}

dag = DAG(
    'lru_retraining',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

# Adicionar após os imports

class ModelTrainingTimeout(Exception):
    """Exceção para timeout no treinamento de modelos"""
    pass

def fetch_data(**kwargs):
    logging.info("Iniciando a extração de dados.")
    # Lógica para extração de dados
    return {"data": "dados extraídos"}


def train_model(**kwargs):
    logging.info("Treinando o modelo preditivo.")
    # Simulação de treinamento com possível erro condicional
    import random
    if random.randint(0, 1):
        raise Exception("Erro durante o treinamento do modelo")
    return {"model": "modelo treinado"}


def validate_model(**kwargs):
    logging.info("Validando o modelo treinado.")
    # Lógica para validação do modelo
    return {"valid": True}


def deploy_model(**kwargs):
    logging.info("Implantando o modelo.")
    # Lógica para implantação do modelo
    return {"status": "deploy realizado"}

# Adicionar nova função build_ranking_model após deploy_model

def build_ranking_model(data):
    from time import sleep
    try:
        # Simulação de treinamento demorado
        sleep(120 * 60)  # 120 minutos (deve falhar pelo timeout)
        return {"accuracy": 0.8}
    except TimeoutError:
        raise ModelTrainingTimeout("Treinamento excedeu o tempo limite")

fetch_data_task = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    dag=dag,
    execution_timeout=timedelta(minutes=20),
    retries=1,
    retry_delay=timedelta(minutes=2)
)

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
    execution_timeout=timedelta(minutes=60),
    retries=3,
    retry_delay=timedelta(minutes=5),
    retry_on_exception=lambda e: isinstance(e, ModelTrainingTimeout)
)

validate_model_task = PythonOperator(
    task_id='validate_model',
    python_callable=validate_model,
    dag=dag,
    execution_timeout=timedelta(minutes=15),
    retries=1,
    retry_delay=timedelta(minutes=2)
)

deploy_model_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag,
    execution_timeout=timedelta(minutes=10),
    retries=1,
    retry_delay=timedelta(minutes=2)
)

fetch_data_task >> train_model_task >> validate_model_task >> deploy_model_task 