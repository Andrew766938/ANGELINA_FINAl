from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.flight_repository import FlightRepository, AirportRepository
from app.schemes.flights import FlightCreate, FlightUpdate, AirportCreate


class FlightService:
    def __init__(self, db_session: AsyncSession):
        self.flight_repo = FlightRepository(db_session)
        self.airport_repo = AirportRepository(db_session)
        self.db_session = db_session

    async def get_flight(self, flight_id: int):
        flight = await self.flight_repo.get_flight_by_id(flight_id)
        if not flight:
            raise ValueError(f"Flight with id {flight_id} not found")
        return flight

    async def get_all_flights(self):
        return await self.flight_repo.get_all_flights()

    async def search_flights(
        self,
        departure_airport_id: int | None = None,
        arrival_airport_id: int | None = None,
        departure_date: str | None = None,
    ):
        departure_date_obj = None
        if departure_date:
            try:
                departure_date_obj = datetime.fromisoformat(departure_date)
            except ValueError:
                raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DD)")

        flights = await self.flight_repo.search_flights(
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id,
            departure_date=departure_date_obj,
        )
        return flights

    async def create_flight(self, flight_data: FlightCreate):
        # Проверяем аэропорты
        departure_airport = await self.airport_repo.get_airport_by_id(
            flight_data.departure_airport_id
        )
        arrival_airport = await self.airport_repo.get_airport_by_id(
            flight_data.arrival_airport_id
        )

        if not departure_airport:
            raise ValueError("Departure airport not found")
        if not arrival_airport:
            raise ValueError("Arrival airport not found")
        if flight_data.available_seats > flight_data.total_seats:
            raise ValueError("Available seats cannot exceed total seats")

        flight = await self.flight_repo.create_flight(flight_data.dict())
        return flight

    async def update_flight(self, flight_id: int, flight_data: FlightUpdate):
        flight = await self.flight_repo.get_flight_by_id(flight_id)
        if not flight:
            raise ValueError(f"Flight with id {flight_id} not found")

        update_data = flight_data.dict(exclude_unset=True)
        flight = await self.flight_repo.update_flight(flight_id, update_data)
        return flight

    async def delete_flight(self, flight_id: int):
        success = await self.flight_repo.delete_flight(flight_id)
        if not success:
            raise ValueError(f"Flight with id {flight_id} not found")
        return {"message": "Flight deleted successfully"}


class AirportService:
    def __init__(self, db_session: AsyncSession):
        self.airport_repo = AirportRepository(db_session)

    async def get_airport(self, airport_id: int):
        airport = await self.airport_repo.get_airport_by_id(airport_id)
        if not airport:
            raise ValueError(f"Airport with id {airport_id} not found")
        return airport

    async def get_airport_by_code(self, code: str):
        airport = await self.airport_repo.get_airport_by_code(code)
        if not airport:
            raise ValueError(f"Airport with code {code} not found")
        return airport

    async def get_all_airports(self):
        return await self.airport_repo.get_all_airports()

    async def create_airport(self, airport_data: AirportCreate):
        existing = await self.airport_repo.get_airport_by_code(airport_data.code)
        if existing:
            raise ValueError(f"Airport with code {airport_data.code} already exists")

        airport = await self.airport_repo.create_airport(airport_data.dict())
        return airport

    async def update_airport(self, airport_id: int, airport_data: dict):
        airport = await self.airport_repo.get_airport_by_id(airport_id)
        if not airport:
            raise ValueError(f"Airport with id {airport_id} not found")

        airport = await self.airport_repo.update_airport(airport_id, airport_data)
        return airport

    async def delete_airport(self, airport_id: int):
        success = await self.airport_repo.delete_airport(airport_id)
        if not success:
            raise ValueError(f"Airport with id {airport_id} not found")
        return {"message": "Airport deleted successfully"}
