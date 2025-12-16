from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_manager import get_db_session
from app.repositories.booking_repository import BookingRepository
from app.repositories.flight_repository import FlightRepository
from app.models.booking import BookingStatus, BookingModel
from app.schemes.bookings import BookingCreate, BookingRead, BookingListRead
import random
import string
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bookings", tags=["bookings"])


def generate_booking_number() -> str:
    """Generate unique booking number"""
    return "BK" + "".join(random.choices(string.digits, k=8))


@router.get("/", response_model=list[BookingListRead])
async def get_all_bookings(
    db_session: AsyncSession = Depends(get_db_session),
):
    """Get all bookings"""
    try:
        logger.info("[Bookings GET] Fetching all bookings")
        booking_repo = BookingRepository(db_session)
        bookings = await booking_repo.get_all_bookings()
        logger.info(f"[Bookings GET] Found {len(bookings)} bookings")
        return bookings
    except Exception as e:
        logger.error(f"[Bookings GET] Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(
    booking_data: BookingCreate,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Create a new booking"""
    logger.info(f"[Bookings POST] Starting creation")
    logger.info(f"[Bookings POST] Data received: {booking_data.dict()}")
    
    try:
        # Get repositories
        booking_repo = BookingRepository(db_session)
        flight_repo = FlightRepository(db_session)
        
        # Validate flight
        logger.info(f"[Bookings POST] Checking flight {booking_data.flight_id}")
        flight = await flight_repo.get_flight_by_id(booking_data.flight_id)
        if not flight:
            logger.error(f"[Bookings POST] Flight not found: {booking_data.flight_id}")
            raise HTTPException(status_code=400, detail="Flight not found")
        
        logger.info(f"[Bookings POST] Flight found: {flight.flight_number}")
        logger.info(f"[Bookings POST] Available seats: {flight.available_seats}, Requested: {booking_data.seats_count}")
        
        # Check seats
        if flight.available_seats < booking_data.seats_count:
            logger.error(f"[Bookings POST] Not enough seats")
            raise HTTPException(status_code=400, detail="Not enough available seats")
        
        # Create booking
        booking_number = generate_booking_number()
        total_price = flight.price * booking_data.seats_count
        
        logger.info(f"[Bookings POST] Creating booking number: {booking_number}")
        logger.info(f"[Bookings POST] Total price: {total_price}")
        
        booking_dict = {
            "user_id": 1,
            "flight_id": booking_data.flight_id,
            "booking_number": booking_number,
            "passenger_name": booking_data.passenger_name,
            "passenger_email": booking_data.passenger_email,
            "passenger_phone": booking_data.passenger_phone,
            "seats_count": booking_data.seats_count,
            "total_price": total_price,
            "status": BookingStatus.PENDING,
        }
        
        booking = await booking_repo.create_booking(booking_dict)
        logger.info(f"[Bookings POST] Booking created: id={booking.id}")
        
        # Update flight seats
        logger.info(f"[Bookings POST] Updating flight seats")
        new_available = flight.available_seats - booking_data.seats_count
        await flight_repo.update_flight(
            booking_data.flight_id,
            {"available_seats": new_available},
        )
        logger.info(f"[Bookings POST] Flight updated")
        
        logger.info(f"[Bookings POST] Success! Booking: {booking.booking_number}")
        return booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Bookings POST] Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Get booking by ID"""
    try:
        booking_repo = BookingRepository(db_session)
        booking = await booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}", status_code=200)
async def delete_booking(
    booking_id: int,
    is_admin: bool = False,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Delete a booking by ID (Admin only)"""
    logger.info(f"[Bookings DELETE] Attempting to delete booking {booking_id}")
    logger.info(f"[Bookings DELETE] User is_admin: {is_admin}")
    
    # Check if user is admin
    if not is_admin:
        logger.error(f"[Bookings DELETE] Access denied - user is not admin")
        raise HTTPException(status_code=403, detail="Only administrators can delete bookings")
    
    try:
        booking_repo = BookingRepository(db_session)
        flight_repo = FlightRepository(db_session)
        
        # Get booking
        booking = await booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"[Bookings DELETE] Booking not found: {booking_id}")
            raise HTTPException(status_code=404, detail="Booking not found")
        
        logger.info(f"[Bookings DELETE] Found booking: {booking.booking_number}")
        
        # Get flight to restore seats
        flight = await flight_repo.get_flight_by_id(booking.flight_id)
        if flight:
            logger.info(f"[Bookings DELETE] Restoring {booking.seats_count} seats to flight {flight.flight_number}")
            new_available = flight.available_seats + booking.seats_count
            await flight_repo.update_flight(
                booking.flight_id,
                {"available_seats": new_available},
            )
            logger.info(f"[Bookings DELETE] Flight seats updated")
        
        # Delete booking
        await booking_repo.delete_booking(booking_id)
        logger.info(f"[Bookings DELETE] Booking {booking_id} deleted successfully")
        
        return {"message": f"Booking {booking.booking_number} deleted successfully", "booking_id": booking_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Bookings DELETE] Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
