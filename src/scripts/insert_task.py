from db.tasks import insert_task
from db.tasks import get_db_id_by_task_uuid
from utils.log import log
from insert_tasks_from_json import send_to_schedulers
import sys
import json

if __name__ == "__main__":
    interval_override = None

    if len(sys.argv) > 1:
        try:
            interval_override = int(sys.argv[1])
            print(f"Substituindo todos os intervalos para {interval_override} segundos.")
        except ValueError:
            print("O argumento deve ser um número inteiro representando o intervalo em segundos.")
            sys.exit(1)
    task = {}

    task['task_name'] = "url_example"
    task['task_type'] = "url_checker"
    task['payload_json'] = json.dumps('{"url": "https://example.com", "method": "GET"}')
    if interval_override is not None:
        task['interval_seconds'] = interval_override
    else:
        task['interval_seconds'] = 90

    task_uuid = insert_task(task['task_name'], task['task_type'], task['payload_json'], task['interval_seconds'])
    try:
        db_id = get_db_id_by_task_uuid(task_uuid)
    except Exception as e:
        log(f"❌ Erro ao recuperar ID do banco para o task_uuid {task_uuid}: {str(e)}")
        db_id = None
    task['id'] = db_id
    try:
        send_to_schedulers(task)
    except Exception as e:
        log(f"❌ Erro ao enviar tarefa '{task['task_name']}' para os schedulers: {str(e)}")
    log(f"✅ Tarefa '{task['task_name']}' inserida com id {task_uuid} (ID banco: {db_id})")
