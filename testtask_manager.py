

import uuid

from database.database import create_db
from database.category_repository import add_category, get_all_categories, delete_category
from core.task_manager import (
    create_task, get_tasks, get_task, edit_task, complete_task,
    set_task_status, remove_task,
)


def main():
    create_db()
    suffix = uuid.uuid4().hex[:8]
    category_id = None
    task_id = None

    try:
        category_name = f"Manager Category {suffix}"
        assert add_category(category_name)
        category = next(row for row in get_all_categories() if row[1] == category_name)
        category_id = category[0]
        print("CREATE CATEGORY: PASS")

        task_id = create_task(
            title=f"Manager Task {suffix}",
            description="Testing Task Manager",
            importance=8, urgency=9, difficulty=5,
            deadline="2026-12-15", status="new", category_id=category_id,
        )
        print("CREATE TASK: PASS")

        task = get_task(task_id)
        assert task is not None and task[8] == category_id
        print("GET TASK: PASS")

        assert any(row[0] == task_id for row in get_tasks())
        print("GET ALL TASKS: PASS")

        assert edit_task(
            task_id, "Updated Manager Task", "Updated description",
            10, 8, 6, "2026-12-20", "in_progress",
        )
        task = get_task(task_id)
        assert task[1] == "Updated Manager Task"
        assert task[3] == 10 and task[6] == "2026-12-20"
        assert task[7] == "in_progress"
        print("EDIT TASK: PASS")

        assert complete_task(task_id)
        assert get_task(task_id)[7] == "completed"
        print("COMPLETE TASK: PASS")

        assert set_task_status(task_id, "new")
        assert get_task(task_id)[7] == "new"
        print("CHANGE STATUS: PASS")

        assert remove_task(task_id)
        task_id = None
        print("REMOVE TASK: PASS")

        print("\nALL TASK MANAGER TESTS PASSED!")
    finally:
        if task_id is not None:
            remove_task(task_id)
        if category_id is not None:
            delete_category(category_id)


if __name__ == "__main__":
    main()
