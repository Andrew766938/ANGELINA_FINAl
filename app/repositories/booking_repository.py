from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import BookingModel, PaymentModel, BookingStatus
import logging

logger = logging.getLogger(__name__)


class BookingRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_booking_by_id(self, booking_id: int) -> BookingModel | None:
        result = await self.db_session.execute(
            select(BookingModel).where(BookingModel.id == booking_id)
        )
        return result.scalars().first()

    async def get_booking_by_number(self, booking_number: str) -> BookingModel | None:
        result = await self.db_session.execute(
            select(BookingModel).where(BookingModel.booking_number == booking_number)
        )
        return result.scalars().first()

    async def get_user_bookings(self, user_id: int) -> list[BookingModel]:
        result = await self.db_session.execute(
            select(BookingModel).where(BookingModel.user_id == user_id)
        )
        return result.scalars().all()

    async def get_flight_bookings(self, flight_id: int) -> list[BookingModel]:
        result = await self.db_session.execute(
            select(BookingModel).where(BookingModel.flight_id == flight_id)
        )
        return result.scalars().all()

    async def get_all_bookings(self) -> list[BookingModel]:
        logger.info("[BookingRepo] Fetching all bookings")
        result = await self.db_session.execute(select(BookingModel))
        bookings = result.scalars().all()
        logger.info(f"[BookingRepo] Found {len(bookings)} bookings")
        return bookings

    async def create_booking(self, booking_data: dict) -> BookingModel:
        logger.info(f"[BookingRepo] Creating booking with number {booking_data.get('booking_number')}")
        try:
            booking = BookingModel(**booking_data)
            self.db_session.add(booking)
            logger.info(f"[BookingRepo] Added booking to session")
            
            await self.db_session.flush()
            logger.info(f"[BookingRepo] Flushed booking to database, ID: {booking.id}")
            
            await self.db_session.commit()
            logger.info(f"[BookingRepo] Committed booking, ID: {booking.id}")
            
            await self.db_session.refresh(booking)
            logger.info(f"[BookingRepo] Refreshed booking data")
            
            return booking
        except Exception as e:
            logger.error(f"[BookingRepo] Error creating booking: {str(e)}", exc_info=True)
            await self.db_session.rollback()
            raise

    async def update_booking(
        self, booking_id: int, booking_data: dict
    ) -> BookingModel | None:
        logger.info(f"[BookingRepo] Updating booking {booking_id}")
        booking = await self.get_booking_by_id(booking_id)
        if booking:
            for key, value in booking_data.items():
                if value is not None:
                    setattr(booking, key, value)
            await self.db_session.flush()
            await self.db_session.commit()
            await self.db_session.refresh(booking)
            logger.info(f"[BookingRepo] Updated booking {booking_id}")
        return booking

    async def delete_booking(self, booking_id: int) -> bool:
        logger.info(f"[BookingRepo] Deleting booking {booking_id}")
        booking = await self.get_booking_by_id(booking_id)
        if booking:
            await self.db_session.delete(booking)
            await self.db_session.commit()
            logger.info(f"[BookingRepo] Deleted booking {booking_id}")
            return True
        return False

    async def cancel_booking(self, booking_id: int) -> BookingModel | None:
        logger.info(f"[BookingRepo] Cancelling booking {booking_id}")
        return await self.update_booking(booking_id, {"status": BookingStatus.CANCELLED})


class PaymentRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_payment_by_id(self, payment_id: int) -> PaymentModel | None:
        result = await self.db_session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        return result.scalars().first()

    async def get_payment_by_booking_id(self, booking_id: int) -> PaymentModel | None:
        result = await self.db_session.execute(
            select(PaymentModel).where(PaymentModel.booking_id == booking_id)
        )
        return result.scalars().first()

    async def get_payment_by_transaction_id(
        self, transaction_id: str
    ) -> PaymentModel | None:
        result = await self.db_session.execute(
            select(PaymentModel).where(PaymentModel.transaction_id == transaction_id)
        )
        return result.scalars().first()

    async def create_payment(self, payment_data: dict) -> PaymentModel:
        logger.info(f"[PaymentRepo] Creating payment for booking {payment_data.get('booking_id')}")
        try:
            payment = PaymentModel(**payment_data)
            self.db_session.add(payment)
            await self.db_session.flush()
            await self.db_session.commit()
            await self.db_session.refresh(payment)
            logger.info(f"[PaymentRepo] Payment created, ID: {payment.id}")
            return payment
        except Exception as e:
            logger.error(f"[PaymentRepo] Error creating payment: {str(e)}", exc_info=True)
            await self.db_session.rollback()
            raise

    async def update_payment(
        self, payment_id: int, payment_data: dict
    ) -> PaymentModel | None:
        logger.info(f"[PaymentRepo] Updating payment {payment_id}")
        payment = await self.get_payment_by_id(payment_id)
        if payment:
            for key, value in payment_data.items():
                if value is not None:
                    setattr(payment, key, value)
            await self.db_session.flush()
            await self.db_session.commit()
            await self.db_session.refresh(payment)
            logger.info(f"[PaymentRepo] Updated payment {payment_id}")
        return payment
