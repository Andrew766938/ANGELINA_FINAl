from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_manager import get_db_session
from app.services.booking_service import BookingService, PaymentService
from app.schemes.bookings import BookingCreate, BookingRead, BookingListRead, PaymentRead, BookingUpdate
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/bookings", tags=["bookings"])


# Получить все бронирования (публичный доступ для демо)
@router.get("/", response_model=list[BookingListRead])
async def get_all_bookings(
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        logger.info("Fetching all bookings")
        service = BookingService(db_session)
        bookings = await service.get_all_bookings()
        logger.info(f"Found {len(bookings)} bookings")
        return bookings
    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Создать бронирование (публичный доступ для демо)
@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(
    booking_data: BookingCreate,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        logger.info(f"Creating booking for flight {booking_data.flight_id}: {booking_data.passenger_name}")
        
        service = BookingService(db_session)
        # Для демо используем фиксированный user_id или генерируем новый
        user_id = 1  # Демо пользователь
        
        booking = await service.create_booking(user_id, booking_data)
        
        logger.info(f"Booking created successfully: {booking.booking_number}")
        return booking
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Получить бронирование по ID
@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.get_booking(booking_id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Обновить статус бронирования
@router.put("/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.update_booking(booking_id, booking_update)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Отменить бронирование
@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(
    booking_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        await service.cancel_booking(booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Подтвердить бронирование
@router.post("/{booking_id}/confirm", response_model=BookingRead)
async def confirm_booking(
    booking_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.confirm_booking(booking_id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error confirming booking: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Создать платеж
@router.post("/{booking_id}/payment", response_model=PaymentRead, status_code=201)
async def create_payment(
    booking_id: int,
    payment_data: dict,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.get_booking(booking_id)
        
        payment_service = PaymentService(db_session)
        payment_data["transaction_id"] = str(uuid.uuid4())
        payment = await payment_service.create_payment(booking_id, payment_data)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Подтвердить платеж
@router.post("/payment/{payment_id}/confirm", response_model=PaymentRead)
async def confirm_payment(
    payment_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        payment_service = PaymentService(db_session)
        payment = await payment_service.confirm_payment(payment_id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
