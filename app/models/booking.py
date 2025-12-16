from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import enum

if TYPE_CHECKING:
    from app.models.users import UserModel
    from app.models.flight import FlightModel


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingModel(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), nullable=False)
    
    passenger_name: Mapped[str] = mapped_column(String(150), nullable=False)  # Increased from 100 to 150
    passenger_email: Mapped[str] = mapped_column(String(150), nullable=False)  # Increased from 100 to 150
    passenger_phone: Mapped[str] = mapped_column(String(50), nullable=False)  # Increased from 20 to 50
    
    seats_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[float] = mapped_column(nullable=False)
    
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), default=BookingStatus.PENDING
    )
    
    user: Mapped["UserModel"] = relationship(back_populates="bookings")
    flight: Mapped["FlightModel"] = relationship(back_populates="bookings")
    payment: Mapped["PaymentModel"] = relationship(back_populates="booking", uselist=False)


class PaymentModel(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    
    amount: Mapped[float] = mapped_column(nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    
    transaction_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    
    booking: Mapped["BookingModel"] = relationship(back_populates="payment")
