from uuid import UUID

from fastapi import HTTPException, Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import joinedload
from starlette.status import HTTP_400_BAD_REQUEST

from ..settings import settings

from ..database import database
from ..models import Account
from .dependencies.auth import LoginRequired, PermissionsRequired
from .managers.model import ModelManager


class AuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        data = await request.form()
        return await database.run_with_session(
            self._login, data=data, req=request
        )  # type: ignore
    
    async def _login(self, req: Request, data: dict[str, str], session) -> bool:
        account: Account | None = await ModelManager(
            model=Account,
            options=[joinedload(Account.session)],  # type: ignore
            session=session,
        ).get_one_or_none(username=data["username"])

        if account is None or not account.check_password(data["password"]):
            return False
        
        account.refresh_session()
        account.save(session)
        req.session.update({"session_uuid": str(account.session.uuid)})
        return True

    async def authenticate(self, request: Request):
        uuid = request.session.get("session_uuid")
        if uuid is None:
            raise HTTPException(HTTP_400_BAD_REQUEST)

        uuid = UUID(uuid)
        await database.run_with_session(self._auth, uuid=uuid)
        return True

    async def _auth(self, session, uuid: UUID):
        acc_session = await LoginRequired()(session_uuid=uuid, session=session)
        await PermissionsRequired(["admin"])(acc_session=acc_session, session=session)


auth_backend = AuthBackend(secret_key=settings.secret)
