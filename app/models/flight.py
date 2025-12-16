"""Flight and Airport models"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime


class AirportModel(Base):
    """Airport model"""
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True)
    name = Column(String(255))
    city = Column(String(255))
    country = Column(String(255))
    
    # Relationships
    departing_flights = relationship(
        "FlightModel",
        foreign_keys="FlightModel.departure_airport_id",
        back_populates="departure_airport",
        lazy="selectin"
    )
    arriving_flights = relationship(
        "FlightModel",
        foreign_keys="FlightModel.arrival_airport_id",
        back_populates="arrival_airport",
        lazy="selectin"
    )


class FlightModel(Base):
    """Flight model"""
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(50), unique=True, index=True)
    airline = Column(String(255))
    departure_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey("airports.id"), nullable=False)
    departure_time = Column(DateTime, default=datetime.now)
    arrival_time = Column(DateTime)
    total_seats = Column(Integer, default=180)
    available_seats = Column(Integer, default=180)
    price = Column(Float, default=0.0)
    
    # Relationships
    departure_airport = relationship(
        "AirportModel",
        foreign_keys=[departure_airport_id],
        back_populates="departing_flights",
        lazy="selectin"
    )
    arrival_airport = relationship(
        "AirportModel",
        foreign_keys=[arrival_airport_id],
        back_populates="arriving_flights",
        lazy="selectin"
    )
    bookings = relationship("BookingModel", back_populates="flight", cascade="all, delete-orphan")
