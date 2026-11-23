
from datetime import datetime, timedelta
import uuid

from database.database import create_db
from database.task_repository import add_task, delete_task

from database.pomodoro_repository import (
    add_completed_session,
    delete_session,
    get_daily_focus_stats,
    get_task_focus_stats,
    get_session_stats
)


def main():

    create_db()

    suffix = uuid.uuid4().hex[:6]
    task_title = f"Analytics Test {suffix}"

    # Create test task
    task_id = add_task(
        task_title,
        "Testing productivity analytics",
        8,
        8,
        5
    )

    now = datetime.now().astimezone().replace(microsecond=0)
    yesterday = now - timedelta(days=1)

    session_ids = []

    # Save two sessions for the same task
    first_session = add_completed_session(
        task_id,
        task_title,
        (now - timedelta(minutes=25)).isoformat(),
        now.isoformat(),
        1500
    )

    session_ids.append(first_session)

    second_session = add_completed_session(
        task_id,
        task_title,
        (yesterday - timedelta(minutes=10)).isoformat(),
        yesterday.isoformat(),
        600
    )

    session_ids.append(second_session)

    print("CREATE ANALYTICS DATA: PASS")

    # Test daily statistics
    daily_stats = get_daily_focus_stats(7)

    today_stats = next(
        item for item in daily_stats
        if item["date"] == now.date().isoformat()
    )

    yesterday_stats = next(
        item for item in daily_stats
        if item["date"] == yesterday.date().isoformat()
    )

    assert today_stats["sessions"] >= 1
    assert today_stats["duration_seconds"] >= 1500

    assert yesterday_stats["sessions"] >= 1
    assert yesterday_stats["duration_seconds"] >= 600

    print("DAILY FOCUS STATISTICS: PASS")

    # Test task statistics
    task_stats = get_task_focus_stats()

    result = next(
        item for item in task_stats
        if item["task_id"] == task_id
    )

    assert result["sessions"] == 2
    assert result["duration_seconds"] == 2100

    print("TASK FOCUS STATISTICS: PASS")

    # Test overall statistics
    stats = get_session_stats()

    assert stats["total_sessions"] >= 2
    assert stats["total_seconds"] >= 2100
    assert stats["average_seconds"] > 0

    print("OVERALL STATISTICS: PASS")

    # Test limit
    limited_stats = get_task_focus_stats(limit=1)

    assert len(limited_stats) <= 1

    print("TOP TASK LIMIT: PASS")

    # Clean up test data
    for session_id in session_ids:
        assert delete_session(session_id)

    assert delete_task(task_id)

    print("CLEANUP: PASS")

    print("\nALL POMODORO ANALYTICS TESTS PASSED!")


if __name__ == "__main__":
    main()
