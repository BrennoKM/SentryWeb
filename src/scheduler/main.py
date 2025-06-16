import threading
import hashlib
from utils.log import log
from db.tasks import get_all_tasks
from messaging.producer import send_message
from k8s.discovery import get_total_schedulers
from messaging.consumer import start_consumer
import os
import time

hostname = os.environ.get("HOSTNAME", "scheduler-0")
try:
    SCHEDULER_ID = int(hostname.split('-')[-1])
except Exception:
    SCHEDULER_ID = 0  # fallback

TOTAL_SCHEDULERS = int(os.environ.get("TOTAL_SCHEDULERS", "2"))  # Via env no YAML e depois é atualizado pelo discovery

active_tasks = {} # esse dicionário é usado para armazenar as tarefas ativas, para poder gerenciar o envio periódico


def sync_tasks():
    tasks = get_all_tasks()
    my_tasks = [t for t in tasks if is_task_owned(t['task_uuid'])]

    clear_unowned_tasks(my_tasks)
    add_new_tasks(my_tasks)

    log(f"[scheduler-{SCHEDULER_ID}] [INFO] Agora gerenciando {len(my_tasks)} tarefas")

def clear_unowned_tasks(new_tasks):
    new_ids = {t['task_uuid'] for t in new_tasks}
    old_ids = set(active_tasks.keys())

    to_remove = old_ids - new_ids
    for tid in to_remove:
        timer = active_tasks.pop(tid, None)
        if timer:
            timer.cancel()
            log(f"[scheduler-{SCHEDULER_ID}] [INFO] Cancelada tarefa {tid} (não pertence mais a este scheduler)")

def add_new_tasks(new_tasks):
    for task in new_tasks:
        tid = task['task_uuid']
        old_timer = active_tasks.get(tid)
        if old_timer:
            old_timer.cancel()
        log(f"[scheduler-{SCHEDULER_ID}] [INFO] Reagendando tarefa: {tid}")
        send_task_periodic(task)
            
def update_scheduler_count():
    global TOTAL_SCHEDULERS
    while True:
        try:
            new_total = get_total_schedulers()
            if new_total != TOTAL_SCHEDULERS:
                log(f"[scheduler-{SCHEDULER_ID}] [INFO] TOTAL_SCHEDULERS alterado: {TOTAL_SCHEDULERS} → {new_total}")
                TOTAL_SCHEDULERS = new_total
                sync_tasks()
        except Exception as e:
            log(f"[{hostname}] [ERRO] Erro ao consultar schedulers ativos: {e}")
        time.sleep(30)

def get_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)

def is_task_owned(task_uuid: str) -> bool:
    return (get_hash(task_uuid) % TOTAL_SCHEDULERS) == SCHEDULER_ID

def send_task_periodic(task):
    tid = task['task_uuid']
    if not is_task_owned(tid):
        log(f"[scheduler-{SCHEDULER_ID}] [INFO] Ignorando envio da tarefa {tid} — ownership mudou.")
        # active_tasks.pop(tid, None)  # remove do dicionário
        return
    try:
        log(f"[scheduler-{SCHEDULER_ID}] [INFO] Enviando tarefa: Nome: {task['task_name']}, Tipo: {task['task_type']}, uuid: {task['task_uuid']} (id (db)={task['id']})")
        send_message({
            'task_name': task['task_name'],
            'id': task['id'],
            'task_uuid': task['task_uuid'],
            'task_type': task['task_type'],
            'payload': task['payload'],
        }, queue='tasks', hostname=f"scheduler-{SCHEDULER_ID}")
    except Exception as e:
        log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Erro ao enviar tarefa: {e}")
    finally:
        interval = task['interval_seconds']
        tid = task['task_uuid']
        timer = threading.Timer(interval, send_task_periodic, args=(task,))
        timer.daemon = True
        timer.start()
        active_tasks[tid] = timer  # Armazena o timer ativo para essa tarefa
 
def start_scheduler():
    try:
        tasks = get_all_tasks()
    except Exception as e:
        log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Erro ao buscar tarefas: {e}")
        return
    my_tasks = [t for t in tasks if is_task_owned(t['task_uuid'])]
    log(f"[scheduler-{SCHEDULER_ID}] [INFO] TOTAL_SCHEDULERS atual: {TOTAL_SCHEDULERS}")
    log(f"[scheduler-{SCHEDULER_ID}] [INFO] Gerenciando {len(my_tasks)} tarefas...")

    # Agenda disparo inicial imediato para cada tarefa
    for task in my_tasks:
        send_task_periodic(task)

def on_new_task_message(ch, method, properties, body):
    import json
    task = json.loads(body)
    tid = task['task_uuid']
    if is_task_owned(tid):
        log(f"[scheduler-{SCHEDULER_ID}] [INFO] Recebeu tarefa nova {tid} — é minha, agendando...")
        add_new_tasks([task]) # dicionário de uma tarefa
    else:
        log(f"[scheduler-{SCHEDULER_ID}] [INFO] Recebeu tarefa nova {tid} — não é minha, ignorando.")

def listen_for_new_tasks():
    try:
        start_consumer(
            callback=on_new_task_message,
            exchange='new_task_exchange',
            exchange_type='fanout',
            exclusive=True
        )
    except Exception as e:
        log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Erro ao iniciar consumidor RabbitMQ: {e}")
        log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Tentando reconectar-se ao RabbitMQ em 5 segundos...")
        threading.Timer(5, listen_for_new_tasks).start()

if __name__ == "__main__":
    threading.Thread(target=update_scheduler_count, daemon=True).start()
    threading.Thread(target=listen_for_new_tasks, daemon=True).start()
    threading.Timer(30, start_scheduler).start() 
    # Mantém o programa vivo para os timers funcionarem
    threading.Event().wait()
