import threading
import hashlib
from utils.log import log
from db.tasks import get_all_tasks
from messaging.producer import send_message
from k8s.discovery import get_total_schedulers
import os

hostname = os.environ.get("HOSTNAME", "scheduler-0")
try:
    SCHEDULER_ID = int(hostname.split('-')[-1])
except Exception:
    SCHEDULER_ID = 0  # fallback

TOTAL_SCHEDULERS = int(os.environ.get("TOTAL_SCHEDULERS", "2"))  # Via env no YAML e depois é atualizado pelo discovery

active_tasks = {} # esse dicionário é usado para armazenar as tarefas ativas, para poder gerenciar o envio periódico

def update_scheduler_count():
    global TOTAL_SCHEDULERS
    try:
        new_total = get_total_schedulers()
        if new_total != TOTAL_SCHEDULERS:
            log(f"[{hostname}] TOTAL_SCHEDULERS alterado: {TOTAL_SCHEDULERS} → {new_total}")
            TOTAL_SCHEDULERS = new_total
    except Exception as e:
        log(f"[{hostname}] Erro ao consultar schedulers ativos: {e}")
    finally:
        threading.Timer(30, update_scheduler_count).start()

def get_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)

def is_task_owned(task_id: str) -> bool:
    return (get_hash(task_id) % TOTAL_SCHEDULERS) == SCHEDULER_ID

def clear_unowned_tasks(new_tasks):
    new_ids = {t['task_id'] for t in new_tasks}
    old_ids = set(active_tasks.keys())

    to_remove = old_ids - new_ids
    for tid in to_remove:
        timer = active_tasks.pop(tid, None)
        if timer:
            timer.cancel()
            log(f"[scheduler-{SCHEDULER_ID}] Cancelada tarefa {tid} (não pertence mais a este scheduler)")

def add_new_tasks(new_tasks):
    for task in new_tasks:
        tid = task['task_id']
        if tid not in active_tasks:
            log(f"[scheduler-{SCHEDULER_ID}] Nova tarefa agendada: {tid}")
            send_task_periodic(task)


def send_task_periodic(task):
    try:
        log(f"[scheduler-{SCHEDULER_ID}] Enviando tarefa: Nome: {task['task_name']}, Tipo: {task['task_type']}, ID (uuid): {task['task_id']} (id (db)={task['id']})")
        send_message({
            'task_name': task['task_name'],
            'id': task['id'],
            'task_id': task['task_id'],
            'task_type': task['task_type'],
            'payload': task['payload'],
        }, queue='tasks')
    except Exception as e:
        log(f"[scheduler-{SCHEDULER_ID}] ERRO ao enviar tarefa: {e}")
    finally:
        interval = task['interval_seconds']
        tid = task['task_id']
        timer = threading.Timer(interval, send_task_periodic, args=(task,))
        timer.daemon = True
        timer.start()
        active_tasks[tid] = timer  # Armazena o timer ativo para essa tarefa


def start_scheduler():
    tasks = get_all_tasks()
    my_tasks = [t for t in tasks if is_task_owned(t['task_id'])]
    log(f"[scheduler-{SCHEDULER_ID}] TOTAL_SCHEDULERS atual: {TOTAL_SCHEDULERS}")
    log(f"[scheduler-{SCHEDULER_ID}] Gerenciando {len(my_tasks)} tarefas...")

    # Agenda disparo inicial imediato para cada tarefa
    for task in my_tasks:
        send_task_periodic(task)

if __name__ == "__main__":
    update_scheduler_count()
    threading.Timer(1, start_scheduler).start() 
    # Mantém o programa vivo para os timers funcionarem
    threading.Event().wait()
