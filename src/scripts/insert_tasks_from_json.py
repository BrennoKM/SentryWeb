import json
from db.tasks import insert_task

def load_tasks_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data.get('tasks', [])

def insert_tasks(tasks):
    inserted_ids = []
    for task in tasks:
        try:
            task_id = insert_task(
                task_name=task['task_name'],
                task_type=task['task_type'],
                payload_json=json.dumps(task['payload']),
                interval_seconds=task['interval_seconds']
            )
            inserted_ids.append(task_id)
            print(f"✅ Tarefa '{task['task_name']}' inserida com id {task_id}")
        except Exception as e:
            print(f"❌ Erro ao inserir tarefa '{task['task_name']}': {str(e)}")
    return inserted_ids

if __name__ == "__main__":
    json_file = "tasks.json"
    
    print(f"Carregando tarefas do arquivo {json_file}...")
    tasks = load_tasks_from_file(json_file)
    
    if not tasks:
        print("Nenhuma tarefa encontrada no arquivo.")
    else:
        print(f"Encontradas {len(tasks)} tarefas. Iniciando inserção...")
        inserted_ids = insert_tasks(tasks)
        print(f"\nConcluído! {len(inserted_ids)} tarefas inseridas com sucesso.")