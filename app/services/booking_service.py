import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.booking_repository import BookingRepository, PaymentRepository
from app.repositories.flight_repository import FlightRepository
from app.schemes.bookings import BookingCreate
from app.models.booking import BookingStatus


class BookingService:
    def __init__(self, db_session: AsyncSession):
        self.booking_repo = BookingRepository(db_session)
        self.payment_repo = PaymentRepository(db_session)
        self.flight_repo = FlightRepository(db_session)
        self.db_session = db_session

    def _generate_booking_number(self) -> str:
        """Генерирует уникальный номер бронирования"""
        return "BK" + "".join(random.choices(string.digits, k=8))

    async def create_booking(self, user_id: int, booking_data: BookingCreate):
        """Создает новое бронирование"""
        # Проверяем рейс
        flight = await self.flight_repo.get_flight_by_id(booking_data.flight_id)
        if not flight:
            raise ValueError(f"Flight with id {booking_data.flight_id} not found")

        # Проверяем количество свободных мест
        if flight.available_seats < booking_data.seats_count:
            raise ValueError(
                f"Not enough available seats. Available: {flight.available_seats}, Requested: {booking_data.seats_count}"
            )

        # Создаем бронирование
        booking_number = self._generate_booking_number()
        total_price = flight.price * booking_data.seats_count

        booking_dict = {
            "user_id": user_id,
            "flight_id": booking_data.flight_id,
            "booking_number": booking_number,
            "passenger_name": booking_data.passenger_name,
            "passenger_email": booking_data.passenger_email,
            "passenger_phone": booking_data.passenger_phone,
            "seats_count": booking_data.seats_count,
            "total_price": total_price,
            "status": BookingStatus.PENDING,
        }

        booking = await self.booking_repo.create_booking(booking_dict)

        # Обновляем количество свободных мест в рейсе
        await self.flight_repo.update_flight(
            booking_data.flight_id,
            {"available_seats": flight.available_seats - booking_data.seats_count},
        )

        return booking

    async def get_booking(self, booking_id: int):
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")
        return booking

    async def get_user_bookings(self, user_id: int):
        return await self.booking_repo.get_user_bookings(user_id)

    async def get_all_bookings(self):
        return await self.booking_repo.get_all_bookings()

    async def cancel_booking(self, booking_id: int):
        """Отменяет бронирование и возвращает места на рейс"""
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")

        if booking.status == BookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled")

        # Возвращаем места на рейс
        flight = await self.flight_repo.get_flight_by_id(booking.flight_id)
        await self.flight_repo.update_flight(
            booking.flight_id,
            {"available_seats": flight.available_seats + booking.seats_count},
        )

        # Обновляем статус бронирования
        cancelled_booking = await self.booking_repo.cancel_booking(booking_id)
        return cancelled_booking

    async def confirm_booking(self, booking_id: int):
        """Подтверждает бронирование"""
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")

        booking = await self.booking_repo.update_booking(
            booking_id, {"status": BookingStatus.CONFIRMED}
        )
        return booking


class PaymentService:
    def __init__(self, db_session: AsyncSession):
        self.payment_repo = PaymentRepository(db_session)
        self.booking_repo = BookingRepository(db_session)

    async def create_payment(self, booking_id: int, payment_data: dict):
        """Создает платеж для бронирования"""
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")

        # Генерируем ID транзакции
        transaction_id = "TRX" + "".join(random.choices(string.digits, k=10))

        payment_dict = {
            "booking_id": booking_id,
            "amount": booking.total_price,
            "payment_method": payment_data.get("payment_method", "card"),
            "transaction_id": transaction_id,
            "status": "pending",
        }

        payment = await self.payment_repo.create_payment(payment_dict)
        return payment

    async def confirm_payment(self, payment_id: int):
        """Подтверждает платеж"""
        payment = await self.payment_repo.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")

        payment = await self.payment_repo.update_payment(
            payment_id, {"status": "completed"}
        )

        # Обновляем статус бронирования
        await self.booking_repo.update_booking(
            payment.booking_id, {"status": BookingStatus.CONFIRMED}
        )

        return payment

    async def get_payment(self, payment_id: int):
        payment = await self.payment_repo.get_payment_by_id(payment_id)
        if not payment:
            raise ValueError(f"Payment with id {payment_id} not found")
        return payment
