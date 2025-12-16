from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import BookingModel, PaymentModel, BookingStatus


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
        result = await self.db_session.execute(select(BookingModel))
        return result.scalars().all()

    async def create_booking(self, booking_data: dict) -> BookingModel:
        booking = BookingModel(**booking_data)
        self.db_session.add(booking)
        await self.db_session.commit()
        await self.db_session.refresh(booking)
        return booking

    async def update_booking(
        self, booking_id: int, booking_data: dict
    ) -> BookingModel | None:
        booking = await self.get_booking_by_id(booking_id)
        if booking:
            for key, value in booking_data.items():
                if value is not None:
                    setattr(booking, key, value)
            await self.db_session.commit()
            await self.db_session.refresh(booking)
        return booking

    async def delete_booking(self, booking_id: int) -> bool:
        booking = await self.get_booking_by_id(booking_id)
        if booking:
            await self.db_session.delete(booking)
            await self.db_session.commit()
            return True
        return False

    async def cancel_booking(self, booking_id: int) -> BookingModel | None:
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
        payment = PaymentModel(**payment_data)
        self.db_session.add(payment)
        await self.db_session.commit()
        await self.db_session.refresh(payment)
        return payment

    async def update_payment(
        self, payment_id: int, payment_data: dict
    ) -> PaymentModel | None:
        payment = await self.get_payment_by_id(payment_id)
        if payment:
            for key, value in payment_data.items():
                if value is not None:
                    setattr(payment, key, value)
            await self.db_session.commit()
            await self.db_session.refresh(payment)
        return payment
