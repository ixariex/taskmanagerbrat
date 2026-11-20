import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "taskforge.db")


def create_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        color TEXT DEFAULT '#3498db'
        )
        ''')
    c.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    importance INTEGER DEFAULT 5,
                    urgency INTEGER DEFAULT 5,
                    difficulty INTEGER DEFAULT 5,
                    deadline TEXT,
                    status TEXT DEFAULT 'new',
                    category_id INTEGER REFERENCES categories(id)
                        ON DELETE SET NULL
                )
            """)
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(tasks)")
    }

    if "category_id" not in columns:
        conn.execute("""
                    ALTER TABLE tasks
                    ADD COLUMN category_id INTEGER REFERENCES categories(id)
                    ON DELETE SET NULL
                """)


print("Database created successfully")

if __name__ == "__main__":
    create_db()

