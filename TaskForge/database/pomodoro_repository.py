
from database.database import get_connection
from datetime import datetime, timedelta


# =====================================
# CREATE SESSION
# =====================================

def add_completed_session(
    task_id,
    task_title,
    started_at,
    completed_at,
    duration_seconds
):
    """
    Save a completed focus session.
    """

    if not task_title or not task_title.strip():
        raise ValueError("Task title cannot be empty")

    if not isinstance(duration_seconds, int) or duration_seconds <= 0:
        raise ValueError("Duration must be a positive integer")

    if not started_at or not completed_at:
        raise ValueError("Session timestamps cannot be empty")

    with get_connection() as conn:

        cursor = conn.execute("""
            INSERT INTO pomodoro_sessions (
                task_id,
                task_title,
                started_at,
                completed_at,
                duration_seconds
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            task_id,
            task_title.strip(),
            started_at,
            completed_at,
            duration_seconds
        ))

        return cursor.lastrowid


# =====================================
# GET ALL SESSIONS
# =====================================

def get_all_sessions(limit=None):
    """
    Return all completed sessions.
    Newest sessions first.
    """

    query = """
        SELECT
            id,
            task_id,
            task_title,
            started_at,
            completed_at,
            duration_seconds
        FROM pomodoro_sessions
        ORDER BY completed_at DESC, id DESC
    """

    with get_connection() as conn:

        if limit is not None:

            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("Limit must be positive")

            query += " LIMIT ?"

            cursor = conn.execute(query, (limit,))

        else:
            cursor = conn.execute(query)

        return cursor.fetchall()


# =====================================
# GET SESSION BY ID
# =====================================

def get_session_by_id(session_id):

    with get_connection() as conn:

        cursor = conn.execute("""
            SELECT
                id,
                task_id,
                task_title,
                started_at,
                completed_at,
                duration_seconds
            FROM pomodoro_sessions
            WHERE id = ?
        """, (session_id,))

        return cursor.fetchone()


# =====================================
# GET SESSIONS FOR TASK
# =====================================

def get_sessions_for_task(task_id):
    """
    Return all sessions associated with a task.
    """

    with get_connection() as conn:

        cursor = conn.execute("""
            SELECT
                id,
                task_id,
                task_title,
                started_at,
                completed_at,
                duration_seconds
            FROM pomodoro_sessions
            WHERE task_id = ?
            ORDER BY completed_at DESC
        """, (task_id,))

        return cursor.fetchall()


# =====================================
# SESSION STATISTICS
# =====================================


def get_session_stats():
    """
    Return overall focus statistics.
    """

    with get_connection() as conn:

        cursor = conn.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(duration_seconds), 0),
                COALESCE(AVG(duration_seconds), 0)
            FROM pomodoro_sessions
        """)

        row = cursor.fetchone()

        total_sessions = row[0]
        total_seconds = row[1]
        average_seconds = row[2]

        return {
            "total_sessions": total_sessions,
            "total_seconds": total_seconds,
            "total_minutes": round(total_seconds / 60, 1),
            "average_seconds": round(average_seconds, 1)
        }



# =====================================
# DELETE SESSION
# =====================================

def delete_session(session_id):

    with get_connection() as conn:

        cursor = conn.execute("""
            DELETE FROM pomodoro_sessions
            WHERE id = ?
        """, (session_id,))

        return cursor.rowcount > 0


# =====================================
# DAILY FOCUS STATISTICS
# =====================================

def get_daily_focus_stats(days=7):
    """
    Return focus statistics for the last N calendar days.

    Sessions are grouped by their local completion date.
    """

    if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
        raise ValueError("Days must be a positive integer")

    today = datetime.now().astimezone().date()
    start_day = today - timedelta(days=days - 1)

    # Prepare empty statistics for every day
    daily_stats = {}

    for i in range(days):
        current_day = start_day + timedelta(days=i)

        daily_stats[current_day] = {
            "date": current_day.isoformat(),
            "sessions": 0,
            "duration_seconds": 0
        }

    sessions = get_all_sessions()

    for session in sessions:

        completed_at = datetime.fromisoformat(session[4])

        if completed_at.tzinfo is not None:
            completed_at = completed_at.astimezone()

        session_day = completed_at.date()

        if session_day in daily_stats:
            daily_stats[session_day]["sessions"] += 1
            daily_stats[session_day]["duration_seconds"] += session[5]

    return [
        daily_stats[day]
        for day in sorted(daily_stats)
    ]


# =====================================
# TASK FOCUS STATISTICS
# =====================================

def get_task_focus_stats(limit=None):
    """
    Return total focus time grouped by task.
    """

    if limit is not None:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("Limit must be a positive integer")

    sessions = get_all_sessions()

    task_stats = {}

    for session in sessions:

        task_id = session[1]
        task_title = session[2]
        duration = session[5]

        # Keep deleted tasks in history as separate entries by title
        key = (task_id, task_title)

        if key not in task_stats:
            task_stats[key] = {
                "task_id": task_id,
                "task_title": task_title,
                "sessions": 0,
                "duration_seconds": 0
            }

        task_stats[key]["sessions"] += 1
        task_stats[key]["duration_seconds"] += duration

    result = list(task_stats.values())

    # Most focused tasks first
    result.sort(
        key=lambda item: (
            -item["duration_seconds"],
            item["task_title"].casefold()
        )
    )

    if limit is not None:
        result = result[:limit]

    return result


# =====================================
# DAILY FOCUS STATISTICS
# =====================================

def get_daily_focus_stats(days=7):
    """
    Return focus statistics for the last N calendar days.

    Sessions are grouped by their local completion date.
    """

    if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
        raise ValueError("Days must be a positive integer")

    today = datetime.now().astimezone().date()
    start_day = today - timedelta(days=days - 1)

    # Prepare empty statistics for every day
    daily_stats = {}

    for i in range(days):
        current_day = start_day + timedelta(days=i)

        daily_stats[current_day] = {
            "date": current_day.isoformat(),
            "sessions": 0,
            "duration_seconds": 0
        }

    sessions = get_all_sessions()

    for session in sessions:

        completed_at = datetime.fromisoformat(session[4])

        if completed_at.tzinfo is not None:
            completed_at = completed_at.astimezone()

        session_day = completed_at.date()

        if session_day in daily_stats:
            daily_stats[session_day]["sessions"] += 1
            daily_stats[session_day]["duration_seconds"] += session[5]

    return [
        daily_stats[day]
        for day in sorted(daily_stats)
    ]


# =====================================
# TASK FOCUS STATISTICS
# =====================================

def get_task_focus_stats(limit=None):
    """
    Return total focus time grouped by task.
    """

    if limit is not None:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
            raise ValueError("Limit must be a positive integer")

    sessions = get_all_sessions()

    task_stats = {}

    for session in sessions:

        task_id = session[1]
        task_title = session[2]
        duration = session[5]

        # Keep deleted tasks in history as separate entries by title
        key = (task_id, task_title)

        if key not in task_stats:
            task_stats[key] = {
                "task_id": task_id,
                "task_title": task_title,
                "sessions": 0,
                "duration_seconds": 0
            }

        task_stats[key]["sessions"] += 1
        task_stats[key]["duration_seconds"] += duration

    result = list(task_stats.values())

    # Most focused tasks first
    result.sort(
        key=lambda item: (
            -item["duration_seconds"],
            item["task_title"].casefold()
        )
    )

    if limit is not None:
        result = result[:limit]

    return result
