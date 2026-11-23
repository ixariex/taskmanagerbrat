
from optimizer_bridge import (
    optimize_tasks,
    calculate_task_priority,
)

from database.task_repository import get_all_tasks


def main():
    print("=" * 55)
    print("TASKFORGE PYTHON-C++ INTEGRATION TEST")
    print("=" * 55)

    # Получаем настоящие задачи из SQLite.
    all_tasks = get_all_tasks()

    active_tasks = [
        task for task in all_tasks
        if task[7] in {"new", "in_progress"}
    ]

    completed_tasks = [
        task for task in all_tasks
        if task[7] == "completed"
    ]

    print(f"\nTotal tasks: {len(all_tasks)}")
    print(f"Active tasks: {len(active_tasks)}")
    print(f"Completed tasks: {len(completed_tasks)}")

    # Передаём задачи в C++.
    optimized_tasks = optimize_tasks(all_tasks)

    print("\nOPTIMIZED TASKS:")
    print("-" * 55)

    priorities = []

    for index, task in enumerate(optimized_tasks, start=1):
        priority = calculate_task_priority(task)
        priorities.append(priority)

        print(
            f"{index}. {task[1]} "
            f"| Priority: {priority:.2f} "
            f"| Status: {task[7]}"
        )

    # Проверяем, что все активные задачи сохранились.
    assert len(optimized_tasks) == len(active_tasks), (
        "Some active tasks were lost during optimization!"
    )

    # Проверяем сортировку по убыванию приоритета.
    assert priorities == sorted(priorities, reverse=True), (
        "Tasks are not sorted by priority!"
    )

    # Проверяем, что завершённые задачи исключены.
    assert all(task[7] != "completed" for task in optimized_tasks)

    print("\n" + "=" * 55)
    print("ALL INTEGRATION TESTS PASSED!")
    print("=" * 55)


if __name__ == "__main__":
    main()
