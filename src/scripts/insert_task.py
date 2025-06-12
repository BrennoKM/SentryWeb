from db.tasks import insert_task

if __name__ == "__main__":
    task_name = "url_example"
    task_type = "url_checker"
    payload_json = '{"url": "https://example.com", "method": "GET"}'
    interval_seconds = 60

    task_uuid = insert_task(task_name, task_type, payload_json, interval_seconds)
    print(f"✅ Tarefa inserida com id {task_uuid}")
