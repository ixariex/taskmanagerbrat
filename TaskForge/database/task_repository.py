
import sqlite3
from datetime import date

from database.database import DB_PATH


VALID_STATUSES = {
    "new",
    "in_progress",
    "completed"
}


def validate_deadline(deadline):
    if deadline is None or deadline == "":
        return None

    try:
        parsed_date = date.fromisoformat(deadline)

        if parsed_date.isoformat() != deadline:
            raise ValueError

        return deadline

    except (ValueError, TypeError):
        raise ValueError(
            "Deadline must have format YYYY-MM-DD"
        )


def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status: {status}. "
            f"Available statuses: {VALID_STATUSES}"
        )


def add_task(
    title,
    description=None,
    importance=5,
    urgency=5,
    difficulty=5,
    deadline=None,
    status="new"
):
    deadline = validate_deadline(deadline)
    validate_status(status)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO tasks (
                title,
                description,
                importance,
                urgency,
                difficulty,
                deadline,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            description,
            importance,
            urgency,
            difficulty,
            deadline,
            status
        ))

        return cur.lastrowid


def get_all_tasks():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                title,
                description,
                importance,
                urgency,
                difficulty,
                deadline,
                status,
                category_id
            FROM tasks
        """)

        return cur.fetchall()


# READ: Get task by ID
def get_task_by_id(task_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                title,
                description,
                importance,
                urgency,
                difficulty,
                deadline,
                status,
                category_id
            FROM tasks
            WHERE id = ?
        """, (task_id,))

        return cur.fetchone()


def update_task(
    task_id,
    title,
    description,
    importance,
    urgency,
    difficulty,
    deadline,
    status
):
    deadline = validate_deadline(deadline)
    validate_status(status)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute("""
            UPDATE tasks
            SET
                title = ?,
                description = ?,
                importance = ?,
                urgency = ?,
                difficulty = ?,
                deadline = ?,
                status = ?
            WHERE id = ?
        """, (
            title,
            description,
            importance,
            urgency,
            difficulty,
            deadline,
            status,
            task_id
        ))

        return cur.rowcount > 0


def delete_task(task_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        return cur.rowcount > 0



def assign_category(task_id, category_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        # Check whether task exists
        cur.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,)
        )

        if cur.fetchone() is None:
            return False

        # Check category if one was selected
        if category_id is not None:
            cur.execute(
                "SELECT id FROM categories WHERE id = ?",
                (category_id,)
            )

            if cur.fetchone() is None:
                return False

        # Assign or remove category
        cur.execute(
            "UPDATE tasks SET category_id = ? WHERE id = ?",
            (category_id, task_id)
        )

        return cur.rowcount > 0
