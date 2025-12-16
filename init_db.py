"""Script to initialize database with sample data"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.flight import AirportModel, FlightModel
from app.models.users import UserModel
from app.models.roles import RoleModel


async def init_db():
    """Initialize database with sample data"""
    
    # Create tables
    engine = create_async_engine("sqlite+aiosqlite:///test.db", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if data already exists
        result = await session.execute(text("SELECT COUNT(*) FROM airports"))
        count = result.scalar()
        
        if count > 0:
            print("✅ Database already initialized with sample data")
            await engine.dispose()
            return
        
        # Sample airports
        airports = [
            AirportModel(
                code="MOW",
                name="Шереметьево",
                city="Москва",
                country="Россия"
            ),
            AirportModel(
                code="SPB",
                name="Пулково",
                city="Санкт-Петербург",
                country="Россия"
            ),
            AirportModel(
                code="KZN",
                name="Международный аэропорт Казани",
                city="Казань",
                country="Россия"
            ),
            AirportModel(
                code="YKA",
                name="Якутск Междунаpодный",
                city="Якутск",
                country="Россия"
            ),
            AirportModel(
                code="SVX",
                name="Кольцово",
                city="Екатеринбург",
                country="Россия"
            ),
        ]
        
        session.add_all(airports)
        await session.flush()
        
        # Sample flights
        base_time = datetime.now() + timedelta(days=1)
        
        flights = [
            FlightModel(
                flight_number="SU-001",
                airline="Аэрофлот",
                departure_airport_id=1,
                arrival_airport_id=2,
                departure_time=base_time.replace(hour=8, minute=0),
                arrival_time=base_time.replace(hour=10, minute=0),
                total_seats=180,
                available_seats=180,
                price=5500
            ),
            FlightModel(
                flight_number="SU-002",
                airline="Аэрофлот",
                departure_airport_id=2,
                arrival_airport_id=1,
                departure_time=base_time.replace(hour=12, minute=0),
                arrival_time=base_time.replace(hour=14, minute=0),
                total_seats=180,
                available_seats=145,
                price=5500
            ),
            FlightModel(
                flight_number="U6-100",
                airline="Уральские авиалинии",
                departure_airport_id=1,
                arrival_airport_id=3,
                departure_time=base_time.replace(hour=10, minute=30),
                arrival_time=base_time.replace(hour=13, minute=30),
                total_seats=150,
                available_seats=150,
                price=4800
            ),
            FlightModel(
                flight_number="UT-50",
                airline="Уральские авиалинии",
                departure_airport_id=3,
                arrival_airport_id=5,
                departure_time=base_time.replace(hour=14, minute=0),
                arrival_time=base_time.replace(hour=17, minute=30),
                total_seats=160,
                available_seats=160,
                price=6200
            ),
            FlightModel(
                flight_number="S7-500",
                airline="S7 Airlines",
                departure_airport_id=2,
                arrival_airport_id=5,
                departure_time=base_time.replace(hour=9, minute=0),
                arrival_time=base_time.replace(hour=12, minute=30),
                total_seats=190,
                available_seats=120,
                price=7200
            ),
            FlightModel(
                flight_number="SU-003",
                airline="Аэрофлот",
                departure_airport_id=1,
                arrival_airport_id=4,
                departure_time=base_time.replace(hour=15, minute=0),
                arrival_time=base_time.replace(hour=19, minute=0),
                total_seats=200,
                available_seats=200,
                price=8500
            ),
        ]
        
        session.add_all(flights)
        await session.commit()
        
        print("✅ Database initialized with sample data!")
        print(f"  - {len(airports)} airports")
        print(f"  - {len(flights)} flights")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Initializing database...")
    asyncio.run(init_db())
    print("✅ Done!")
