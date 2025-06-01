import pika
import json
import time
from config.envs import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD
from worker.monitor.url_checker import check_url

def process_task(task):
    print(f"[worker]    ===================================================")
    print(f"[worker]    Executando tarefa: {task['task_name']}")
    print(f"[worker]    Payload: {task['payload']}")
    result = check_url(task['payload']['url'])
    print(f"[worker]    Resultado: {result}")
    print(f"[worker]    Finalizou tarefa: {task['task_name']}")

def callback(ch, method, properties, body):
    try:
        task = json.loads(body)
        process_task(task)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[worker] Erro ao processar tarefa: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_worker():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='tasks', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='tasks', on_message_callback=callback)
    
    print("[worker] Aguardando tarefas...")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
