import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "host.docker.internal"),
        port=int(os.getenv("DB_PORT", "5458")),
        dbname=os.getenv("DB_NAME", "rekun28"),
        user=os.getenv("DB_USER", "rekun"),
        password=os.environ["DB_PASSWORD"],
    )

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL
                )
            """)
