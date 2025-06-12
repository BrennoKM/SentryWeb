import json
from concurrent.futures import ThreadPoolExecutor
from messaging.consumer import start_consumer
from worker.monitor.url_checker import check_url
from utils.log import log

executor = None

def process_task(task):
    try:
        result = check_url(task['payload']['url'])
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
    except Exception as e:
        log(f"[worker] Erro ao processar tarefa: {e}")

def callback(ch, method, properties, body):
    global executor
    try:
        task = json.loads(body)

        if executor is None:
            log("[worker] Executor não está disponível!")
            return

        executor.submit(process_task, task)

    except Exception as e:
        log(f"[worker] Erro ao agendar tarefa: {e}")

def listen_for_tasks():
    global executor
    log("[worker] Criando novo executor...")
    executor = ThreadPoolExecutor(max_workers=1)

    start_consumer(
        callback=callback,
        queue='tasks',
        durable=True,
        auto_ack=True,
        prefetch_count=1
    )

if __name__ == "__main__":
    log("[worker] Iniciando o worker...")
    listen_for_tasks()
