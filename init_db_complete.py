"""Complete database initialization with 15+ items each"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.models.flight import AirportModel, FlightModel
from app.models.booking import BookingModel, BookingStatus
from app.models.users import UserModel
from app.models.roles import RoleModel


async def init_db():
    """Initialize database with complete sample data"""
    
    engine = create_async_engine("sqlite+aiosqlite:///test.db", echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if data already exists
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM airports"))
            count = result.scalar()
            if count > 0:
                print("✅ Database already has sample data")
                await engine.dispose()
                return
        except:
            pass
        
        # Create roles
        user_role = RoleModel(name="user")
        admin_role = RoleModel(name="admin")
        session.add(user_role)
        session.add(admin_role)
        await session.flush()
        
        # Create 16 airports
        airports = [
            AirportModel(code="MOW", name="Шереметьево", city="Москва", country="Россия"),
            AirportModel(code="SPB", name="Пулково", city="Санкт-Петербург", country="Россия"),
            AirportModel(code="KZN", name="Казань", city="Казань", country="Россия"),
            AirportModel(code="SVX", name="Кольцово", city="Екатеринбург", country="Россия"),
            AirportModel(code="YKA", name="Площадь Ленина", city="Якутск", country="Россия"),
            AirportModel(code="LED", name="Пулково-2", city="Санкт-Петербург", country="Россия"),
            AirportModel(code="NOV", name="Новосибирск", city="Новосибирск", country="Россия"),
            AirportModel(code="VVO", name="Новый Владивосток", city="Владивосток", country="Россия"),
            AirportModel(code="OVB", name="Объ", city="Обь", country="Россия"),
            AirportModel(code="UUS", name="Южносахалинск", city="Южносахалинск", country="Россия"),
            AirportModel(code="TOE", name="Толяти", city="Толяти", country="Россия"),
            AirportModel(code="PEE", name="Пермь", city="Пермь", country="Россия"),
            AirportModel(code="TJM", name="Тюмень", city="Тюмень", country="Россия"),
            AirportModel(code="IGT", name="Иркутск", city="Иркутск", country="Россия"),
            AirportModel(code="ULY", name="Улан-Удэ", city="Улан-Удэ", country="Россия"),
            AirportModel(code="CHI", name="Чита", city="Чита", country="Россия"),
        ]
        
        session.add_all(airports)
        await session.flush()
        
        # Create 16 flights
        base_time = datetime.now() + timedelta(days=1)
        flights = [
            FlightModel(flight_number="SU-001", airline="Аэрофлот", departure_airport_id=1, arrival_airport_id=2, departure_time=base_time.replace(hour=8, minute=0), arrival_time=base_time.replace(hour=10, minute=0), total_seats=180, available_seats=180, price=5500),
            FlightModel(flight_number="SU-002", airline="Аэрофлот", departure_airport_id=2, arrival_airport_id=1, departure_time=base_time.replace(hour=12, minute=0), arrival_time=base_time.replace(hour=14, minute=0), total_seats=180, available_seats=145, price=5500),
            FlightModel(flight_number="U6-100", airline="Уральские авиалинии", departure_airport_id=1, arrival_airport_id=3, departure_time=base_time.replace(hour=10, minute=30), arrival_time=base_time.replace(hour=13, minute=30), total_seats=150, available_seats=150, price=4800),
            FlightModel(flight_number="UT-50", airline="Ют-Аэр", departure_airport_id=3, arrival_airport_id=4, departure_time=base_time.replace(hour=14, minute=0), arrival_time=base_time.replace(hour=17, minute=30), total_seats=160, available_seats=160, price=6200),
            FlightModel(flight_number="S7-500", airline="S7 Авиалинии", departure_airport_id=2, arrival_airport_id=4, departure_time=base_time.replace(hour=9, minute=0), arrival_time=base_time.replace(hour=12, minute=30), total_seats=120, available_seats=120, price=7200),
            FlightModel(flight_number="SU-003", airline="Аэрофлот", departure_airport_id=1, arrival_airport_id=5, departure_time=base_time.replace(hour=15, minute=0), arrival_time=base_time.replace(hour=19, minute=0), total_seats=200, available_seats=200, price=8500),
            FlightModel(flight_number="FV-201", airline="Финир аэро", departure_airport_id=4, arrival_airport_id=2, departure_time=base_time.replace(hour=11, minute=0), arrival_time=base_time.replace(hour=14, minute=0), total_seats=140, available_seats=140, price=6800),
            FlightModel(flight_number="A4-400", airline="A4", departure_airport_id=1, arrival_airport_id=6, departure_time=base_time.replace(hour=7, minute=0), arrival_time=base_time.replace(hour=9, minute=30), total_seats=190, available_seats=190, price=5200),
            FlightModel(flight_number="R2-102", airline="Русские авиалинии", departure_airport_id=2, arrival_airport_id=3, departure_time=base_time.replace(hour=13, minute=0), arrival_time=base_time.replace(hour=15, minute=0), total_seats=170, available_seats=170, price=5800),
            FlightModel(flight_number="FP-55", airline="Фламинго", departure_airport_id=3, arrival_airport_id=1, departure_time=base_time.replace(hour=16, minute=0), arrival_time=base_time.replace(hour=18, minute=0), total_seats=160, available_seats=160, price=5400),
            FlightModel(flight_number="N1-555", airline="Новые века", departure_airport_id=1, arrival_airport_id=7, departure_time=base_time.replace(hour=6, minute=0), arrival_time=base_time.replace(hour=9, minute=30), total_seats=210, available_seats=210, price=7800),
            FlightModel(flight_number="V1-888", airline="Высота", departure_airport_id=2, arrival_airport_id=8, departure_time=base_time.replace(hour=10, minute=0), arrival_time=base_time.replace(hour=13, minute=0), total_seats=140, available_seats=140, price=8200),
            FlightModel(flight_number="E3-200", airline="Экспресс", departure_airport_id=1, arrival_airport_id=4, departure_time=base_time.replace(hour=18, minute=0), arrival_time=base_time.replace(hour=21, minute=0), total_seats=150, available_seats=150, price=6500),
            FlightModel(flight_number="G5-777", airline="Галактика", departure_airport_id=3, arrival_airport_id=2, departure_time=base_time.replace(hour=14, minute=30), arrival_time=base_time.replace(hour=16, minute=30), total_seats=180, available_seats=180, price=5700),
            FlightModel(flight_number="T4-999", airline="Тандем", departure_airport_id=4, arrival_airport_id=3, departure_time=base_time.replace(hour=19, minute=0), arrival_time=base_time.replace(hour=20, minute=30), total_seats=120, available_seats=120, price=4200),
            FlightModel(flight_number="L7-333", airline="Луч", departure_airport_id=1, arrival_airport_id=9, departure_time=base_time.replace(hour=5, minute=0), arrival_time=base_time.replace(hour=8, minute=0), total_seats=200, available_seats=200, price=9200),
        ]
        
        session.add_all(flights)
        await session.flush()
        
        # Create demo users (user and admin)
        demo_user = UserModel(name="Демо Пользователь", email="demo@example.com", hashed_password="demo123", role_id=user_role.id)
        demo_admin = UserModel(name="Админ", email="admin@example.com", hashed_password="admin123", role_id=admin_role.id)
        session.add(demo_user)
        session.add(demo_admin)
        await session.flush()
        
        # Create 16 bookings (tickets)
        bookings = [
            BookingModel(booking_number="BK-001", user_id=demo_user.id, flight_id=1, passenger_name="Иван Петров", passenger_email="ivan@example.com", passenger_phone="+7-999-111-0001", seats_count=1, total_price=5500, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-002", user_id=demo_user.id, flight_id=2, passenger_name="Мария Сидорова", passenger_email="maria@example.com", passenger_phone="+7-999-222-0002", seats_count=2, total_price=11000, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-003", user_id=demo_user.id, flight_id=3, passenger_name="Алексей Иванов", passenger_email="alex@example.com", passenger_phone="+7-999-333-0003", seats_count=1, total_price=4800, status=BookingStatus.COMPLETED),
            BookingModel(booking_number="BK-004", user_id=demo_user.id, flight_id=4, passenger_name="Елена Смирнова", passenger_email="elena@example.com", passenger_phone="+7-999-444-0004", seats_count=1, total_price=6200, status=BookingStatus.PENDING),
            BookingModel(booking_number="BK-005", user_id=demo_user.id, flight_id=5, passenger_name="Сергей Федоров", passenger_email="sergey@example.com", passenger_phone="+7-999-555-0005", seats_count=1, total_price=7200, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-006", user_id=demo_user.id, flight_id=6, passenger_name="Ольга Новикова", passenger_email="olga@example.com", passenger_phone="+7-999-666-0006", seats_count=3, total_price=25500, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-007", user_id=demo_user.id, flight_id=7, passenger_name="Виктор Козлов", passenger_email="victor@example.com", passenger_phone="+7-999-777-0007", seats_count=1, total_price=6800, status=BookingStatus.COMPLETED),
            BookingModel(booking_number="BK-008", user_id=demo_user.id, flight_id=8, passenger_name="Екатерина Волкова", passenger_email="kate@example.com", passenger_phone="+7-999-888-0008", seats_count=1, total_price=5200, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-009", user_id=demo_user.id, flight_id=9, passenger_name="Максим Соколов", passenger_email="max@example.com", passenger_phone="+7-999-900-0009", seats_count=2, total_price=11600, status=BookingStatus.PENDING),
            BookingModel(booking_number="BK-010", user_id=demo_user.id, flight_id=10, passenger_name="Наталья Степанова", passenger_email="nata@example.com", passenger_phone="+7-999-101-0010", seats_count=1, total_price=5400, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-011", user_id=demo_user.id, flight_id=11, passenger_name="Павел Морозов", passenger_email="pavel@example.com", passenger_phone="+7-999-202-0011", seats_count=1, total_price=7800, status=BookingStatus.COMPLETED),
            BookingModel(booking_number="BK-012", user_id=demo_user.id, flight_id=12, passenger_name="Анна Буланова", passenger_email="anna@example.com", passenger_phone="+7-999-303-0012", seats_count=1, total_price=8200, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-013", user_id=demo_user.id, flight_id=13, passenger_name="Дмитрий Петров", passenger_email="dmitry@example.com", passenger_phone="+7-999-404-0013", seats_count=1, total_price=6500, status=BookingStatus.PENDING),
            BookingModel(booking_number="BK-014", user_id=demo_user.id, flight_id=14, passenger_name="Валентина Соловьева", passenger_email="val@example.com", passenger_phone="+7-999-505-0014", seats_count=2, total_price=11400, status=BookingStatus.CONFIRMED),
            BookingModel(booking_number="BK-015", user_id=demo_user.id, flight_id=15, passenger_name="Руслан Кузнецов", passenger_email="ruslan@example.com", passenger_phone="+7-999-606-0015", seats_count=1, total_price=4200, status=BookingStatus.COMPLETED),
            BookingModel(booking_number="BK-016", user_id=demo_user.id, flight_id=16, passenger_name="Людмила Волохова", passenger_email="lyuda@example.com", passenger_phone="+7-999-707-0016", seats_count=1, total_price=9200, status=BookingStatus.CONFIRMED),
        ]
        
        session.add_all(bookings)
        await session.commit()
        
        print("✅ Database initialized!")
        print(f"  - 16 airports created")
        print(f"  - 16 flights created")
        print(f"  - 16 bookings (tickets) created")
        print(f"  - Demo user created (demo@example.com / demo123)")
        print(f"  - Demo admin created (admin@example.com / admin123)")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Initializing database with complete data...")
    asyncio.run(init_db())
    print("✅ Done!")