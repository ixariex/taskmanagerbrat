# TaskForge — восстановленная версия

Восстановлены функции, которые были реализованы в ходе разработки:

- SQLite: таблицы `tasks` и `categories`, миграция старой БД и внешний ключ `category_id`.
- Category Repository: создание, чтение, обновление и удаление категорий.
- Task Repository: создание, чтение, обновление и удаление задач, дедлайны, статусы и назначение категорий.
- Task Manager: бизнес-логика создания, получения, редактирования, завершения и удаления задач.
- PyQt6: Dashboard, Sidebar, My Tasks, Categories, Completed, форма Add Task, Edit Selected и Delete Selected.

## Запуск на Windows с uv

Открой терминал в этой папке (рядом с `pyproject.toml`) и выполни:

```powershell
uv sync
uv run python app.py
```

Если используешь обычный Python/venv:

```powershell
python -m pip install -r requirements.txt
python app.py
```

## Тесты

```powershell
uv run python testtasks.py
uv run python testtask_manager.py
```

Тестовые записи получают уникальные названия и по возможности удаляются после завершения теста.

## Структура

```text
TaskForge/
├── app.py
├── core/
│   └── task_manager.py
├── database/
│   ├── database.py
│   ├── category_repository.py
│   └── task_repository.py
├── ui/
│   ├── main_window.py
│   └── task_dialog.py
├── testtasks.py
├── testtask_manager.py
├── pyproject.toml
└── requirements.txt
```

## Где хранится база

При первом запуске SQLite-файл автоматически создаётся здесь:

`database/data/taskforge.db`

Не удаляй этот файл, если хочешь сохранить созданные задачи и категории.

## Примечание по C++

C++-модуль `TaskOptimizer` не включён: по переписке его должен отдельно разрабатывать второй участник команды. Python-часть подготовлена для последующего подключения, но `pybind11`-интеграция ещё не реализована.
