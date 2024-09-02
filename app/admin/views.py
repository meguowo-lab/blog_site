from typing import Any
from uuid import UUID

from fastapi import HTTPException, Request
from sqladmin import ModelView
from sqlalchemy.orm import joinedload
from starlette.status import HTTP_401_UNAUTHORIZED
from wtforms import TextAreaField

from ..controllers.managers.model import ModelManager
from ..database.db import database
from ..models.account import Account, BlogPostModel, Permission, Session


class AccountView(ModelView, model=Account):
    pass


class PermissionsView(ModelView, model=Permission):
    pass


class BlogPostsView(ModelView, model=BlogPostModel):
    form_excluded_columns = ["author", "account"]
    create_template = "/templates/blog_form_create.html"
    edit_template = "/templates/blog_form_edit.html"

    async def on_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        sessiongen = database.get_session()
        session = await sessiongen.__anext__()
        try:
            uuid = request.session.get("session_uuid")
            if uuid is None:
                raise HTTPException(HTTP_401_UNAUTHORIZED)
            uuid = UUID(uuid)

            acc_session: Session = await ModelManager(
                model=Session, session=session, options=[joinedload(Session.account)]
            ).get_one(uuid=uuid)
            data["author"] = acc_session.account.username
            data["account_id"] = acc_session.account.id
            return await super().on_model_change(data, model, is_created, request)
        except Exception as e:
            await sessiongen.athrow(e)
