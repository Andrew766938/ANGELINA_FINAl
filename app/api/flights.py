from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_manager import get_db_session
from app.services.flight_service import FlightService, AirportService
from app.schemes.flights import (
    FlightCreate,
    FlightRead,
    FlightListRead,
    AirportCreate,
    AirportRead,
    FlightUpdate,
)

router = APIRouter(prefix="/flights", tags=["flights"])


# Авюлинеа (Airport)
@router.post("/airports", response_model=AirportRead, status_code=201)
async def create_airport(
    airport_data: AirportCreate, db_session: AsyncSession = Depends(get_db_session)
):
    try:
        service = AirportService(db_session)
        airport = await service.create_airport(airport_data)
        return airport
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/airports", response_model=list[AirportRead])
async def get_airports(db_session: AsyncSession = Depends(get_db_session)):
    try:
        service = AirportService(db_session)
        airports = await service.get_all_airports()
        return airports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/airports/{airport_id}", response_model=AirportRead)
async def get_airport(
    airport_id: int, db_session: AsyncSession = Depends(get_db_session)
):
    try:
        service = AirportService(db_session)
        airport = await service.get_airport(airport_id)
        return airport
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Рейсы (Flights)
@router.post("/", response_model=FlightRead, status_code=201)
async def create_flight(
    flight_data: FlightCreate, db_session: AsyncSession = Depends(get_db_session)
):
    try:
        service = FlightService(db_session)
        flight = await service.create_flight(flight_data)
        return flight
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[FlightListRead])
async def get_flights(
    departure_airport_id: int | None = Query(None),
    arrival_airport_id: int | None = Query(None),
    departure_date: str | None = Query(None),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = FlightService(db_session)
        if departure_airport_id or arrival_airport_id or departure_date:
            flights = await service.search_flights(
                departure_airport_id=departure_airport_id,
                arrival_airport_id=arrival_airport_id,
                departure_date=departure_date,
            )
        else:
            flights = await service.get_all_flights()
        return flights
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flight_id}", response_model=FlightRead)
async def get_flight(
    flight_id: int, db_session: AsyncSession = Depends(get_db_session)
):
    try:
        service = FlightService(db_session)
        flight = await service.get_flight(flight_id)
        return flight
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{flight_id}", response_model=FlightRead)
async def update_flight(
    flight_id: int,
    flight_data: FlightUpdate,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = FlightService(db_session)
        flight = await service.update_flight(flight_id, flight_data)
        return flight
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{flight_id}", status_code=204)
async def delete_flight(
    flight_id: int, db_session: AsyncSession = Depends(get_db_session)
):
    try:
        service = FlightService(db_session)
        await service.delete_flight(flight_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
