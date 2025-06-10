import uuid
from datetime import datetime, timezone
from .database import get_cursor

def insert_task(task_name, task_type, payload_json, interval_seconds):
    task_uuid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    conn, cur = get_cursor()
    cur.execute("""
        INSERT INTO tasks (task_uuid, task_name, task_type, payload, interval_seconds, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (task_uuid, task_name, task_type, payload_json, interval_seconds, now))
    conn.commit()
    cur.close()
    conn.close()
    return task_uuid

def get_db_id_by_task_uuid(task_uuid): # busca o id do banco de dados pelo task_uuid (uuid)
    conn, cur = get_cursor()
    cur.execute("SELECT id FROM tasks WHERE task_uuid = %s", (task_uuid,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0]
    return None

def get_all_tasks():
    conn, cur = get_cursor()
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks

def update_last_run(task_uuid):
    conn, cur = get_cursor()
    cur.execute("UPDATE tasks SET last_run = %s, updated_at = NOW() WHERE task_uuid = %s",
                (datetime.utcnow(), task_uuid))
    conn.commit()
    cur.close()
    conn.close()
