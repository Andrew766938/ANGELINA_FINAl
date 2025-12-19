import uvicorn
import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.api.sample import router as sample_router
from app.api.auth import router as auth_router
from app.api.roles import router as role_router
from app.api.flights import router as flights_router
from app.api.bookings import router as bookings_router
from app.admin import setup_admin
from app.database.base import Base
from app.database.database import register_models
from app.database.init_db import init_database_sync

# 🔥 Обязательно регистрируем модели сразу после импорта
register_models()

app = FastAPI(
    title="Крылья онлайн - Система бронирования авиа билетов",
    description="API для системы бронирования авиа билетов",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """🚀 Обработчик стартупа приложения"""
    print("""
╯───────────────────────────────────────╮
╰───────── 💣 Крылья онлайн стартует... 💣 ─────────╯
    """)
    
    # Отбрасываем все выводы в выходном канале (flush stdout)
    import sys
    sys.stdout.flush()
    
    # Инициализируем БД (SYNC - для SQLite)
    init_database_sync()
    
    print("✅ Приложение готово!\n")


# ============== CORS CONFIGURATION ==============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники для разработки
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Подключаем все роутеры
app.include_router(sample_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(flights_router)
app.include_router(bookings_router)

# ============== SQLADMIN SETUP ==============
try:
    setup_admin(app)
    print("✅ SQLAdmin админ-панель подключена на /admin")
except Exception as e:
    print(f"⚠️  Ошибка при подключении SQLAdmin: {e}")

# Монтируем статические файлы
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Маршрут для главной страницы
@app.get("/")
async def read_root():
    index_path = Path(__file__).parent / "templates" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Крылья онлайн - Добро пожаловать!"}

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
