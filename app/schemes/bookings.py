from datetime import datetime
from pydantic import BaseModel, Field
from app.models.booking import BookingStatus


class BookingBase(BaseModel):
    passenger_name: str = Field(..., min_length=1, max_length=100)
    passenger_email: str = Field(..., min_length=1, max_length=100)
    passenger_phone: str = Field(..., min_length=1, max_length=20)
    seats_count: int = Field(..., gt=0)


class BookingCreate(BookingBase):
    flight_id: int


class BookingUpdate(BaseModel):
    status: BookingStatus | None = None


class BookingRead(BookingBase):
    id: int
    booking_number: str
    flight_id: int
    user_id: int
    total_price: float
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingListRead(BaseModel):
    id: int
    booking_number: str
    flight_id: int
    passenger_name: str
    passenger_email: str
    seats_count: int
    total_price: float
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentRead(BaseModel):
    id: int
    booking_id: int
    amount: float
    payment_method: str
    transaction_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
