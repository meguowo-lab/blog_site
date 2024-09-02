from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlmodel import Field, SQLModel


class Base(SQLModel, AsyncAttrs):
    def save(self, session: AsyncSession):
        session.add(self)

    async def delete(self, session: AsyncSession):
        await session.delete(self)


class UUIDBase(Base):
    uuid: UUID = Field(primary_key=True, default_factory=uuid4)


class IdBase(Base):
    id: int = Field(primary_key=True)
