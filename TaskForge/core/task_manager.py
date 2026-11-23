

from typing import Optional

from database.category_repository import get_category_by_id
from database.task_repository import (
    add_task,
    assign_category,
    delete_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    validate_deadline,
    validate_status,
)


def create_task(
    title: str,
    description: Optional[str] = None,
    importance: int = 5,
    urgency: int = 5,
    difficulty: int = 5,
    deadline: Optional[str] = None,
    status: str = "new",
    category_id: Optional[int] = None,
) -> int:
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title cannot be empty")

    if category_id is not None and get_category_by_id(category_id) is None:
        raise ValueError("Selected category does not exist")

    task_id = add_task(
        title=title.strip(),
        description=description,
        importance=importance,
        urgency=urgency,
        difficulty=difficulty,
        deadline=deadline,
        status=status,
    )

    if category_id is not None and not assign_category(task_id, category_id):
        delete_task(task_id)
        raise RuntimeError("Could not assign the selected category")

    return task_id


def get_tasks() -> list[tuple]:
    return get_all_tasks()


def get_task(task_id: int) -> Optional[tuple]:
    return get_task_by_id(task_id)


def edit_task(
    task_id: int,
    title: str,
    description: Optional[str],
    importance: int,
    urgency: int,
    difficulty: int,
    deadline: Optional[str] = None,
    status: str = "new",
) -> bool:
    if get_task_by_id(task_id) is None:
        return False
    return update_task(
        task_id, title, description, importance, urgency,
        difficulty, deadline, status,
    )


def set_task_status(task_id: int, status: str) -> bool:
    validate_status(status)
    task = get_task_by_id(task_id)
    if task is None:
        return False
    return update_task(
        task_id=task_id,
        title=task[1],
        description=task[2],
        importance=task[3],
        urgency=task[4],
        difficulty=task[5],
        deadline=task[6],
        status=status,
    )


def complete_task(task_id: int) -> bool:
    return set_task_status(task_id, "completed")


def remove_task(task_id: int) -> bool:
    return delete_task(task_id)


def set_task_category(task_id: int, category_id: Optional[int]) -> bool:
    return assign_category(task_id, category_id)
