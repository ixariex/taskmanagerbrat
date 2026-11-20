"""CRUD operations for task categories."""

import sqlite3
from typing import Optional

from database.database import get_connection


def add_category(name: str, color: str = "#3498db") -> bool:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Category name cannot be empty")

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO categories (name, color) VALUES (?, ?)",
                (name.strip(), color or "#3498db"),
            )
        return True
    except sqlite3.IntegrityError:
        # A category with this name already exists.
        return False


def get_all_categories() -> list[tuple]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, name, color FROM categories ORDER BY name COLLATE NOCASE"
        )
        return cursor.fetchall()


def get_category_by_id(category_id: int) -> Optional[tuple]:
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, name, color FROM categories WHERE id = ?",
            (category_id,),
        )
        return cursor.fetchone()


def update_category(
    category_id: int, name: str, color: Optional[str] = None
) -> bool:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Category name cannot be empty")

    try:
        with get_connection() as conn:
            if color is not None:
                cursor = conn.execute(
                    "UPDATE categories SET name = ?, color = ? WHERE id = ?",
                    (name.strip(), color, category_id),
                )
            else:
                cursor = conn.execute(
                    "UPDATE categories SET name = ? WHERE id = ?",
                    (name.strip(), category_id),
                )
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        return False


def delete_category(category_id: int) -> bool:
    """Delete a category; linked tasks remain and get category_id=NULL."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM categories WHERE id = ?",
            (category_id,),
        )
        return cursor.rowcount > 0
