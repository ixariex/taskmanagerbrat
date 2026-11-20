
import sqlite3
from database.database import DB_PATH


def add_category(name, color="#3498db"):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO categories (name, color) VALUES (?, ?)",
                (name, color)
            )
        return True

    except sqlite3.IntegrityError:
        return False


def get_all_categories():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories")
        return cursor.fetchall()


def get_category_by_id(category_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM categories WHERE id = ?",
            (category_id,)
        )
        return cursor.fetchone()


def update_category(category_id, name, color=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        if color is not None:
            cursor.execute(
                "UPDATE categories SET name = ?, color = ? WHERE id = ?",
                (name, color, category_id)
            )
        else:
            cursor.execute(
                "UPDATE categories SET name = ? WHERE id = ?",
                (name, category_id)
            )

        return cursor.rowcount > 0


def delete_category(category_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM categories WHERE id = ?",
            (category_id,)
        )

        return cursor.rowcount > 0




