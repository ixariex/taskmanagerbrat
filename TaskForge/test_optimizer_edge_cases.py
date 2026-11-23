
from optimizer_bridge import (
    optimize_tasks,
    calculate_task_priority,
)


def make_task(
    task_id,
    title,
    importance,
    urgency,
    difficulty,
    status="new",
):
    return (
        task_id,
        title,
        "Test description",
        importance,
        urgency,
        difficulty,
        None,
        status,
        None,
    )


def main():
    print("=" * 55)
    print("TASKFORGE OPTIMIZER EDGE CASE TESTS")
    print("=" * 55)

    # TEST 1: Empty task list
    result = optimize_tasks([])

    assert result == []

    print("\n[PASS] Empty task list")

    # TEST 2: Completed tasks must be excluded
    completed_task = make_task(
        1, "Completed task", 10, 10, 1, "completed"
    )

    result = optimize_tasks([completed_task])

    assert result == []

    print("[PASS] Completed tasks are excluded")

    # TEST 3: Active tasks are sorted correctly
    low_priority = make_task(
        2, "Low priority", 2, 2, 5
    )

    high_priority = make_task(
        3, "High priority", 9, 8, 3
    )

    medium_priority = make_task(
        4, "Medium priority", 6, 5, 4, "in_progress"
    )

    result = optimize_tasks([
        low_priority,
        completed_task,
        high_priority,
        medium_priority,
    ])

    result_ids = [task[0] for task in result]

    assert result_ids == [3, 4, 2]
    assert all(task[7] != "completed" for task in result)

    print("[PASS] Active tasks sorted correctly")

    # TEST 4: Original task data is preserved
    original_tasks = {
        task[0]: task
        for task in [
            low_priority,
            high_priority,
            medium_priority,
        ]
    }

    for task in result:
        assert task == original_tasks[task[0]]

    print("[PASS] Original database rows preserved")

    # TEST 5: Priority calculation
    priority = calculate_task_priority(high_priority)

    assert abs(priority - 8.5) < 0.001

    print(f"[PASS] Priority calculation: {priority:.2f}")

    # TEST 6: Completed task priority must raise an error
    try:
        calculate_task_priority(completed_task)
    except ValueError:
        print("[PASS] Completed task priority validation")
    else:
        raise AssertionError(
            "Expected ValueError for a completed task"
        )

    print("\n" + "=" * 55)
    print("ALL EDGE CASE TESTS PASSED!")
    print("=" * 55)


if __name__ == "__main__":
    main()
