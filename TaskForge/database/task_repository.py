

from datetime import date
from typing import Optional

from database.database import get_connection


VALID_STATUSES = {"new", "in_progress", "completed"}


def validate_deadline(deadline: Optional[str]) -> Optional[str]:
    if deadline is None or deadline == "":
        return None
    if not isinstance(deadline, str):
        raise ValueError("Deadline must be a string in YYYY-MM-DD format")
    try:
        parsed = date.fromisoformat(deadline)
    except ValueError as exc:
        raise ValueError("Deadline must have format YYYY-MM-DD") from exc
    if parsed.isoformat() != deadline:
        raise ValueError("Deadline must have format YYYY-MM-DD")
    return deadline


def validate_status(status: str) -> None:
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status: {status!r}. Choose one of: {sorted(VALID_STATUSES)}"
        )


def _validate_score(value: int, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 10:
        raise ValueError(f"{field_name} must be an integer from 1 to 10")


def add_task(
    title: str,
    description: Optional[str] = None,
    importance: int = 5,
    urgency: int = 5,
    difficulty: int = 5,
    deadline: Optional[str] = None,
    status: str = "new",
) -> int:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title cannot be empty")
    _validate_score(importance, "importance")
    _validate_score(urgency, "urgency")
    _validate_score(difficulty, "difficulty")
    deadline = validate_deadline(deadline)
    validate_status(status)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks (
                title, description, importance, urgency, difficulty,
                deadline, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(), description, importance, urgency,
                difficulty, deadline, status,
            ),
        )
        return int(cursor.lastrowid)


def get_all_tasks() -> list[tuple]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, title, description, importance, urgency, difficulty,
                   deadline, status, category_id
            FROM tasks
            ORDER BY id
            """
        )
        return cursor.fetchall()


def get_task_by_id(task_id: int) -> Optional[tuple]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, title, description, importance, urgency, difficulty,
                   deadline, status, category_id
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )
        return cursor.fetchone()


def update_task(
    task_id: int,
    title: str,
    description: Optional[str],
    importance: int,
    urgency: int,
    difficulty: int,
    deadline: Optional[str] = None,
    status: str = "new",
) -> bool:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title cannot be empty")
    _validate_score(importance, "importance")
    _validate_score(urgency, "urgency")
    _validate_score(difficulty, "difficulty")
    deadline = validate_deadline(deadline)
    validate_status(status)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, importance = ?, urgency = ?,
                difficulty = ?, deadline = ?, status = ?
            WHERE id = ?
            """,
            (
                title.strip(), description, importance, urgency,
                difficulty, deadline, status, task_id,
            ),
        )
        return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )
        return cursor.rowcount > 0


def assign_category(task_id: int, category_id: Optional[int]) -> bool:
    with get_connection() as conn:
        task = conn.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if task is None:
            return False

        if category_id is not None:
            category = conn.execute(
                "SELECT id FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            if category is None:
                return False

        cursor = conn.execute(
            "UPDATE tasks SET category_id = ? WHERE id = ?",
            (category_id, task_id),
        )
        return cursor.rowcount > 0
