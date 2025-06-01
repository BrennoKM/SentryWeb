import pika
import json
from config.envs import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD

def start_consumer(callback, queue='tasks'):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    def on_message(ch, method, properties, body):
        data = json.loads(body)
        callback(ch, method, properties, body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=on_message)
    print(f"[*] Aguardando mensagens na fila '{queue}'. Ctrl+C para sair.")
    channel.start_consuming()