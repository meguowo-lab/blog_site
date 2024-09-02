from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from ...models import Base


class ModelManager[T: Base](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    model: type[T]
    session: AsyncSession
    options: list[ExecutableOption] = []

    def _create_get_query(self, **where):
        return select(self.model).filter_by(**where).options(*self.options)

    async def get(self, **where):
        res = await self.session.execute(self._create_get_query(**where))
        return res.unique()

    async def get_one(self, **where):
        res = await self.get(**where)
        return res.one()[0]

    async def get_one_or_none(self, **where) -> tuple[T] | None:
        res = await self.get(**where)
        row = res.one_or_none()
        if row is None:
            return None

        return row[0]

    async def get_many(self, **where):
        res = await self.get(**where)
        return [row[0] for row in res]
