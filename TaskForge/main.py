from database.database import create_db
from database.category_repository import (
    add_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category
)
import uuid


def main():
    create_db()
    print("Database created successfully!")


    test_name = f"Test Category {uuid.uuid4().hex[:6]}"

    result = add_category(test_name, "#3498db")
    print("ADD:", result)
    assert result is True

    categories = get_all_categories()
    print("ALL CATEGORIES:", categories)

    assert any(category[1] == test_name for category in categories)

    category = next(
        category for category in categories
        if category[1] == test_name
    )

    category_id = category[0]

    result = get_category_by_id(category_id)
    print("GET BY ID:", result)

    assert result is not None

    updated_name = f"Updated Category {uuid.uuid4().hex[:6]}"

    result = update_category(
        category_id,
        updated_name,
        "#e74c3c"
    )


    print("UPDATE:", result)
    assert result is True

    updated_category = get_category_by_id(category_id)
    print("UPDATED CATEGORY:", updated_category)

    assert updated_category[1] == updated_name


    result = delete_category(category_id)

    print("DELETE:", result)
    assert result is True

    deleted_category = get_category_by_id(category_id)

    print("AFTER DELETE:", deleted_category)
    assert deleted_category is None

    print("\nALL CATEGORY TESTS PASSED!")


if __name__ == "__main__":
    main()
