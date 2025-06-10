DROP TABLE IF EXISTS tasks;

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_uuid UUID NOT NULL UNIQUE,
    task_name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    interval_seconds INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
