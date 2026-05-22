import os
import time
import psycopg2

def get_db_connection():
    max_retries = 5
    while max_retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                database=os.getenv("POSTGRES_DB", "tickets_database"),
                user=os.getenv("POSTGRES_USER", "app"),
                password=os.getenv("POSTGRES_PASSWORD")
            )
            return conn
        except Exception as e:
            max_retries -= 1
            print(f"Reintentando conexión... ({max_retries} intentos restantes): {e}")
            time.sleep(2)
    return None