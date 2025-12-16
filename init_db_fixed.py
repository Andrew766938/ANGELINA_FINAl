"""Script to initialize database with tables and sample data"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.models.flight import AirportModel, FlightModel


async def init_db():
    """Initialize database with tables and sample data"""
    
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
            pass  # Table doesn't exist yet
        
        # Create sample airports
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
                name="Казань",
                city="Казань",
                country="Россия"
            ),
        ]
        
        session.add_all(airports)
        await session.flush()
        
        # Create sample flights
        from datetime import datetime, timedelta
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
        ]
        
        session.add_all(flights)
        await session.commit()
        
        print("✅ Database initialized!")
        print(f"  - 3 airports created")
        print(f"  - 3 flights created")
    
    await engine.dispose()


if __name__ == "__main__":
    print("🚀 Initializing database...")
    asyncio.run(init_db())
    print("✅ Done!")
