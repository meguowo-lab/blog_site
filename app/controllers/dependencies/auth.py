from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from starlette.status import HTTP_401_UNAUTHORIZED

from ...database import SessionDep
from ...models.account import Account, Session
from ..managers import ModelManager


class LoginRequired:
    async def __call__(
        self, session_uuid: Annotated[UUID, Cookie()], session: SessionDep
    ) -> Session:
        try:
            return await ModelManager(model=Session, session=session).get_one(
                uuid=session_uuid
            )
        except NoResultFound:
            raise HTTPException(HTTP_401_UNAUTHORIZED)


class PermissionsRequired:
    def __init__(self, permissions: list[str]):
        self.permissions = permissions

    async def __call__(
        self,
        acc_session: Annotated[Session, Depends(LoginRequired())],
        session: SessionDep,
    ) -> Account:
        account: Account = await ModelManager(
            model=Account,
            session=session,
            options=[joinedload(Account.permissions)],  # type: ignore
        ).get_one(id=acc_session.account_id)
        acc_permissions = [permission.name for permission in account.permissions]
        for permission in self.permissions:
            if permission not in acc_permissions:
                raise HTTPException(HTTP_401_UNAUTHORIZED)

        return account
