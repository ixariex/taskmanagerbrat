

import uuid

from database.database import create_db
from database.category_repository import add_category, get_all_categories, delete_category
from database.task_repository import (
    add_task, get_all_tasks, get_task_by_id, update_task,
    delete_task, assign_category,
)


def main():
    create_db()
    suffix = uuid.uuid4().hex[:8]
    category_id = None
    task_id = None

    try:
        category_name = f"Test Category {suffix}"
        assert add_category(category_name)
        category = next(row for row in get_all_categories() if row[1] == category_name)
        category_id = category[0]
        print("CATEGORY CREATED: PASS")

        title = f"Test Task {suffix}"
        task_id = add_task(
            title, "Testing TaskForge database", 8, 9, 5,
            deadline="2026-12-15", status="new",
        )
        assert task_id is not None
        print("ADD TASK: PASS")

        task = get_task_by_id(task_id)
        assert task is not None and task[1] == title
        print("GET TASK BY ID: PASS")
        assert task[6] == "2026-12-15"
        print("DEADLINE CREATION: PASS")
        assert task[7] == "new"
        print("STATUS CREATION: PASS")

        tasks = get_all_tasks()
        assert any(row[0] == task_id for row in tasks)
        print("GET ALL TASKS: PASS")

        assert update_task(
            task_id, "Updated Test Task", "Updated description", 10, 8, 6,
            "2026-12-20", "in_progress",
        )
        updated = get_task_by_id(task_id)
        assert updated[1] == "Updated Test Task" and updated[3] == 10
        print("UPDATE TASK: PASS")
        assert updated[6] == "2026-12-20"
        print("DEADLINE UPDATE: PASS")
        assert updated[7] == "in_progress"
        print("STATUS UPDATE: PASS")

        assert assign_category(task_id, category_id)
        assert get_task_by_id(task_id)[8] == category_id
        print("ASSIGN CATEGORY: PASS")

        assert delete_category(category_id)
        category_id = None
        assert get_task_by_id(task_id)[8] is None
        print("DELETE CATEGORY (TASK PRESERVED): PASS")

        deleted_task_id = task_id
        assert delete_task(deleted_task_id)
        assert get_task_by_id(deleted_task_id) is None
        task_id = None
        print("DELETE TASK: PASS")

        print("\nALL TASK REPOSITORY TESTS PASSED!")
    finally:
        if task_id is not None:
            delete_task(task_id)
        if category_id is not None:
            delete_category(category_id)


if __name__ == "__main__":
    main()
