import random
import string
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.booking_repository import BookingRepository, PaymentRepository
from app.repositories.flight_repository import FlightRepository
from app.schemes.bookings import BookingCreate
from app.models.booking import BookingStatus

logger = logging.getLogger(__name__)


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
        try:
            logger.info(f"[BookingService] Starting to create booking for user {user_id}, flight {booking_data.flight_id}")
            
            # Проверяем рейс
            flight = await self.flight_repo.get_flight_by_id(booking_data.flight_id)
            if not flight:
                logger.error(f"[BookingService] Flight with id {booking_data.flight_id} not found")
                raise ValueError(f"Flight with id {booking_data.flight_id} not found")
            
            logger.info(f"[BookingService] Flight found: {flight.flight_number}, available seats: {flight.available_seats}")

            # Проверяем количество свободных мест
            if flight.available_seats < booking_data.seats_count:
                logger.error(f"[BookingService] Not enough seats. Available: {flight.available_seats}, Requested: {booking_data.seats_count}")
                raise ValueError(
                    f"Not enough available seats. Available: {flight.available_seats}, Requested: {booking_data.seats_count}"
                )

            # Создаем бронирование
            booking_number = self._generate_booking_number()
            total_price = flight.price * booking_data.seats_count
            
            logger.info(f"[BookingService] Creating booking number {booking_number}, total price: {total_price}")

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
            logger.info(f"[BookingService] Booking created successfully: {booking.booking_number} (id: {booking.id})")

            # Обновляем количество свободных мест в рейсе
            logger.info(f"[BookingService] Updating available seats for flight {booking_data.flight_id}")
            await self.flight_repo.update_flight(
                booking_data.flight_id,
                {"available_seats": flight.available_seats - booking_data.seats_count},
            )
            logger.info(f"[BookingService] Flight updated successfully")

            return booking
            
        except Exception as e:
            logger.error(f"[BookingService] Error creating booking: {str(e)}", exc_info=True)
            raise

    async def get_booking(self, booking_id: int):
        logger.info(f"[BookingService] Getting booking {booking_id}")
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"[BookingService] Booking with id {booking_id} not found")
            raise ValueError(f"Booking with id {booking_id} not found")
        return booking

    async def get_user_bookings(self, user_id: int):
        logger.info(f"[BookingService] Getting bookings for user {user_id}")
        return await self.booking_repo.get_user_bookings(user_id)

    async def get_all_bookings(self):
        logger.info("[BookingService] Getting all bookings")
        bookings = await self.booking_repo.get_all_bookings()
        logger.info(f"[BookingService] Found {len(bookings)} bookings")
        return bookings

    async def cancel_booking(self, booking_id: int):
        """Отменяет бронирование и возвращает места на рейс"""
        logger.info(f"[BookingService] Cancelling booking {booking_id}")
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"[BookingService] Booking with id {booking_id} not found")
            raise ValueError(f"Booking with id {booking_id} not found")

        if booking.status == BookingStatus.CANCELLED:
            logger.warning(f"[BookingService] Booking {booking_id} already cancelled")
            raise ValueError("Booking is already cancelled")

        # Возвращаем места на рейс
        flight = await self.flight_repo.get_flight_by_id(booking.flight_id)
        await self.flight_repo.update_flight(
            booking.flight_id,
            {"available_seats": flight.available_seats + booking.seats_count},
        )

        # Обновляем статус бронирования
        cancelled_booking = await self.booking_repo.cancel_booking(booking_id)
        logger.info(f"[BookingService] Booking {booking_id} cancelled successfully")
        return cancelled_booking

    async def confirm_booking(self, booking_id: int):
        """Подтверждает бронирование"""
        logger.info(f"[BookingService] Confirming booking {booking_id}")
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"[BookingService] Booking with id {booking_id} not found")
            raise ValueError(f"Booking with id {booking_id} not found")

        booking = await self.booking_repo.update_booking(
            booking_id, {"status": BookingStatus.CONFIRMED}
        )
        logger.info(f"[BookingService] Booking {booking_id} confirmed successfully")
        return booking


class PaymentService:
    def __init__(self, db_session: AsyncSession):
        self.payment_repo = PaymentRepository(db_session)
        self.booking_repo = BookingRepository(db_session)

    async def create_payment(self, booking_id: int, payment_data: dict):
        """Создает платеж для бронирования"""
        logger.info(f"[PaymentService] Creating payment for booking {booking_id}")
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"[PaymentService] Booking with id {booking_id} not found")
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
        logger.info(f"[PaymentService] Payment created successfully: {transaction_id}")
        return payment

    async def confirm_payment(self, payment_id: int):
        """Подтверждает платеж"""
        logger.info(f"[PaymentService] Confirming payment {payment_id}")
        payment = await self.payment_repo.get_payment_by_id(payment_id)
        if not payment:
            logger.error(f"[PaymentService] Payment with id {payment_id} not found")
            raise ValueError(f"Payment with id {payment_id} not found")

        payment = await self.payment_repo.update_payment(
            payment_id, {"status": "completed"}
        )

        # Обновляем статус бронирования
        await self.booking_repo.update_booking(
            payment.booking_id, {"status": BookingStatus.CONFIRMED}
        )

        logger.info(f"[PaymentService] Payment {payment_id} confirmed successfully")
        return payment

    async def get_payment(self, payment_id: int):
        logger.info(f"[PaymentService] Getting payment {payment_id}")
        payment = await self.payment_repo.get_payment_by_id(payment_id)
        if not payment:
            logger.error(f"[PaymentService] Payment with id {payment_id} not found")
            raise ValueError(f"Payment with id {payment_id} not found")
        return payment
