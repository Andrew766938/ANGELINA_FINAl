from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import async_session_maker
from app.repositories.roles import RolesRepository
from app.repositories.users import UsersRepository


class DBManager:
    def __init__(self, session_factory: async_session_maker):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        # TODO Добавить сюда созданные репозитории
        # Пример:
        self.users = UsersRepository(self.session)
        self.roles = RolesRepository(self.session)
        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()


async def get_db_session() -> AsyncSession:
    """Get database session for dependency injection"""
    async with async_session_maker() as session:
        yield session
