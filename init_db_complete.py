"""Complete database initialization with 15+ items each"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.models.flight import AirportModel, FlightModel


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
        
        # Create 15+ airports
        airports = [
            AirportModel(code="MOW", name="Шереметьево", city="Москва", country="Россия"),
            AirportModel(code="SPB", name="Пулково", city="Санкт-Петербург", country="Россия"),
            AirportModel(code="KZN", name="Казань", city="Казань", country="Россия"),
            AirportModel(code="SVX", name="Кольцово", city="Екатеринбург", country="Россия"),
            AirportModel(code="YKA", name="Площадь ленина", city="Якутск", country="Россия"),
            AirportModel(code="LED", name="Пулково-2", city="Санкт-Петербург", country="Россия"),
            AirportModel(code="NOV", name="Новосибирск", city="Новосибирск", country="Россия"),
            AirportModel(code="VVO", name="новый владивосток", city="Владивосток", country="Россия"),
            AirportModel(code="OVB", name="Обь телутинские", city="Обь", country="Россия"),
            AirportModel(code="UUS", name="uюжно-сахалинск", city="uюжно-сахалинск", country="Россия"),
            AirportModel(code="TOE", name="тольятти", city="тольятти", country="Россия"),
            AirportModel(code="PEE", name="u043fермь", city="u043fермь", country="Россия"),
            AirportModel(code="TJM", name="u0442юмень", city="u0442юмень", country="Россия"),
            AirportModel(code="IGT", name="u0438ркутск", city="u0438ркутск", country="Россия"),
            AirportModel(code="ULY", name="u0443лян-u0443дэ", city="u0423лан-u0423дэ", country="Россия"),
            AirportModel(code="CHI", name="u0447ита", city="u0427ита", country="Россия"),
        ]
        
        session.add_all(airports)
        await session.flush()
        
        # Create 15+ flights
        base_time = datetime.now() + timedelta(days=1)
        flights = [
            FlightModel(flight_number="SU-001", airline="Аэрофлот", departure_airport_id=1, arrival_airport_id=2, departure_time=base_time.replace(hour=8, minute=0), arrival_time=base_time.replace(hour=10, minute=0), total_seats=180, available_seats=180, price=5500),
            FlightModel(flight_number="SU-002", airline="Аэрофлот", departure_airport_id=2, arrival_airport_id=1, departure_time=base_time.replace(hour=12, minute=0), arrival_time=base_time.replace(hour=14, minute=0), total_seats=180, available_seats=145, price=5500),
            FlightModel(flight_number="U6-100", airline="Уральские авиалинии", departure_airport_id=1, arrival_airport_id=3, departure_time=base_time.replace(hour=10, minute=30), arrival_time=base_time.replace(hour=13, minute=30), total_seats=150, available_seats=150, price=4800),
            FlightModel(flight_number="UT-50", airline="u0423т-Аэр", departure_airport_id=3, arrival_airport_id=4, departure_time=base_time.replace(hour=14, minute=0), arrival_time=base_time.replace(hour=17, minute=30), total_seats=160, available_seats=160, price=6200),
            FlightModel(flight_number="S7-500", airline="S7 Авиалинии", departure_airport_id=2, arrival_airport_id=4, departure_time=base_time.replace(hour=9, minute=0), arrival_time=base_time.replace(hour=12, minute=30), total_seats=120, available_seats=120, price=7200),
            FlightModel(flight_number="SU-003", airline="Аэрофлот", departure_airport_id=1, arrival_airport_id=5, departure_time=base_time.replace(hour=15, minute=0), arrival_time=base_time.replace(hour=19, minute=0), total_seats=200, available_seats=200, price=8500),
            FlightModel(flight_number="FV-201", airline="u0424нир аэро", departure_airport_id=4, arrival_airport_id=2, departure_time=base_time.replace(hour=11, minute=0), arrival_time=base_time.replace(hour=14, minute=0), total_seats=140, available_seats=140, price=6800),
            FlightModel(flight_number="A4-400", airline="u0410 4", departure_airport_id=1, arrival_airport_id=6, departure_time=base_time.replace(hour=7, minute=0), arrival_time=base_time.replace(hour=9, minute=30), total_seats=190, available_seats=190, price=5200),
            FlightModel(flight_number="R2-102", airline="u0420усские авиалинии", departure_airport_id=2, arrival_airport_id=3, departure_time=base_time.replace(hour=13, minute=0), arrival_time=base_time.replace(hour=15, minute=0), total_seats=170, available_seats=170, price=5800),
            FlightModel(flight_number="FP-55", airline="u0424ламинго", departure_airport_id=3, arrival_airport_id=1, departure_time=base_time.replace(hour=16, minute=0), arrival_time=base_time.replace(hour=18, minute=0), total_seats=160, available_seats=160, price=5400),
            FlightModel(flight_number="N1-555", airline="u041dовые века", departure_airport_id=1, arrival_airport_id=7, departure_time=base_time.replace(hour=6, minute=0), arrival_time=base_time.replace(hour=9, minute=30), total_seats=210, available_seats=210, price=7800),
            FlightModel(flight_number="V1-888", airline="u0412ысота", departure_airport_id=2, arrival_airport_id=8, departure_time=base_time.replace(hour=10, minute=0), arrival_time=base_time.replace(hour=13, minute=0), total_seats=140, available_seats=140, price=8200),
            FlightModel(flight_number="E3-200", airline="u042dкспресс", departure_airport_id=1, arrival_airport_id=4, departure_time=base_time.replace(hour=18, minute=0), arrival_time=base_time.replace(hour=21, minute=0), total_seats=150, available_seats=150, price=6500),
            FlightModel(flight_number="G5-777", airline="u0413алактика", departure_airport_id=3, arrival_airport_id=2, departure_time=base_time.replace(hour=14, minute=30), arrival_time=base_time.replace(hour=16, minute=30), total_seats=180, available_seats=180, price=5700),
            FlightModel(flight_number="T4-999", airline="u0422андем", departure_airport_id=4, arrival_airport_id=3, departure_time=base_time.replace(hour=19, minute=0), arrival_time=base_time.replace(hour=20, minute=30), total_seats=120, available_seats=120, price=4200),
            FlightModel(flight_number="L7-333", airline="u041bуч", departure_airport_id=1, arrival_airport_id=9, departure_time=base_time.replace(hour=5, minute=0), arrival_time=base_time.replace(hour=8, minute=0), total_seats=200, available_seats=200, price=9200),
        ]
        
        session.add_all(flights)
        await session.commit()
        
        print("✅ Database initialized!")
        print(f"  - 16 airports created")
        print(f"  - 16 flights created")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Initializing database with complete data...")
    asyncio.run(init_db())
    print("✅ Done!")
