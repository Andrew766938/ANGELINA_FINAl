# 🔧 Исправление Циклического Импорта

## Проблема

```
ImportError: cannot import name 'Base' from partially initialized module 'app.database.database'
```

### Почему это происходит:

```
app/database/database.py
    ↓
    от app.models.users import UserModel
    ↓
    app/models/__init__.py (НАЛИЧНО импортировал ВСЕ модели!)
    ↓
    ты импортируешь Base из database.py
    ↓
    database.py ещё не закончился!
    ↓
💥 Циклический импорт!
```

## Решение

### Шаг 1: Обновить код

```bash
git pull origin master
```

### Шаг 2: Очистить кэш

Команда `python3.13` может использовать `pycache`:

```bash
# Windows
rd /s /q __pycache__ app/__pycache__ app/api/__pycache__ app/database/__pycache__ app/models/__pycache__ migrations/__pycache__

# Mac/Linux
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Шаг 3: Удалить старую БД (опционально)

```bash
rm test.db
```

### Шаг 4: Запустить

```bash
uvicorn main:app --reload
```

## ✅ Ожидаемые выводы

```
╯───────────────────────────────────────╮
╰───────── 💣 Крылья онлайн стартует... 💣 ─────────╯

🗄️  Проверка БД...
🔴 Таблицы не найдены. Создаю...
✅ Таблицы созданы
🌱 Загружаю тестовые данные...
✅ Загружено 5 тестовых аэропортов
✅ Приложение готово!

INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Проверка

### Тест API

```bash
# В новом терминале (в пока первый работает):

curl http://localhost:8000/flights/

# Ожидаемо
# [{"id": 1, "flight_number": "...", ...}, ...]
```

### Браузер

Open: `http://localhost:8000`

Все кнопки должны работать! ✅

## Не помогло?

### Опция 1: Полная очистка

```bash
# 1. Остановить uvicorn (Ctrl+C)

# 2. Очистить всё

# Windows
rd /s /q .venv

# Mac/Linux
rm -rf .venv

# 3. Переустановить
uv sync

# 4. Запустить
uvicorn main:app --reload
```

### Опция 2: Новый IDE/Terminal

Поновите IDE чтобы релоадили импорты.

## ✨ Готово!

Теперь циклические импорты исправлены! 🎉
