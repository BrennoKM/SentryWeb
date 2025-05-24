import pika
import json

def send_message(data, queue='tasks', delay=None):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    args = {}
    exchange = ''

    if delay is not None:
        exchange = 'delayed_exchange'
        channel.exchange_declare(
            exchange=exchange,
            exchange_type='x-delayed-message',
            arguments={'x-delayed-type': 'direct'}
        )
        args['x-delay'] = delay * 1000  # milissegundos

        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(exchange=exchange, queue=queue, routing_key=queue)
    else:
        # Sem delay: só declara a fila, sem bind na default exchange
        channel.queue_declare(queue=queue, durable=True)

    channel.basic_publish(
        exchange=exchange,
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # mensagem persistente
            headers=args
        )
    )
    connection.close()
