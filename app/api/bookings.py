from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_manager import get_db_session
from app.repositories.booking_repository import BookingRepository, PaymentRepository
from app.repositories.flight_repository import FlightRepository
from app.models.booking import BookingStatus, BookingModel
from app.schemes.bookings import BookingCreate, BookingRead, BookingListRead
import random
import string
import logging
import traceback

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
        logger.info("[API] GET /bookings/ - Fetching all bookings")
        booking_repo = BookingRepository(db_session)
        bookings = await booking_repo.get_all_bookings()
        logger.info(f"[API] GET /bookings/ - Found {len(bookings)} bookings")
        return bookings
    except Exception as e:
        logger.error(f"[API] GET /bookings/ - Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching bookings: {str(e)}")


@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(
    booking_data: BookingCreate,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Create a new booking"""
    full_traceback = ""
    try:
        logger.info(f"[API] POST /bookings/ - Starting booking creation")
        logger.info(f"[API] Request data: flight_id={booking_data.flight_id}, passenger={booking_data.passenger_name}, seats={booking_data.seats_count}")
        
        # Initialize repositories
        booking_repo = BookingRepository(db_session)
        flight_repo = FlightRepository(db_session)
        
        # Validate flight exists
        logger.info(f"[API] Checking if flight {booking_data.flight_id} exists")
        flight = await flight_repo.get_flight_by_id(booking_data.flight_id)
        if not flight:
            logger.error(f"[API] Flight {booking_data.flight_id} not found")
            raise ValueError(f"Flight with id {booking_data.flight_id} not found")
        
        logger.info(f"[API] Flight found: {flight.flight_number}, available seats: {flight.available_seats}")
        
        # Validate available seats
        if flight.available_seats < booking_data.seats_count:
            logger.error(f"[API] Not enough seats: available={flight.available_seats}, requested={booking_data.seats_count}")
            raise ValueError(
                f"Not enough available seats. Available: {flight.available_seats}, Requested: {booking_data.seats_count}"
            )
        
        # Calculate total price
        total_price = flight.price * booking_data.seats_count
        logger.info(f"[API] Total price calculated: {total_price} (price per seat: {flight.price})")
        
        # Generate booking number
        booking_number = generate_booking_number()
        logger.info(f"[API] Generated booking number: {booking_number}")
        
        # Prepare booking data
        booking_dict = {
            "user_id": 1,  # Demo user
            "flight_id": booking_data.flight_id,
            "booking_number": booking_number,
            "passenger_name": booking_data.passenger_name,
            "passenger_email": booking_data.passenger_email,
            "passenger_phone": booking_data.passenger_phone,
            "seats_count": booking_data.seats_count,
            "total_price": total_price,
            "status": BookingStatus.PENDING,
        }
        
        logger.info(f"[API] Creating booking in database with: {booking_dict}")
        
        # Create booking
        booking = await booking_repo.create_booking(booking_dict)
        logger.info(f"[API] Booking created successfully: id={booking.id}, number={booking.booking_number}")
        
        # Update flight available seats
        logger.info(f"[API] Updating flight {booking_data.flight_id} available seats from {flight.available_seats} to {flight.available_seats - booking_data.seats_count}")
        updated_flight = await flight_repo.update_flight(
            booking_data.flight_id,
            {"available_seats": flight.available_seats - booking_data.seats_count},
        )
        logger.info(f"[API] Flight updated successfully")
        
        logger.info(f"[API] POST /bookings/ - Booking created successfully: {booking.booking_number}")
        return booking
        
    except ValueError as e:
        logger.warning(f"[API] POST /bookings/ - Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        full_traceback = traceback.format_exc()
        logger.error(f"[API] POST /bookings/ - Unexpected error: {str(e)}")
        logger.error(f"[API] Full traceback:\n{full_traceback}")
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Get booking by ID"""
    try:
        logger.info(f"[API] GET /bookings/{booking_id}")
        booking_repo = BookingRepository(db_session)
        booking = await booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"[API] Booking {booking_id} not found")
            raise HTTPException(status_code=404, detail=f"Booking with id {booking_id} not found")
        return booking
    except Exception as e:
        logger.error(f"[API] GET /bookings/{booking_id} - Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{booking_id}", response_model=BookingRead)
async def update_booking_status(
    booking_id: int,
    status: str,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Update booking status"""
    try:
        logger.info(f"[API] PUT /bookings/{booking_id} - Updating status to {status}")
        booking_repo = BookingRepository(db_session)
        booking = await booking_repo.update_booking(booking_id, {"status": status})
        if not booking:
            logger.error(f"[API] Booking {booking_id} not found")
            raise HTTPException(status_code=404, detail=f"Booking with id {booking_id} not found")
        logger.info(f"[API] Booking {booking_id} updated")
        return booking
    except Exception as e:
        logger.error(f"[API] PUT /bookings/{booking_id} - Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(
    booking_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Cancel booking"""
    try:
        logger.info(f"[API] DELETE /bookings/{booking_id} - Cancelling booking")
        booking_repo = BookingRepository(db_session)
        flight_repo = FlightRepository(db_session)
        
        booking = await booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"[API] Booking {booking_id} not found")
            raise HTTPException(status_code=404, detail=f"Booking with id {booking_id} not found")
        
        # Return seats to flight
        flight = await flight_repo.get_flight_by_id(booking.flight_id)
        await flight_repo.update_flight(
            booking.flight_id,
            {"available_seats": flight.available_seats + booking.seats_count}
        )
        
        # Cancel booking
        await booking_repo.cancel_booking(booking_id)
        logger.info(f"[API] Booking {booking_id} cancelled")
        
    except Exception as e:
        logger.error(f"[API] DELETE /bookings/{booking_id} - Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
