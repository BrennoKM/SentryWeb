import hashlib
import threading
from datetime import datetime, timezone
from db.tasks import get_all_tasks
from messaging.producer import send_message
import uuid

TOTAL_TASKS = 1000
TOTAL_SCHEDULERS = 2
SCHEDULER_ID = 1

def get_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)

def is_task_owned(task_uuid: str) -> bool:
    return (get_hash(task_uuid) % TOTAL_SCHEDULERS) == SCHEDULER_ID


if __name__ == "__main__":

    # Contagem de tarefas por scheduler
    matrix = [0] * TOTAL_SCHEDULERS


    for i in range(TOTAL_TASKS):
        task_uuid = uuid.uuid4()
        hash_value = get_hash(str(task_uuid))
        owner = hash_value % TOTAL_SCHEDULERS
        print(f"Task ID: {task_uuid}, Hash: {hash_value},\tScheduler Owner: {owner}")
        matrix[owner] += 1
    
    for i in range(TOTAL_SCHEDULERS):
        print(f"Scheduler {i} gerencia {matrix[i]} tarefas")
    print(f"Total de tarefas: {sum(matrix)}")
    print(f"Total de schedulers: {TOTAL_SCHEDULERS}")
    print(f"Média de tarefas por scheduler: {sum(matrix) / TOTAL_SCHEDULERS}")
    print(f"Maior número de tarefas: {max(matrix)}")
    print(f"Menor número de tarefas: {min(matrix)}")
    print(f"Diferença: {max(matrix) - min(matrix)}")
    




