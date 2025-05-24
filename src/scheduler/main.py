import json
import threading
import hashlib
from datetime import datetime, timezone
from db.tasks import get_all_tasks
from messaging.producer import send_message

SCHEDULER_ID = 1
TOTAL_SCHEDULERS = 2

def get_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)

def is_task_owned(task_id: str) -> bool:
    return (get_hash(task_id) % TOTAL_SCHEDULERS) == SCHEDULER_ID

def send_task_periodic(task):
    print(f"[scheduler {SCHEDULER_ID}] Enviando tarefa: {task['task_type']} (task_id={task['task_name']})")
    send_message({
        'task_name': task['task_name'],
        'task_id': task['task_id'],
        'type': task['task_type'],
        'payload': task['payload'],
    }, queue='tasks')

    # Agenda o próximo disparo
    interval = task['interval_seconds']
    timer = threading.Timer(interval, send_task_periodic, args=(task,))
    timer.daemon = True
    timer.start()

def start_scheduler():
    tasks = get_all_tasks()
    my_tasks = [t for t in tasks if is_task_owned(t['task_id'])]

    print(f"[scheduler {SCHEDULER_ID}] Gerenciando {len(my_tasks)} tarefas...")

    # Agenda disparo inicial imediato para cada tarefa
    for task in my_tasks:
        send_task_periodic(task)

if __name__ == "__main__":
    start_scheduler()
    # Mantém o programa vivo para os timers funcionarem
    threading.Event().wait()
