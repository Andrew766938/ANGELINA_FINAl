from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.flight import FlightModel, AirportModel


class FlightRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_flight_by_id(self, flight_id: int) -> FlightModel | None:
        result = await self.db_session.execute(
            select(FlightModel).where(FlightModel.id == flight_id)
        )
        return result.scalars().first()

    async def get_all_flights(self) -> list[FlightModel]:
        result = await self.db_session.execute(select(FlightModel))
        return result.scalars().all()

    async def search_flights(
        self,
        departure_airport_id: int | None = None,
        arrival_airport_id: int | None = None,
        departure_date: datetime | None = None,
    ) -> list[FlightModel]:
        query = select(FlightModel)
        filters = []

        if departure_airport_id:
            filters.append(FlightModel.departure_airport_id == departure_airport_id)
        if arrival_airport_id:
            filters.append(FlightModel.arrival_airport_id == arrival_airport_id)
        if departure_date:
            filters.append(
                func.date(FlightModel.departure_time)
                == func.date(departure_date)
            )

        if filters:
            query = query.where(and_(*filters))

        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def create_flight(self, flight_data: dict) -> FlightModel:
        flight = FlightModel(**flight_data)
        self.db_session.add(flight)
        await self.db_session.flush()
        return flight

    async def update_flight(self, flight_id: int, flight_data: dict) -> FlightModel | None:
        flight = await self.get_flight_by_id(flight_id)
        if flight:
            for key, value in flight_data.items():
                if value is not None:
                    setattr(flight, key, value)
            await self.db_session.flush()
        return flight

    async def delete_flight(self, flight_id: int) -> bool:
        flight = await self.get_flight_by_id(flight_id)
        if flight:
            await self.db_session.delete(flight)
            return True
        return False


class AirportRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_airport_by_id(self, airport_id: int) -> AirportModel | None:
        result = await self.db_session.execute(
            select(AirportModel).where(AirportModel.id == airport_id)
        )
        return result.scalars().first()

    async def get_airport_by_code(self, code: str) -> AirportModel | None:
        result = await self.db_session.execute(
            select(AirportModel).where(AirportModel.code == code.upper())
        )
        return result.scalars().first()

    async def get_all_airports(self) -> list[AirportModel]:
        result = await self.db_session.execute(select(AirportModel))
        return result.scalars().all()

    async def create_airport(self, airport_data: dict) -> AirportModel:
        # Normalize code to uppercase
        if 'code' in airport_data:
            airport_data['code'] = airport_data['code'].upper()
        airport = AirportModel(**airport_data)
        self.db_session.add(airport)
        await self.db_session.flush()
        return airport

    async def update_airport(self, airport_id: int, airport_data: dict) -> AirportModel | None:
        airport = await self.get_airport_by_id(airport_id)
        if airport:
            for key, value in airport_data.items():
                if value is not None:
                    setattr(airport, key, value)
            await self.db_session.flush()
        return airport

    async def delete_airport(self, airport_id: int) -> bool:
        airport = await self.get_airport_by_id(airport_id)
        if airport:
            await self.db_session.delete(airport)
            return True
        return False
