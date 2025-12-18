"""SQLAdmin configuration for admin panel at /admin"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView
from app.config import settings
from app.models.users import UserModel
from app.models.roles import RoleModel
from app.models.flight import FlightModel, AirportModel
from app.models.booking import BookingModel


# Create sync engine for SQLAdmin (SQLAdmin doesn't support async yet)
engine = create_engine(
    str(settings.get_db_url).replace('aiosqlite', 'sqlite'),
    echo=False
)


class UserAdmin(ModelView, model=UserModel):
    """Админ-панель для управления пользователями"""
    column_list = [UserModel.id, UserModel.name, UserModel.email, UserModel.role]
    column_details_list = [UserModel.id, UserModel.name, UserModel.email, UserModel.hashed_password, UserModel.role]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class RoleAdmin(ModelView, model=RoleModel):
    """Админ-панель для управления ролями"""
    column_list = [RoleModel.id, RoleModel.name]
    name = "Роль"
    name_plural = "Роли"
    icon = "fa-solid fa-lock"


class FlightAdmin(ModelView, model=FlightModel):
    """Админ-панель для управления рейсами"""
    column_list = [
        FlightModel.id,
        FlightModel.flight_number,
        FlightModel.airline,
        FlightModel.departure_airport,
        FlightModel.arrival_airport,
        FlightModel.price,
        FlightModel.available_seats,
    ]
    column_details_list = [
        FlightModel.id,
        FlightModel.flight_number,
        FlightModel.airline,
        FlightModel.departure_airport,
        FlightModel.arrival_airport,
        FlightModel.departure_time,
        FlightModel.price,
        FlightModel.total_seats,
        FlightModel.available_seats,
    ]
    name = "Рейс"
    name_plural = "Рейсы"
    icon = "fa-solid fa-plane"
    page_size = 20


class AirportAdmin(ModelView, model=AirportModel):
    """Админ-панель для управления аэропортами"""
    column_list = [AirportModel.id, AirportModel.code, AirportModel.name, AirportModel.city, AirportModel.country]
    column_details_list = [AirportModel.id, AirportModel.code, AirportModel.name, AirportModel.city, AirportModel.country]
    name = "Аэропорт"
    name_plural = "Аэропорты"
    icon = "fa-solid fa-location-dot"


class BookingAdmin(ModelView, model=BookingModel):
    """Админ-панель для управления бронированиями"""
    column_list = [
        BookingModel.id,
        BookingModel.booking_number,
        BookingModel.flight_id,
        BookingModel.passenger_name,
        BookingModel.seats_count,
        BookingModel.status,
    ]
    column_details_list = [
        BookingModel.id,
        BookingModel.booking_number,
        BookingModel.flight_id,
        BookingModel.passenger_name,
        BookingModel.passenger_email,
        BookingModel.passenger_phone,
        BookingModel.seats_count,
        BookingModel.total_price,
        BookingModel.status,
        BookingModel.created_at,
    ]
    name = "Бронирование"
    name_plural = "Бронирования"
    icon = "fa-solid fa-ticket"
    page_size = 25


def setup_admin(app):
    """
    Настройка SQLAdmin панели для FastAPI приложения
    
    Args:
        app: FastAPI приложение
    """
    admin = Admin(
        app=app,
        engine=engine,
        title="✈️ Крылья - Админ-панель",
        base_url="/admin",
        logo_url="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext x='50' y='70' font-size='80' text-anchor='middle'%3E✈️%3C/text%3E%3C/svg%3E"
    )
    
    # Регистрируем все админ-модели
    admin.register_model(UserAdmin)
    admin.register_model(RoleAdmin)
    admin.register_model(FlightAdmin)
    admin.register_model(AirportAdmin)
    admin.register_model(BookingAdmin)
    
    return admin
