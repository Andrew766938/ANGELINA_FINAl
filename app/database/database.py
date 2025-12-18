from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.database.base import Base

engine = create_async_engine(settings.get_db_url)

engine_null_pool = create_async_engine(settings.get_db_url, poolclass=NullPool)


async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null_pool = async_sessionmaker(
    bind=engine_null_pool, expire_on_commit=False
)


# 🔥 ОТЛОЖЕННЫЙ ИМПОРТ МОДЕЛЕЙ (для регистрации в Base.metadata)
# это необходимо, чтобы модели открывались только когда этот модуль принустится
def register_models():
    """Отложенный импорт моделей"""
    from app.models.users import UserModel
    from app.models.roles import RoleModel
    from app.models.flight import FlightModel, AirportModel
    from app.models.booking import BookingModel, PaymentModel
