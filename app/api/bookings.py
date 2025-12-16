from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db_manager import get_db_session
from app.services.booking_service import BookingService, PaymentService
from app.schemes.bookings import BookingCreate, BookingRead, BookingListRead, PaymentRead
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])


# Бронирования
@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(
    booking_data: BookingCreate,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.create_booking(current_user["id"], booking_data)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=list[BookingListRead])
async def get_my_bookings(
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        bookings = await service.get_user_bookings(current_user["id"])
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[BookingListRead])
async def get_all_bookings(
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    # Онли админы могут видеть все бронирования
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Only admins can view all bookings"
        )
    try:
        service = BookingService(db_session)
        bookings = await service.get_all_bookings()
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: int,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.get_booking(booking_id)
        # Проверяем доступ
        if booking.user_id != current_user["id"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(
    booking_id: int,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.get_booking(booking_id)
        # Проверяем доступ
        if booking.user_id != current_user["id"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        await service.cancel_booking(booking_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/confirm", response_model=BookingRead)
async def confirm_booking(
    booking_id: int,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.get_booking(booking_id)
        if booking.user_id != current_user["id"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        booking = await service.confirm_booking(booking_id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Оплаты (Payments)
@router.post("/{booking_id}/payment", response_model=PaymentRead, status_code=201)
async def create_payment(
    booking_id: int,
    payment_data: dict,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        service = BookingService(db_session)
        booking = await service.get_booking(booking_id)
        if booking.user_id != current_user["id"] and current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Access denied")

        payment_service = PaymentService(db_session)
        payment = await payment_service.create_payment(booking_id, payment_data)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment/{payment_id}/confirm", response_model=PaymentRead)
async def confirm_payment(
    payment_id: int,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        payment_service = PaymentService(db_session)
        payment = await payment_service.confirm_payment(payment_id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
