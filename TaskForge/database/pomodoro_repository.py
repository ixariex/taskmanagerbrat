
from database.database import get_connection


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
    Return total sessions and focus time.
    """

    with get_connection() as conn:

        cursor = conn.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(duration_seconds), 0)
            FROM pomodoro_sessions
        """)

        row = cursor.fetchone()

        total_sessions = row[0]
        total_seconds = row[1]

        return {
            "total_sessions": total_sessions,
            "total_seconds": total_seconds,
            "total_minutes": round(total_seconds / 60, 1)
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
