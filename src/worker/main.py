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
        log(f"[worker] [ERRO] Erro ao processar tarefa: {e}")
        raise

def callback(ch, method, properties, body):
    global executor

    try:
        task = json.loads(body)

        if executor is None:
            log("[worker] [INFO] Executor não está disponível!")
            return

        def task_wrapper():
            try:
                process_task(task)
                if ch.is_open:
                    ch.connection.add_callback_threadsafe(
                        lambda: ch.basic_ack(delivery_tag=method.delivery_tag)
                    )
            except Exception as e:
                log(f"[worker] [ERRO] Exceção durante a tarefa: {e}")
                if ch.is_open:
                    ch.connection.add_callback_threadsafe(
                        lambda: ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    )

        executor.submit(task_wrapper)

    except Exception as e:
        log(f"[worker] [ERRO] Erro ao agendar tarefa: {e}")
        if ch.is_open:
            ch.connection.add_callback_threadsafe(
                lambda: ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            )

def listen_for_tasks():
    global executor
    log("[worker] [INFO] Criando novo executor...")
    executor = ThreadPoolExecutor(max_workers=20)

    connection = start_consumer(
        callback=callback,
        queue='tasks',
        durable=True,
        auto_ack=False,
        prefetch_count=20,
        manual_ack_inside_callback=True
    )

if __name__ == "__main__":
    log("[worker] [INFO] Iniciando o worker...")
    listen_for_tasks()
