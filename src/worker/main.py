import json
from messaging.consumer import start_consumer
from worker.monitor.url_checker import check_url
from utils.log import log

def process_task(task):
    log("[worker]    ========================================================================")
    log(f"[worker]    Executando tarefa: {task['task_name']}")
    log(f"[worker]    Payload: {task['payload']}")
    result = check_url(task['payload']['url'])
    log(f"[worker]    Resultado: {result}")
    log(f"[worker]    Finalizou tarefa: {task['task_name']}")

def callback(ch, method, properties, body):
    try:
        task = json.loads(body)
        process_task(task)
    except Exception as e:
        log(f"[worker] Erro ao processar tarefa: {e}")

if __name__ == "__main__":
    start_consumer(callback, queue='tasks')