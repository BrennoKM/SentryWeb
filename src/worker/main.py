import json
from messaging.consumer import start_consumer
from worker.monitor.url_checker import check_url
from utils.log import log

def process_task(task):
    result = check_url(task['payload']['url'])
    # log("[worker]    ========================================================================")
    # log("[worker]    Executando tarefa")
    # log(f"[worker]    Nome: {task['task_name']}")
    # log(f"[worker]    Tipo: {task['task_type']}")
    # log(f"[worker]    ID (uuid): {task['task_id']}")
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
        "\tFinalizou tarefa: {task['task_name']}\n"
    )

def callback(ch, method, properties, body):
    try:
        task = json.loads(body)
        process_task(task)
    except Exception as e:
        log(f"[worker] Erro ao processar tarefa: {e}")

if __name__ == "__main__":
    start_consumer(callback, queue='tasks')