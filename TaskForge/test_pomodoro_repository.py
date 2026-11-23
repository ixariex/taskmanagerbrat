
from datetime import datetime, timedelta
import uuid

from database.database import create_db

from database.task_repository import (
    add_task,
    delete_task
)

from database.pomodoro_repository import (
    add_completed_session,
    get_all_sessions,
    get_session_by_id,
    get_sessions_for_task,
    get_session_stats,
    delete_session
)


def main():

    create_db()

    suffix = uuid.uuid4().hex[:6]
    task_title = f"Pomodoro Test {suffix}"

    # 1. Create test task
    task_id = add_task(
        task_title,
        "Testing Pomodoro history",
        5,
        5,
        5
    )

    print("CREATE TEST TASK: PASS")

    # 2. Prepare timestamps
    completed_at = datetime.now().astimezone()
    started_at = completed_at - timedelta(minutes=25)

    # 3. Save previous statistics
    stats_before = get_session_stats()

    # 4. Save completed session
    session_id = add_completed_session(
        task_id=task_id,
        task_title=task_title,
        started_at=started_at.isoformat(timespec="seconds"),
        completed_at=completed_at.isoformat(timespec="seconds"),
        duration_seconds=1500
    )

    assert session_id is not None

    print("SAVE SESSION: PASS")

    # 5. Get session by ID
    session = get_session_by_id(session_id)

    assert session is not None
    assert session[1] == task_id
    assert session[2] == task_title
    assert session[5] == 1500

    print("GET SESSION BY ID: PASS")

    # 6. Get all sessions
    sessions = get_all_sessions()

    assert any(row[0] == session_id for row in sessions)

    print("GET ALL SESSIONS: PASS")

    # 7. Get sessions for task
    task_sessions = get_sessions_for_task(task_id)

    assert any(row[0] == session_id for row in task_sessions)

    print("GET SESSIONS FOR TASK: PASS")

    # 8. Check statistics
    stats_after = get_session_stats()

    assert stats_after["total_sessions"] == (
        stats_before["total_sessions"] + 1
    )

    assert stats_after["total_seconds"] == (
        stats_before["total_seconds"] + 1500
    )

    print("SESSION STATISTICS: PASS")

    # 9. Delete task
    result = delete_task(task_id)

    assert result is True

    print("DELETE TASK: PASS")

    # 10. Check history preservation
    session = get_session_by_id(session_id)

    assert session is not None
    assert session[1] is None
    assert session[2] == task_title

    print("PRESERVE HISTORY: PASS")

    # 11. Clean up test session
    result = delete_session(session_id)

    assert result is True
    assert get_session_by_id(session_id) is None

    print("DELETE SESSION: PASS")

    print("\nALL POMODORO REPOSITORY TESTS PASSED!")


if __name__ == "__main__":
    main()
