import uuid
from datetime import datetime, timezone
from .database import get_cursor

def insert_task(task_name, task_type, payload_json, interval_seconds):
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    conn, cur = get_cursor()
    cur.execute("""
        INSERT INTO tasks (task_id, task_name, task_type, payload, interval_seconds, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (task_id, task_name, task_type, payload_json, interval_seconds, now))
    conn.commit()
    cur.close()
    conn.close()
    return task_id


def get_all_tasks():
    conn, cur = get_cursor()
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks

def update_last_run(task_id):
    conn, cur = get_cursor()
    cur.execute("UPDATE tasks SET last_run = %s, updated_at = NOW() WHERE task_id = %s",
                (datetime.utcnow(), task_id))
    conn.commit()
    cur.close()
    conn.close()
