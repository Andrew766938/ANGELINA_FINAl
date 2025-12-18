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
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.database.database import Base
from app.config import settings
from app.models.flight import FlightModel, AirportModel

app = FastAPI(
    title="Крылья онлайн - Система бронирования авиа билетов",
    description="API для системы бронирования авиа билетов",
    version="1.0.0"
)

# ============== АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ БД ==============

async def init_database():
    """🗄️ Автоматическая инициализация БД тестовыми данными"""
    try:
        print("\n🗄️  Проверка БД...")
        
        engine = create_async_engine(
            settings.get_db_url,
            echo=False,
        )
        
        # Проверим есть ли таблицы
        async with engine.begin() as conn:
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ))
            tables = [row[0] for row in result.fetchall()]
        
        if not tables:
            print("🔴 Таблицы не найдены. Создаю...")
            
            # Создаем таблицы
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            print("✅ Таблицы созданы")
            
            # Загружаем тестовые аэропорты
            print("🌱 Загружаю тестовые данные...")
            
            async_session = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            
            async with async_session() as session:
                airports = [
                    AirportModel(
                        code='MOW',
                        name='Шереметьево',
                        city='Москва',
                        country='Россия'
                    ),
                    AirportModel(
                        code='SPB',
                        name='Пулково',
                        city='Санкт-Петербург',
                        country='Россия'
                    ),
                    AirportModel(
                        code='KZN',
                        name='Казань',
                        city='Казань',
                        country='Россия'
                    ),
                    AirportModel(
                        code='SVX',
                        name='Кольцово',
                        city='Екатеринбург',
                        country='Россия'
                    ),
                    AirportModel(
                        code='YKA',
                        name='Площадь Ленина',
                        city='Якутск',
                        country='Россия'
                    ),
                ]
                
                session.add_all(airports)
                await session.commit()
            
            print(f"✅ Загружено {len(airports)} тестовых аэропортов")
        else:
            print(f"✅ БД уже инициализирована ({len(tables)} таблиц)")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"⚠️  Ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()


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
    
    # Инициализируем БД
    await init_database()
    
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
