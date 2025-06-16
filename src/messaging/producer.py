import pika
import json
import time
import threading
from utils.log import log
from config.envs import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD

# Variáveis globais (uma conexão por pod)
_connection = None
_channel = None
_lock = threading.Lock()

def init_connection(hostname="producer"):
    global _connection, _channel
    try:
        _connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
                heartbeat=60,
                blocked_connection_timeout=30
            )
        )
        _channel = _connection.channel()
        log(f"[{hostname}] Conexão com RabbitMQ estabelecida")
    except Exception as e:
        log(f"[{hostname}] [ERRO] Falha ao conectar com RabbitMQ: {e}")
        _connection = None
        _channel = None

def _ensure_connection(hostname="producer"):
    global _connection, _channel
    with _lock:
        if _connection is None or _channel is None or _connection.is_closed or _channel.is_closed:
            log(f"[{hostname}] Reconectando com RabbitMQ...")
            init_connection(hostname=hostname)

def send_message(data, queue=None, exchange='', routing_key=None, durable=True, max_retries=3, hostname="producer"):
    global _connection, _channel
    if not queue and not exchange:
        raise AssertionError("Deve informar 'queue' ou 'exchange'")

    if exchange and routing_key is None:
        routing_key = ''

    if not queue and (exchange is None or routing_key is None):
        raise AssertionError("Deve informar 'queue' ou ('exchange' e 'routing_key')")

    delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            _ensure_connection(hostname=hostname)
            if _channel is None:
                raise Exception("Canal RabbitMQ ainda é None após tentativa de conexão")

            with _lock:
                if queue:
                    _channel.queue_declare(queue=queue, durable=durable)
                    rk = queue
                else:
                    rk = routing_key

                _channel.basic_publish(
                    exchange=exchange,
                    routing_key=rk,
                    body=json.dumps(data),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
            return
        except Exception as e:
            log(f"[{hostname}] [ERRO] Erro ao enviar mensagem (tentativa {attempt}): {e}, dados: {data}")
            with _lock:
                _connection = None
                _channel = None
            if attempt == max_retries:
                raise
            time.sleep(delay)
            delay *= 2
