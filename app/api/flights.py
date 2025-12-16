from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/flights", tags=["flights"])


# ============== АЭРОПОРТЫ (AIRPORTS) ==============
@router.post("/airports", response_model=AirportRead, status_code=201)
async def create_airport(
    airport_data: AirportCreate, db_session: AsyncSession = Depends(get_db_session)
):
    logger.info(f"[POST /flights/airports] Creating airport: {airport_data.code}")
    try:
        service = AirportService(db_session)
        airport = await service.create_airport(airport_data)
        await db_session.commit()
        logger.info(f"[POST /flights/airports] Airport created successfully: {airport.id}")
        return airport
    except ValueError as e:
        logger.error(f"[POST /flights/airports] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[POST /flights/airports] Error creating airport: {str(e)}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail="Error creating airport")


@router.get("/airports/", response_model=list[AirportRead])
async def get_airports(db_session: AsyncSession = Depends(get_db_session)):
    logger.info("[GET /flights/airports/] Getting all airports")
    try:
        service = AirportService(db_session)
        airports = await service.get_all_airports()
        logger.info(f"[GET /flights/airports/] Found {len(airports) if airports else 0} airports")
        return airports if airports else []
    except Exception as e:
        logger.error(f"[GET /flights/airports/] Error getting airports: {str(e)}")
        return []


@router.get("/airports/{airport_id}", response_model=AirportRead)
async def get_airport(
    airport_id: int, db_session: AsyncSession = Depends(get_db_session)
):
    logger.info(f"[GET /flights/airports/{airport_id}] Getting airport")
    try:
        service = AirportService(db_session)
        airport = await service.get_airport(airport_id)
        logger.info(f"[GET /flights/airports/{airport_id}] Found airport: {airport.code}")
        return airport
    except ValueError as e:
        logger.error(f"[GET /flights/airports/{airport_id}] Airport not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[GET /flights/airports/{airport_id}] Error getting airport: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting airport")


@router.delete("/airports/{airport_id}", status_code=204)
async def delete_airport(
    airport_id: int, db_session: AsyncSession = Depends(get_db_session)
):
    logger.info(f"[DELETE /flights/airports/{airport_id}] Deleting airport")
    try:
        service = AirportService(db_session)
        await service.delete_airport(airport_id)
        await db_session.commit()
        logger.info(f"[DELETE /flights/airports/{airport_id}] Airport deleted successfully")
    except ValueError as e:
        logger.error(f"[DELETE /flights/airports/{airport_id}] Airport not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[DELETE /flights/airports/{airport_id}] Error deleting airport: {str(e)}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail="Error deleting airport")


# ============== РЕЙСЫ (FLIGHTS) ==============
@router.post("/", response_model=FlightRead, status_code=201)
async def create_flight(
    flight_data: FlightCreate, db_session: AsyncSession = Depends(get_db_session)
):
    logger.info(f"[POST /flights/] Creating flight: {flight_data.flight_number}")
    try:
        service = FlightService(db_session)
        flight = await service.create_flight(flight_data)
        await db_session.commit()
        logger.info(f"[POST /flights/] Flight created: {flight.id}")
        return flight
    except ValueError as e:
        logger.error(f"[POST /flights/] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[POST /flights/] Error creating flight: {str(e)}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail="Error creating flight")


@router.get("/", response_model=list[FlightListRead])
async def get_flights(
    departure_airport_id: int | None = Query(None),
    arrival_airport_id: int | None = Query(None),
    departure_date: str | None = Query(None),
    db_session: AsyncSession = Depends(get_db_session),
):
    logger.info(f"[GET /flights/] Getting flights with filters: from={departure_airport_id}, to={arrival_airport_id}")
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
        logger.info(f"[GET /flights/] Found {len(flights) if flights else 0} flights")
        return flights if flights else []
    except ValueError as e:
        logger.error(f"[GET /flights/] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[GET /flights/] Error getting flights: {str(e)}")
        return []


@router.get("/{flight_id}", response_model=FlightRead)
async def get_flight(
    flight_id: int, db_session: AsyncSession = Depends(get_db_session)
):
    logger.info(f"[GET /flights/{flight_id}] Getting flight")
    try:
        service = FlightService(db_session)
        flight = await service.get_flight(flight_id)
        logger.info(f"[GET /flights/{flight_id}] Found flight: {flight.flight_number}")
        return flight
    except ValueError as e:
        logger.error(f"[GET /flights/{flight_id}] Flight not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[GET /flights/{flight_id}] Error getting flight: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting flight")


@router.put("/{flight_id}", response_model=FlightRead)
async def update_flight(
    flight_id: int,
    flight_data: FlightUpdate,
    db_session: AsyncSession = Depends(get_db_session),
):
    logger.info(f"[PUT /flights/{flight_id}] Updating flight")
    try:
        service = FlightService(db_session)
        flight = await service.update_flight(flight_id, flight_data)
        await db_session.commit()
        logger.info(f"[PUT /flights/{flight_id}] Flight updated")
        return flight
    except ValueError as e:
        logger.error(f"[PUT /flights/{flight_id}] Flight not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[PUT /flights/{flight_id}] Error updating flight: {str(e)}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail="Error updating flight")


@router.delete("/{flight_id}", status_code=204)
async def delete_flight(
    flight_id: int, db_session: AsyncSession = Depends(get_db_session)
):
    logger.info(f"[DELETE /flights/{flight_id}] Deleting flight")
    try:
        service = FlightService(db_session)
        await service.delete_flight(flight_id)
        await db_session.commit()
        logger.info(f"[DELETE /flights/{flight_id}] Flight deleted")
    except ValueError as e:
        logger.error(f"[DELETE /flights/{flight_id}] Flight not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[DELETE /flights/{flight_id}] Error deleting flight: {str(e)}")
        await db_session.rollback()
        raise HTTPException(status_code=500, detail="Error deleting flight")
