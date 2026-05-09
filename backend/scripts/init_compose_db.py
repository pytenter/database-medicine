import os
import time
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

REQUIRED_TABLES = {
    "store",
    "sys_user",
    "announcement",
    "manufacturer",
    "medicine_category",
    "medicine",
    "inventory",
    "purchase_order",
    "purchase_order_item",
    "shift_schedule",
    "sale_order",
    "sale_order_item",
}

BASE_DIR = Path(__file__).resolve().parents[2]
SCHEMA_SQL = BASE_DIR / "sql" / "schema.sql"
INIT_DATA_SQL = BASE_DIR / "sql" / "init_data.sql"

DB_NAME = os.getenv("DB_NAME", "pharmacy_system")
DB_USER = os.getenv("DB_USER", "gaussdb")
DB_PASSWORD = os.getenv("DB_PASSWORD", "replace-with-a-secure-db-password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_ADMIN_DB = os.getenv("DB_ADMIN_DB", "postgres")
INIT_DB_DEMO_DATA = os.getenv("INIT_DB_DEMO_DATA", "True").lower() == "true"


def connect(dbname: str):
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=dbname,
    )


def wait_for_database(max_attempts: int = 60, delay: int = 2):
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            conn = connect(DB_ADMIN_DB)
            conn.close()
            print(f"Database is reachable on attempt {attempt}.")
            return
        except Exception as exc:
            last_error = exc
            print(f"Waiting for database ({attempt}/{max_attempts}): {exc}")
            time.sleep(delay)
    raise RuntimeError(f"Database did not become reachable: {last_error}")


def ensure_database_exists():
    conn = connect(DB_ADMIN_DB)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            exists = cur.fetchone() is not None
            if exists:
                print(f"Database '{DB_NAME}' already exists.")
                return
            cur.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"Database '{DB_NAME}' created.")
    finally:
        conn.close()


def get_existing_tables():
    conn = connect(DB_NAME)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            )
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()


def execute_sql_file(path: Path):
    sql = path.read_text(encoding="utf-8")
    conn = connect(DB_NAME)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        print(f"Executed {path.name}.")
    finally:
        conn.close()


def initialize_database_if_needed():
    existing_tables = get_existing_tables()
    if not existing_tables:
        execute_sql_file(SCHEMA_SQL)
        if INIT_DB_DEMO_DATA:
            execute_sql_file(INIT_DATA_SQL)
        return

    missing = REQUIRED_TABLES - existing_tables
    if missing:
        raise RuntimeError(
            "Database is partially initialized. Missing tables: "
            + ", ".join(sorted(missing))
            + ". Use a clean volume or initialize the database with sql/schema.sql and sql/init_data.sql."
        )

    print("Database schema is already initialized.")


if __name__ == "__main__":
    wait_for_database()
    ensure_database_exists()
    initialize_database_if_needed()
