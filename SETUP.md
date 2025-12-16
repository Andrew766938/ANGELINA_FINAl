# Настройка и запуск ППО

## Строки нарядывания

- Python 3.11+
- pip и virtualenv (или uv)
- Git

## Посажине Python

### Утвержденнесы версии
```bash
python --version  # должно вывести 3.11+
```

### Установка зависимостей (Option 1: pip)

```bash
# Естественные виртуальные окружения
python -m venv venv

# Открыть виртуальные окружения (Linux/Mac)
source venv/bin/activate

# Открыть виртуальные окружения (Windows)
venv\Scripts\activate

# Нарубить pip
pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt
```

### Установка зависимостей (Option 2: uv - Recommended)

```bash
# Первые, установите uv
pip install uv

# Установите зависимости
uv sync
```

## Конфигурирание переменных окружения

### 1. Составить .env файл

Файл `.env` на основе найти в примере `.env.example` (if available)

```bash
echo 'SECRET_KEY=your-super-secret-key-change-me' > .env
echo 'ALGORITHM=HS256' >> .env
echo 'ACCESS_TOKEN_EXPIRE_MINUTES=30' >> .env
echo 'DB_NAME=test.db' >> .env
```

### 2. Пример .env файла

```env
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_NAME=test.db
```

## Установка базы данных

### 1. Установка Alembic для миграции (если требуются)

```bash
alembic upgrade head
```

### 2. Составить таблицы в базе данных

```bash
python -c "from app.database.database import Base, engine; Base.metadata.create_all(engine)"
```

## Ноработка хамности

### Вариант 1: Поправить main.py для синскронного оператен базы данных

```python
# main.py
import asyncio
from sqlalchemy import text
from app.database.database import get_db

async def init_db():
    """Initialize database"""
    async with get_db() as session:
        # Create tables if not exist
        from app.models import FlightModel, BookingModel, UserModel
        from app.database.database import Base, engine
        await engine.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
```

## Начать ППО

### Метод 1: Прямая работа

```bash
python main.py
```

### Метод 2: Использование uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Метод 3: Производственная отавка (Linux/Mac)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Проверка наруботать

### 1. Проверка АППІ

```bash
curl http://localhost:8000/
```

Ожидание ответа: приветственное сообщение или HTML

### 2. Навигате на сайт

Открыть браузер на:
```
http://localhost:8000
```

### 3. Проверка документации Swagger

```
http://localhost:8000/docs
```

## Нерешённые проблемы

### Ошибка: ModuleNotFoundError

```bash
# Проверите, что виртуальные окружения активированы
# Открыть виртуальные окружения и включите pip install -r requirements.txt
```

### Ошибка: Port 8000 используется

```bash
# Открыть на ином порте

python main.py --port 8001

# Ор ссылкоу

uvicorn main:app --host 0.0.0.0 --port 8001
```

### Ошибка: База данных рэцирс

```bash
# Удалите старые таблицы и составьте новые
rm test.db  # Linux/Mac
rm test.db  # Windows (PowerShell): Remove-Item test.db

# Рестарт приложения
```

## Основные вебсайты

- **Приложение**: http://localhost:8000
- **Swagger документация**: http://localhost:8000/docs
- **ReDoc документация**: http://localhost:8000/redoc

## Подполючение третьих сторон
мв

### CORS (для нработы с фронтендом ис иных доменов)

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or list specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Гибернаторы

- Нажимает `Ctrl+C` для остановки приложения
- Виртуальные окружения автоматически деактивируются целовым выходом

## Поддержка

Для вопросов темсе Гитхаб иссюес
