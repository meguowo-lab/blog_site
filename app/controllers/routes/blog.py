from typing import Annotated

from fastapi import APIRouter, Depends

from ...database.db import SessionDep
from ...models import Account, Comment
from ..dependencies import PermissionsRequired
from ..schemas import CommentSchema

router = APIRouter(prefix="/blog")


@router.post("/comment")
async def post_comment(
    data: CommentSchema,
    account: Annotated[Account, Depends(PermissionsRequired(["comment:write"]))],
    session: SessionDep,
):
    Comment(**data.model_dump(), account=account).save(session)
    return "created"
