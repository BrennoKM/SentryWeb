import json
import threading
from messaging.consumer import start_consumer
from worker.monitor.url_checker import check_url
from utils.log import log


def process_task(task):
    result = check_url(task['payload']['url'])
    # log("[worker]    ========================================================================")
    # log("[worker]    Executando tarefa")
    # log(f"[worker]    Nome: {task['task_name']}")
    # log(f"[worker]    Tipo: {task['task_type']}")
    # log(f"[worker]    ID (uuid): {task['task_uuid']}")
    # log(f"[worker]    ID (db): {task['id']}")
    # log(f"[worker]    Payload: {task['payload']}")
    # log(f"[worker]    Resultado: {result}")
    # log(f"[worker]    Finalizou tarefa: {task['task_name']}")
    log(
        "[worker]    ==================================== Tarefa Recebida ====================================\n"
        f"\tNome: {task['task_name']}\n"
        f"\tTipo: {task['task_type']}\n"
        f"\tID (uuid): {task['task_uuid']}\n"
        f"\tID (db): {task['id']}\n"
        f"\tPayload: {task['payload']}\n"
        f"\tResultado: {result}\n"
        "\tFinalizou tarefa.\n"
    )

def callback(ch, method, properties, body):
    try:
        task = json.loads(body)
        process_task(task)
    except Exception as e:
        log(f"[worker] Erro ao processar tarefa: {e}")

def listen_for_tasks():
    try:
        start_consumer(
            callback=callback, 
            queue='tasks', 
            durable=True
        )
    except Exception as e:
        log(f"[worker] ERRO ao conectar RabbitMQ: {e}")
        log("[worker] Tentando reconectar em 5 segundos...")
        threading.Timer(5, listen_for_tasks).start()

if __name__ == "__main__":
    log("[worker] Iniciando o worker...")
    listen_for_tasks()