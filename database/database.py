"""SQLite database setup and connection helpers."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = str(DATA_DIR / "taskforge.db")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a configured SQLite connection and always close it."""
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
    """Create tables and migrate older TaskForge databases safely."""
    with get_connection() as conn:
        # Categories must exist before tasks because tasks reference them.
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

        # CREATE TABLE IF NOT EXISTS does not add columns to an existing DB.
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

        # Add columns if a very early/partial database is encountered.
        if "deadline" not in task_columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN deadline TEXT")
        if "status" not in task_columns:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN status TEXT NOT NULL DEFAULT 'new'"
            )

    print("Database created successfully")


if __name__ == "__main__":
    create_db()
