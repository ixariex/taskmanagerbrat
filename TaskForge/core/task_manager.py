
from database.task_repository import (
    add_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    assign_category
)

from database.category_repository import get_category_by_id


# CREATE TASK
def create_task(
    title,
    description=None,
    importance=5,
    urgency=5,
    difficulty=5,
    deadline=None,
    status="new",
    category_id=None
):
    """
    Creates a new task.
    Optionally assigns a category.
    """

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title cannot be empty")

    # Check category before creating task
    if category_id is not None:
        if get_category_by_id(category_id) is None:
            raise ValueError("Category does not exist")

    task_id = add_task(
        title.strip(),
        description,
        importance,
        urgency,
        difficulty,
        deadline,
        status
    )

    # Assign category if provided
    if category_id is not None:
        result = assign_category(task_id, category_id)

        if not result:
            delete_task(task_id)
            raise RuntimeError("Failed to assign category")

    return task_id


# GET ALL TASKS
def get_tasks():
    """
    Returns all tasks from the database.
    """
    return get_all_tasks()


# GET TASK BY ID
def get_task(task_id):
    """
    Returns a task by its ID.
    """
    return get_task_by_id(task_id)


# EDIT TASK
def edit_task(
    task_id,
    title,
    description,
    importance,
    urgency,
    difficulty,
    deadline,
    status
):
    """
    Updates existing task information.
    """

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task title cannot be empty")

    return update_task(
        task_id,
        title.strip(),
        description,
        importance,
        urgency,
        difficulty,
        deadline,
        status
    )


# CHANGE TASK STATUS
def set_task_status(task_id, status):
    """
    Changes the status of an existing task.
    """

    task = get_task_by_id(task_id)

    if task is None:
        return False

    return update_task(
        task_id,
        task[1],
        task[2],
        task[3],
        task[4],
        task[5],
        task[6],
        status
    )


# COMPLETE TASK
def complete_task(task_id):
    """
    Marks a task as completed.
    """

    return set_task_status(task_id, "completed")


# DELETE TASK
def remove_task(task_id):
    """
    Deletes a task from the database.
    """

    return delete_task(task_id)


# SET TASK CATEGORY
def set_task_category(task_id, category_id):
    """
    Assigns a category to an existing task.
    """

    return assign_category(task_id, category_id)

