
"""
TaskForge C++ Optimizer Bridge

Connects the Python task system with the C++ task_optimizer module.
"""

from typing import Sequence

import task_optimizer


ACTIVE_STATUSES = {"new", "in_progress"}


def _convert_to_cpp_task(task_row: tuple):
    """
    Convert a TaskForge database row into a C++ Task object.

    Database row structure:
    (id, title, description, importance, urgency,
     difficulty, deadline, status, category_id)
    """

    if len(task_row) < 8:
        raise ValueError(
            "Invalid task row: expected at least 8 fields."
        )

    status = task_row[7]

    if status not in ACTIVE_STATUSES:
        return None

    cpp_task = task_optimizer.Task()

    cpp_task.id = int(task_row[0])
    cpp_task.title = str(task_row[1])
    cpp_task.importance = int(task_row[3])
    cpp_task.urgency = int(task_row[4])
    cpp_task.difficulty = int(task_row[5])

    # estimated_time is not stored in the current SQLite schema.
    # The existing C++ priority formula does not use this field.
    cpp_task.estimated_time = 0

    return cpp_task


def optimize_tasks(task_rows: Sequence[tuple]) -> list[tuple]:
    """
    Sort unfinished TaskForge tasks using the C++ optimizer.

    Returns the original database rows in optimized order.
    All original fields are preserved.
    """

    cpp_tasks = []
    original_tasks = {}

    for task_row in task_rows:
        cpp_task = _convert_to_cpp_task(task_row)

        if cpp_task is None:
            continue

        task_id = int(task_row[0])

        cpp_tasks.append(cpp_task)
        original_tasks[task_id] = task_row

    if not cpp_tasks:
        return []

    sorted_cpp_tasks = task_optimizer.sort_tasks(cpp_tasks)

    optimized_rows = [
        original_tasks[int(cpp_task.id)]
        for cpp_task in sorted_cpp_tasks
    ]

    return optimized_rows


def calculate_task_priority(task_row: tuple) -> float:
    """
    Calculate the priority of one unfinished TaskForge task.
    """

    cpp_task = _convert_to_cpp_task(task_row)

    if cpp_task is None:
        raise ValueError(
            "Cannot calculate priority for a completed task."
        )

    return float(
        task_optimizer.calculate_priority(cpp_task)
    )
