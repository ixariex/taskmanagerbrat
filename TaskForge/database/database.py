

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = str(DATA_DIR / "taskforge.db")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def create_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT '#3498db'
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                importance INTEGER NOT NULL DEFAULT 5,
                urgency INTEGER NOT NULL DEFAULT 5,
                difficulty INTEGER NOT NULL DEFAULT 5,
                deadline TEXT,
                status TEXT NOT NULL DEFAULT 'new',
                category_id INTEGER REFERENCES categories(id)
                    ON DELETE SET NULL
            )
            """
        )

        task_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()
        }
        if "category_id" not in task_columns:
            conn.execute(
                """
                ALTER TABLE tasks
                ADD COLUMN category_id INTEGER REFERENCES categories(id)
                    ON DELETE SET NULL
                """
            )

        if "deadline" not in task_columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN deadline TEXT")
        if "status" not in task_columns:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN status TEXT NOT NULL DEFAULT 'new'"
            )

    print("Database created successfully")


if __name__ == "__main__":
    create_db()
