

import uuid

from database.database import create_db
from database.task_repository import add_task, get_task_by_id
from core.category_manager import (
    create_category,
    edit_category,
    get_categories,
    get_category,
    remove_category,
)


def main():
    create_db()
    suffix = uuid.uuid4().hex[:8]
    category_id = None
    task_id = None
    name = f"Test Category {suffix}"

    try:
        assert create_category(name, "#123456")
        category = next(row for row in get_categories() if row[1] == name)
        category_id = category[0]
        assert category[2] == "#123456"
        print("CREATE CATEGORY: PASS")

        assert get_category(category_id)[1] == name
        print("GET CATEGORY: PASS")

        new_name = f"Renamed Category {suffix}"
        assert edit_category(category_id, new_name, "#abcdef")
        category = get_category(category_id)
        assert category[1] == new_name and category[2] == "#abcdef"
        print("EDIT CATEGORY: PASS")

        task_id = add_task(f"Category link test {suffix}")
        from database.task_repository import assign_category
        assert assign_category(task_id, category_id)
        assert get_task_by_id(task_id)[8] == category_id
        print("ASSIGN CATEGORY: PASS")

        assert remove_category(category_id)
        category_id = None
        task = get_task_by_id(task_id)
        assert task is not None and task[8] is None
        print("DELETE CATEGORY / KEEP TASK: PASS")

        print("\nALL CATEGORY MANAGER TESTS PASSED!")
    finally:
        if task_id is not None:
            from database.task_repository import delete_task
            delete_task(task_id)
        if category_id is not None:
            remove_category(category_id)


if __name__ == "__main__":
    main()
