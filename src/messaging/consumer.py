import pika
import json
from config.envs import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD
from utils.log import log

def start_consumer(callback, queue=None, exchange='', exchange_type='direct', routing_key='', exclusive=False, durable=True, prefetch_count=1):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        )
    )
    channel = connection.channel()

    if exchange:
        channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=durable)
        result = channel.queue_declare(queue='', exclusive=exclusive) if exclusive else channel.queue_declare(queue=queue, durable=durable)
        queue_name = result.method.queue
        channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)
    else:
        assert queue, "Se não usar exchange, é obrigatório informar a 'queue'"
        channel.queue_declare(queue=queue, durable=durable)
        queue_name = queue

    def on_message(ch, method, properties, body):
        try:
            callback(ch, method, properties, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            log(f"[consumer] Erro ao processar mensagem: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message)
    log(f"[*] Aguardando mensagens na fila '{queue_name}'...")
    channel.start_consuming()