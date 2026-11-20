
import uuid

from database.database import create_db
from database.category_repository import add_category, get_all_categories
from core.task_manager import (
    create_task,
    get_tasks,
    get_task,
    edit_task,
    complete_task,
    remove_task,
    set_task_category
)


def main():
    create_db()

    suffix = uuid.uuid4().hex[:6]

    # 1. Create category
    category_name = f"Manager Category {suffix}"
    assert add_category(category_name)

    categories = get_all_categories()

    category = next(
        item for item in categories
        if item[1] == category_name
    )

    category_id = category[0]

    print("CREATE CATEGORY: PASS")

    # 2. Create task
    task_id = create_task(
        title=f"Manager Task {suffix}",
        description="Testing Task Manager",
        importance=8,
        urgency=9,
        difficulty=5,
        deadline="2026-12-15",
        status="new",
        category_id=category_id
    )

    assert task_id is not None

    print("CREATE TASK: PASS")

    # 3. Get task
    task = get_task(task_id)

    assert task is not None
    assert task[8] == category_id

    print("GET TASK: PASS")

    # 4. Get all tasks
    tasks = get_tasks()

    assert any(item[0] == task_id for item in tasks)

    print("GET ALL TASKS: PASS")

    # 5. Edit task
    result = edit_task(
        task_id,
        "Updated Manager Task",
        "Updated description",
        10,
        8,
        6,
        "2026-12-20",
        "in_progress"
    )

    assert result is True

    task = get_task(task_id)

    assert task[1] == "Updated Manager Task"
    assert task[3] == 10
    assert task[6] == "2026-12-20"
    assert task[7] == "in_progress"

    print("EDIT TASK: PASS")

    # 6. Complete task
    result = complete_task(task_id)

    assert result is True

    task = get_task(task_id)

    assert task[7] == "completed"

    print("COMPLETE TASK: PASS")

    # 7. Change status back
    result = set_task_status_test(task_id, "new")

    assert result is True

    print("CHANGE STATUS: PASS")

    # 8. Remove task
    result = remove_task(task_id)

    assert result is True
    assert get_task(task_id) is None

    print("REMOVE TASK: PASS")

    print("\nALL TASK MANAGER TESTS PASSED!")


def set_task_status_test(task_id, status):
    from core.task_manager import set_task_status
    return set_task_status(task_id, status)


if __name__ == "__main__":
    main()
