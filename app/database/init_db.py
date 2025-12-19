"""
🗄️  Модуль инициализации базы данных
Загружает тестовые аэропорты и рейсы при первом запуске
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.database.base import Base
from app.config import settings
from app.models.flight import FlightModel, AirportModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def init_database_sync():
    """
    🗄️  Синхронная инициализация БД (работает для SQLite)
    Создает таблицы и гарантирует наличие тестовых данных
    """
    try:
        print("\n🗄️  Проверка БД...")
        
        # Конвертируем async URL в sync для создания таблиц
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
            # Создаем все таблицы
            Base.metadata.create_all(sync_engine)
            print("✅ Таблицы созданы")
        else:
            print(f"✅ БД уже инициализирована ({len(tables)} таблиц)")
        
        # Загружаем тестовые данные (ВсЕГДА, если них нет!)
        print("🌱 Проверяю тестовые данные...")
        
        SessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)
        db = SessionLocal()
        
        try:
            # Проверяем и очищаем если нужно
            
            # Проверяем аэропорты
            airports_count = db.execute(text("SELECT COUNT(*) FROM airports")).scalar()
            if airports_count == 0:
                print("🔴 Аэропорты отсутствуют. Создаю...")
                
                # Создаем аэропорты
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
            else:
                print(f"✅ Аэропорты уже есть ({airports_count} шт)")
            
            # Проверяем рейсы
            flights_count = db.execute(text("SELECT COUNT(*) FROM flights")).scalar()
            if flights_count == 0:
                print("🔴 Рейсы отсутствуют. Создаю...")
                
                # Создаем рейсы
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
            else:
                print(f"✅ Рейсы уже есть ({flights_count} шт)")
                
        finally:
            db.close()
        
        sync_engine.dispose()
        
    except Exception as e:
        print(f"⚠️  Ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()
