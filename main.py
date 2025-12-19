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
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from app.database.base import Base
from app.database.database import register_models
from app.config import settings
from app.models.flight import FlightModel, AirportModel
from datetime import datetime

# 🔥 Обязательно регистрируем модели сразу после импорта
register_models()

app = FastAPI(
    title="Крылья онлайн - Система бронирования авиа билетов",
    description="API для системы бронирования авиа билетов",
    version="1.0.0"
)

# ============== АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ БД ==============

def init_database_sync():
    """🗄️  синхронная инициализация БД (работает для SQLite)"""
    try:
        print("\n🗄️  Проверка БД...")
        
        # Конвертируем async URL в sync для сохранения таблиц
        db_url = settings.get_db_url
        sync_db_url = db_url.replace('sqlite+aiosqlite:///', 'sqlite:///')
        
        sync_engine = create_engine(sync_db_url, echo=False)
        
        # Проверим есть ли таблицы
        with sync_engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ))
            tables = [row[0] for row in result.fetchall()]
        
        if not tables:
            print("🔴 Таблицы не найдены. Создаю...")
            
            # Создаем все таблицы массово
            Base.metadata.create_all(sync_engine)
            print("✅ Таблицы созданы")
            
            # Загружаем тестовые данные
            print("🌱 Загружаю тестовые данные...")
            
            SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
            db = SessionLocal()
            
            try:
                # Проверь не загружены ли уже данные
                existing = db.execute(text("SELECT COUNT(*) FROM airports")).scalar()
                if existing > 0:
                    print("ℹ️  Тестовые аэропорты уже загружены")
                    return
                
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
                
                db.add_all(airports)
                db.flush()
                db.commit()
                print(f"✅ Загружено {len(airports)} тестовых аэропортов")
                
                # Создаем тестовые рейсы
                print("✈️  Создаю тестовые рейсы...")
                
                flights = [
                    FlightModel(
                        flight_number='SU-001',
                        airline='Аэрофлот',
                        departure_airport_id=1,
                        arrival_airport_id=2,
                        departure_time=datetime(2025, 12, 25, 10, 0),
                        arrival_time=datetime(2025, 12, 25, 12, 0),
                        total_seats=180,
                        available_seats=180,
                        price=5500.0
                    ),
                    FlightModel(
                        flight_number='SU-002',
                        airline='Аэрофлот',
                        departure_airport_id=2,
                        arrival_airport_id=1,
                        departure_time=datetime(2025, 12, 25, 14, 0),
                        arrival_time=datetime(2025, 12, 25, 16, 0),
                        total_seats=180,
                        available_seats=180,
                        price=5500.0
                    ),
                    FlightModel(
                        flight_number='U6-100',
                        airline='Уральские авиалинии',
                        departure_airport_id=1,
                        arrival_airport_id=3,
                        departure_time=datetime(2025, 12, 26, 8, 0),
                        arrival_time=datetime(2025, 12, 26, 11, 30),
                        total_seats=150,
                        available_seats=150,
                        price=4800.0
                    ),
                    FlightModel(
                        flight_number='UT-50',
                        airline='Ют-Аэр',
                        departure_airport_id=3,
                        arrival_airport_id=4,
                        departure_time=datetime(2025, 12, 26, 18, 0),
                        arrival_time=datetime(2025, 12, 27, 2, 30),
                        total_seats=160,
                        available_seats=160,
                        price=6200.0
                    ),
                    FlightModel(
                        flight_number='S7-500',
                        airline='S7 Авиалинии',
                        departure_airport_id=2,
                        arrival_airport_id=4,
                        departure_time=datetime(2025, 12, 27, 9, 0),
                        arrival_time=datetime(2025, 12, 27, 15, 0),
                        total_seats=120,
                        available_seats=120,
                        price=7200.0
                    ),
                    FlightModel(
                        flight_number='SU-003',
                        airline='Аэрофлот',
                        departure_airport_id=1,
                        arrival_airport_id=5,
                        departure_time=datetime(2025, 12, 28, 7, 0),
                        arrival_time=datetime(2025, 12, 28, 17, 30),
                        total_seats=200,
                        available_seats=200,
                        price=8500.0
                    ),
                ]
                
                db.add_all(flights)
                db.flush()
                db.commit()
                print(f"✅ Загружено {len(flights)} тестовых рейсов")
                
            finally:
                db.close()
        else:
            print(f"✅ БД уже инициализирована ({len(tables)} таблиц)")
        
        sync_engine.dispose()
        
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
    
    # Инициализируем БД (SYNC - НРОВЕРГО для SQLite)
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
