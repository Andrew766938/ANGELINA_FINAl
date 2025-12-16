from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.booking import BookingModel


class AirportModel(Base):
    __tablename__ = "airports"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    
    flights_from: Mapped[list["FlightModel"]] = relationship(
        back_populates="departure_airport", foreign_keys="FlightModel.departure_airport_id"
    )
    flights_to: Mapped[list["FlightModel"]] = relationship(
        back_populates="arrival_airport", foreign_keys="FlightModel.arrival_airport_id"
    )


class FlightModel(Base):
    __tablename__ = "flights"
    id: Mapped[int] = mapped_column(primary_key=True)
    flight_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    airline: Mapped[str] = mapped_column(String(50), nullable=False)
    
    departure_airport_id: Mapped[int] = mapped_column(
        ForeignKey("airports.id"), nullable=False
    )
    arrival_airport_id: Mapped[int] = mapped_column(
        ForeignKey("airports.id"), nullable=False
    )
    
    departure_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    departure_airport: Mapped["AirportModel"] = relationship(
        back_populates="flights_from", foreign_keys=[departure_airport_id]
    )
    arrival_airport: Mapped["AirportModel"] = relationship(
        back_populates="flights_to", foreign_keys=[arrival_airport_id]
    )
    bookings: Mapped[list["BookingModel"]] = relationship(back_populates="flight")
