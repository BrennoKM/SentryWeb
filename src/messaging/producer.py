import pika
import json
import time
from utils.log import log
from config.envs import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD

def send_message(data, queue='tasks', max_retries=5):
    delay = 2  # segundos
    for attempt in range(1, max_retries + 1):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
            return
        except Exception as e:
            log(f"[producer] Erro ao enviar mensagem, dados: {data} (tentativa {attempt}): {e}")
            if attempt == max_retries:
                raise
            time.sleep(delay)
            delay *= 2  