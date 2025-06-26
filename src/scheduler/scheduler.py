import threading
import hashlib
import time
import os
import json
import heapq
from utils.log import log
from db.tasks import get_all_tasks
from messaging.producer import send_message
from k8s.discovery import get_total_schedulers
from messaging.consumer import start_consumer

hostname = os.environ.get("HOSTNAME", "scheduler-0")
try:
    SCHEDULER_ID = int(hostname.split('-')[-1])
except Exception:
    SCHEDULER_ID = 0

TOTAL_SCHEDULERS = int(os.environ.get("TOTAL_SCHEDULERS", "2"))

active_tasks = {}
schedule_heap = []
tasks_lock = threading.Lock()

def get_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)

def is_task_owned(task_uuid: str) -> bool:
    return (get_hash(task_uuid) % TOTAL_SCHEDULERS) == SCHEDULER_ID

def sync_tasks():
    log(f"[scheduler-{SCHEDULER_ID}] [INFO] Iniciando sincronização completa de tarefas...")
    try:
        all_tasks_from_db = get_all_tasks()
        my_tasks = [t for t in all_tasks_from_db if is_task_owned(t['task_uuid'])]

        with tasks_lock:
            my_tasks_map = {t['task_uuid']: t for t in my_tasks}
            current_task_ids = set(active_tasks.keys())
            new_task_ids = set(my_tasks_map.keys())

            to_remove = current_task_ids - new_task_ids
            for tid in to_remove:
                active_tasks.pop(tid, None)
                log(f"[scheduler-{SCHEDULER_ID}] [INFO] Tarefa {tid} removida (não pertence mais a este scheduler).")
            
            for tid, task in my_tasks_map.items():
                if tid not in current_task_ids:
                    log(f"[scheduler-{SCHEDULER_ID}] [INFO] Nova tarefa adicionada via sync: {tid}")
                    _schedule_task(task, is_new=True)
                else:
                    if active_tasks[tid]['interval_seconds'] != task['interval_seconds']:
                         log(f"[scheduler-{SCHEDULER_ID}] [INFO] Tarefa {tid} atualizada com novo intervalo.")
                         _schedule_task(task, is_new=False)
            
            log(f"[scheduler-{SCHEDULER_ID}] [INFO] Sincronização concluída. Gerenciando agora {len(active_tasks)} tarefas.")

    except Exception as e:
        log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Falha na sincronização de tarefas: {e}")

def _schedule_task(task: dict, is_new: bool):
    tid = task['task_uuid']
    
    active_tasks[tid] = task
    
    next_run_time = time.time()
    
    heapq.heappush(schedule_heap, (next_run_time, tid))
    log(f"[scheduler-{SCHEDULER_ID}] [DEBUG] Tarefa {tid} agendada para execução em {task['interval_seconds']} segundos.")

def send_task_message(task):
    try:
        log(f"[scheduler-{SCHEDULER_ID}] [INFO] Enviando tarefa: Nome: {task['task_name']}, uuid: {task['task_uuid']}, id (db): {task['id']}")
        send_message({
            'task_name': task['task_name'],
            'id': task['id'],
            'task_uuid': task['task_uuid'],
            'task_type': task['task_type'],
            'payload': task['payload'],
        }, queue='tasks', hostname=f"scheduler-{SCHEDULER_ID}")
    except Exception as e:
        log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Erro ao enviar tarefa {task['task_uuid']}: {e}")

def scheduler_loop():
    while True:
        with tasks_lock:
            if not schedule_heap:
                time.sleep(1)
                continue

            next_run_time, task_uuid = schedule_heap[0]

        sleep_duration = next_run_time - time.time()

        if sleep_duration > 0:
            time.sleep(sleep_duration)

        with tasks_lock:
            if not schedule_heap:
                continue
            
            _, tid = heapq.heappop(schedule_heap)

            if tid not in active_tasks or not is_task_owned(tid):
                log(f"[scheduler-{SCHEDULER_ID}] [INFO] Ignorando tarefa obsoleta ou reatribuída: {tid}")
                continue

            task_to_run = active_tasks[tid]

            send_task_message(task_to_run)
            
            interval = task_to_run['interval_seconds']
            new_next_run_time = time.time() + interval
            heapq.heappush(schedule_heap, (new_next_run_time, tid))
            
def on_new_task_message(ch, method, properties, body):
    try:
        task = json.loads(body)
        tid = task['task_uuid']
        if is_task_owned(tid):
            log(f"[scheduler-{SCHEDULER_ID}] [INFO] Recebeu nova tarefa {tid} via RabbitMQ — é minha, agendando...")
            with tasks_lock:
                _schedule_task(task, is_new=True)
            log(f"[scheduler-{SCHEDULER_ID}] [INFO] Agora gerenciando {len(active_tasks)} tarefas ativas.")
        else:
            log(f"[scheduler-{SCHEDULER_ID}] [INFO] Recebeu nova tarefa {tid} — não é minha, ignorando.")
    except Exception as e:
        log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Erro ao processar mensagem de nova tarefa: {e}")


def listen_for_new_tasks():
    while True:
        try:
            log(f"[scheduler-{SCHEDULER_ID}] [INFO] Conectando ao RabbitMQ para ouvir novas tarefas...")
            start_consumer(
                callback=on_new_task_message,
                exchange='new_task_exchange',
                exchange_type='fanout',
                exclusive=True
            )
        except Exception as e:
            log(f"[scheduler-{SCHEDULER_ID}] [ERRO] Erro no consumidor RabbitMQ: {e}. Tentando reconectar em 10s...")
            time.sleep(10)


def update_scheduler_count():
    global TOTAL_SCHEDULERS
    while True:
        try:
            new_total = get_total_schedulers()
            if new_total != TOTAL_SCHEDULERS:
                log(f"[scheduler-{SCHEDULER_ID}] [INFO] TOTAL_SCHEDULERS alterado: {TOTAL_SCHEDULERS} -> {new_total}")
                log(f"[scheduler-{SCHEDULER_ID}] [INFO] Gerenciando agora {len(active_tasks)} tarefas ativas.")
                TOTAL_SCHEDULERS = new_total
                sync_tasks()
        except Exception as e:
            log(f"[{hostname}] [ERRO] Erro ao consultar schedulers ativos: {e}")
        time.sleep(30)


if __name__ == "__main__":
    log(f"[scheduler-{SCHEDULER_ID}] [INFO] Iniciando scheduler...")
    threading.Thread(target=update_scheduler_count, daemon=True).start()
    threading.Thread(target=listen_for_new_tasks, daemon=True).start()
    time.sleep(10)
    sync_tasks()
    log(f"[scheduler-{SCHEDULER_ID}] [INFO] Iniciando o loop de agendamento principal.")
    scheduler_loop()