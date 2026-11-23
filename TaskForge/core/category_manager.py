

from database.category_repository import (
    add_category,
    delete_category,
    get_all_categories,
    get_category_by_id,
    update_category,
)


def create_category(name: str, color: str = "#3498db") -> bool:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Category name cannot be empty")
    if not isinstance(color, str) or not color.startswith("#") or len(color) != 7:
        raise ValueError("Category color must be a hex value such as #3498db")
    return add_category(name.strip(), color.lower())


def get_categories() -> list[tuple]:
    return get_all_categories()


def get_category(category_id: int):
    return get_category_by_id(category_id)


def edit_category(category_id: int, name: str, color: str) -> bool:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Category name cannot be empty")
    if not isinstance(color, str) or not color.startswith("#") or len(color) != 7:
        raise ValueError("Category color must be a hex value such as #3498db")
    return update_category(category_id, name.strip(), color.lower())


def remove_category(category_id: int) -> bool:
    # The database uses ON DELETE SET NULL, so tasks are kept and unlinked.
    return delete_category(category_id)
