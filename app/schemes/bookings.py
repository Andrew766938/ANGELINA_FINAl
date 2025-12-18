from datetime import datetime
from pydantic import BaseModel, Field
from app.models.booking import BookingStatus
from app.schemes.flights import FlightListRead


class BookingBase(BaseModel):
    passenger_name: str = Field(..., min_length=1, max_length=150)
    passenger_email: str = Field(..., min_length=1, max_length=150)
    passenger_phone: str = Field(..., min_length=1, max_length=50)  # Increased from 20 to 50
    seats_count: int = Field(..., gt=0, le=9)  # Max 9 seats per booking


class BookingCreate(BookingBase):
    flight_id: int = Field(..., gt=0)


class BookingUpdate(BaseModel):
    status: BookingStatus | None = None


class BookingRead(BookingBase):
    id: int
    booking_number: str
    flight_id: int
    user_id: int
    total_price: float
    status: BookingStatus

    class Config:
        from_attributes = True


class BookingListRead(BaseModel):
    id: int
    booking_number: str
    flight_id: int
    passenger_name: str
    passenger_email: str
    passenger_phone: str
    seats_count: int
    total_price: float
    status: BookingStatus

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    payment_method: str = Field(..., min_length=1, max_length=50)


class PaymentRead(BaseModel):
    id: int
    booking_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str

    class Config:
        from_attributes = True
