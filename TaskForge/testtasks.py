
import uuid

from database.database import create_db
from database.task_repository import (
    add_task,
    get_all_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    assign_category
)
from database.category_repository import (
    add_category,
    get_all_categories,
    delete_category
)


def main():
    create_db()

    suffix = uuid.uuid4().hex[:6]

    # 1. Create category
    category_name = f"Test Category {suffix}"

    assert add_category(category_name)

    categories = get_all_categories()

    category = next(
        item for item in categories
        if item[1] == category_name
    )

    category_id = category[0]

    print("CATEGORY CREATED: PASS")

    # 2. Add task
    title = f"Test Task {suffix}"

    task_id = add_task(
        title,
        "Testing TaskForge database",
        8,
        9,
        5,
        deadline="2026-12-15",
        status="new"
    )

    assert task_id is not None

    print("ADD TASK: PASS")

    # Get created task from database
    task = get_task_by_id(task_id)

    assert task is not None
    assert task[1] == title

    # Check deadline and status
    assert task[6] == "2026-12-15"
    assert task[7] == "new"

    print("GET TASK BY ID: PASS")
    print("DEADLINE CREATION: PASS")
    print("STATUS CREATION: PASS")

    # 3. Get task by ID
    task = get_task_by_id(task_id)

    assert task is not None
    assert task[1] == title

    print("GET TASK BY ID: PASS")

    # 4. Get all tasks
    tasks = get_all_tasks()

    assert any(item[0] == task_id for item in tasks)

    print("GET ALL TASKS: PASS")

    result = update_task(
        task_id,
        "Updated Test Task",
        "Updated description",
        10,
        8,
        6,
        deadline="2026-12-20",
        status="in_progress"
    )

    assert result is True

    updated_task = get_task_by_id(task_id)

    assert updated_task[1] == "Updated Test Task"
    assert updated_task[3] == 10
    assert updated_task[6] == "2026-12-20"
    assert updated_task[7] == "in_progress"

    print("DEADLINE UPDATE: PASS")
    print("STATUS UPDATE: PASS")

    print("UPDATE TASK: PASS")

    # 6. Assign category
    result = assign_category(task_id, category_id)

    assert result is True

    task = get_task_by_id(task_id)

    assert task[8] == category_id

    print("ASSIGN CATEGORY: PASS")

    # 7. Delete category and check task remains
    result = delete_category(category_id)

    assert result is True

    task = get_task_by_id(task_id)

    assert task is not None
    assert task[8] is None

    print("DELETE CATEGORY: PASS")

    # 8. Delete task
    result = delete_task(task_id)

    assert result is True

    assert get_task_by_id(task_id) is None

    print("DELETE TASK: PASS")

    print("\nALL TASK TESTS PASSED!")


if __name__ == "__main__":
    main()
