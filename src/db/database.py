import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        dbname='sentry_db',
        user='sentry',
        password='sentry',
        host='localhost',  # ou 'sentryk8s_postgres' no Docker Compose
        port=5432
    )

def get_cursor():
    conn = get_connection()
    return conn, conn.cursor(cursor_factory=RealDictCursor)
