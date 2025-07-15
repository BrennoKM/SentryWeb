import sys
import json
from db.tasks import insert_task, get_db_id_by_task_uuid
from utils.log import log
from messaging.producer import send_message

def send_notification_to_schedulers(task):
    message = {
        'task_name': task['task_name'],
        'task_type': task['task_type'],
        'payload': task['payload'],
        'interval_seconds': task['interval_seconds'],
        'task_uuid': task['task_uuid'],
        'id': task['id']
    }
    try:
        send_message(message, exchange='new_task_exchange', routing_key='')
        log(f"✅ Notificação para a tarefa '{task['task_name']}' enviada aos schedulers.")
    except Exception as e:
        log(f"❌ Erro ao enviar notificação para os schedulers: {str(e)}")
        raise

if __name__ == "__main__":
    interval_override = None

    if len(sys.argv) > 1:
        try:
            interval_override = int(sys.argv[1])
            print(f"Substituindo todos os intervalos para {interval_override} segundos.")
        except ValueError:
            print("O argumento deve ser um número inteiro representando o intervalo em segundos.")
            sys.exit(1)

    task = {
        'task_name': "url_example_single",
        'task_type': "url_checker",
        'payload': {"url": "https://example.com"},
    }
    task['interval_seconds'] = interval_override if interval_override is not None else 90

    try:
        task_uuid = insert_task(
            task['task_name'],
            task['task_type'],
            json.dumps(task['payload']),
            task['interval_seconds']
        )
        task['task_uuid'] = task_uuid

        db_id = get_db_id_by_task_uuid(task_uuid)
        task['id'] = db_id
        send_notification_to_schedulers(task)

        log(f"✅ Tarefa '{task['task_name']}' inserida e notificada com sucesso. UUID: {task_uuid}")

    except Exception as e:
        log(f"❌ Erro fatal no processo de inserção da tarefa: {str(e)}")
