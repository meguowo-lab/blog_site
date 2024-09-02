from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Cookie, Form, HTTPException, Request, Response
from starlette.status import HTTP_404_NOT_FOUND

from ...database import SessionDep
from ...models import Account, Session
from .._auth_backend import auth_backend
from ..managers import ModelManager
from ..schemas import AccountSchema

router: APIRouter = APIRouter(prefix="/auth")


@router.post("/login")
async def login(
    req: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]
):
    if not await auth_backend.login(req):
        raise HTTPException(HTTP_404_NOT_FOUND)
    return "logged in!"


@router.post("/register")
def register(data: AccountSchema, session: SessionDep):
    account = Account(**data.model_dump())
    account.set_password(data.password)
    account.save(session=session)
    return "created account!"


@router.post("/logout")
async def logout(
    req: Request, session_uuid: Annotated[UUID, Cookie()], session: SessionDep
):
    acc_session: Session = await ModelManager(model=Session, session=session).get_one(
        uuid=session_uuid
    )
    await acc_session.delete(session)
    req.session.pop("session_uuid")
    return "logged out!"
