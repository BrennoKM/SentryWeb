import pika
import json
import time
from utils.log import log
from config.envs import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD

def send_message(data, queue=None, exchange='', routing_key=None, durable=True, max_retries=5, hostname="producer"):
    # Aceitar routing_key vazio '' como válido para exchange do tipo fanout
    if not queue and not exchange:
        raise AssertionError("Deve informar 'queue' ou 'exchange'")

    # Para fanout, routing_key pode ser None ou '' -> normalize para string vazia
    if exchange and routing_key is None:
        routing_key = ''

    if not queue and (exchange is None or routing_key is None):
        raise AssertionError("Deve informar 'queue' ou ('exchange' e 'routing_key')")

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

            if queue:
                channel.queue_declare(queue=queue, durable=durable)
                rk = queue
            else:
                rk = routing_key

            channel.basic_publish(
                exchange=exchange,
                routing_key=rk,
                body=json.dumps(data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
            return
        except Exception as e:
            log(f"[{hostname}] [ERRO] Erro ao enviar mensagem, (tentativa {attempt}): {e}, dados: {data}")
            if attempt == max_retries:
                raise
            time.sleep(delay)
            delay *= 2 