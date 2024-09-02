from typing import Any
from uuid import UUID

from fastapi import HTTPException, Request
from sqladmin import ModelView
from sqlalchemy.orm import joinedload
from starlette.status import HTTP_401_UNAUTHORIZED

from ..controllers.managers.model import ModelManager
from ..database.db import database
from ..models import Account, BlogPost, Comment, Permission, Session


class AccountView(ModelView, model=Account):
    pass


class PermissionsView(ModelView, model=Permission):
    pass


class BlogPostView(ModelView, model=BlogPost):
    form_excluded_columns = ["author", "account"]
    create_template = "/templates/blog_form_create.html"
    edit_template = "/templates/blog_form_edit.html"

    async def on_model_change(
        self, data: dict, model: Any, is_created: bool, request: Request
    ) -> None:
        uuid = request.session.get("session_uuid")
        if uuid is None:
            raise HTTPException(HTTP_401_UNAUTHORIZED)
        uuid = UUID(uuid)

        await database.run_with_session(self._on_model_change, data=data, uuid=uuid)

        return await super().on_model_change(data, model, is_created, request)

    async def _on_model_change(self, session, data, uuid):
        acc_session: Session = await ModelManager(
            model=Session,
            session=session,
            options=[joinedload(Session.account)],  # type: ignore
        ).get_one(uuid=uuid)
        data["author"] = acc_session.account.username
        data["account_id"] = acc_session.account.id

class CommentView(ModelView, model=Comment):
    form_excluded_columns = ["author", "account"]
