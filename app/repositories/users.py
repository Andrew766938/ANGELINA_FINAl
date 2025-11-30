from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.users import UserModel
from app.repositories.base import BaseRepository
from app.schemes.users import SUserGet, SUserGetWithRels


class UsersRepository(BaseRepository):
    model = UserModel
    schema = SUserGet

    async def get_one_or_none_with_role(self, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
            .options(selectinload(self.model.role))
        )

        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None
        print(model.role.name)
        result = SUserGetWithRels.model_validate(model, from_attributes=True)
        return result
