from datetime import datetime
from pydantic import BaseModel, Field


class AirportBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3)
    name: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)


class AirportCreate(AirportBase):
    pass


class AirportRead(AirportBase):
    id: int

    class Config:
        from_attributes = True


class FlightBase(BaseModel):
    flight_number: str = Field(..., min_length=1, max_length=20)
    airline: str = Field(..., min_length=1, max_length=50)
    departure_airport_id: int
    arrival_airport_id: int
    departure_time: datetime
    arrival_time: datetime
    total_seats: int = Field(..., gt=0)
    available_seats: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    available_seats: int | None = None
    price: float | None = None


class FlightRead(FlightBase):
    id: int
    departure_airport: AirportRead
    arrival_airport: AirportRead

    class Config:
        from_attributes = True


class FlightListRead(BaseModel):
    id: int
    flight_number: str
    airline: str
    departure_airport: AirportRead
    arrival_airport: AirportRead
    departure_time: datetime
    arrival_time: datetime
    available_seats: int
    price: float

    class Config:
        from_attributes = True
