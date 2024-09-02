from typing import Annotated, Any, Callable

from fastapi import Depends, HTTPException
from sqlalchemy import URL
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.status import HTTP_404_NOT_FOUND

from ..settings import settings


class Database:
    def __init__(self) -> None:
        self.url = URL(
            **settings.database.model_dump(),
            query={},  # type: ignore
        )
        self.engine = create_async_engine(self.url)
        self.sessionmaker = async_sessionmaker(bind=self.engine)

    async def get_session(self):
        async with self.sessionmaker.begin() as session:
            try:
                yield session
            except NoResultFound:
                raise HTTPException(HTTP_404_NOT_FOUND, "No result was found!")

    async def run_with_session(self, func: Callable[..., Any], *args, **kwargs):
        sess_gen = database.get_session()
        session = await sess_gen.__anext__()
        try:
            res = await func(session=session, *args, **kwargs)
            try:
                await sess_gen.__anext__()
            except:
                pass
            return res
        except Exception as e:
            await sess_gen.athrow(e)


database = Database()
SessionDep = Annotated[AsyncSession, Depends(database.get_session)]
