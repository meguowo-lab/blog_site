from hashlib import sha256
from uuid import uuid4

from pydantic import model_validator
from sqlmodel import Field, Relationship

from ..controllers.schemas import AccountSchema, CommentSchema
from .base import Base, IdBase, UUIDBase


class AccountPermissionLink(Base, table=True):
    account_id: int = Field(
        foreign_key="account.id", primary_key=True, ondelete="CASCADE"
    )
    permission_id: int = Field(
        foreign_key="permission.id", primary_key=True, ondelete="CASCADE"
    )


class Account(IdBase, AccountSchema, table=True):
    session: "Session" = Relationship(back_populates="account")
    permissions: list["Permission"] = Relationship(link_model=AccountPermissionLink)
    posts: list["BlogPost"] = Relationship(back_populates="account")
    comments: list["Comment"] = Relationship(back_populates="account")

    def set_password(self, password: str):
        self.password = sha256(password.encode()).hexdigest()

    def check_password(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    def refresh_session(self):
        uuid = uuid4()
        if self.session is not None:
            self.session.uuid = uuid
        else:
            self.session = Session(account_id=self.id, uuid=uuid)


class Permission(IdBase, table=True):
    name: str = Field(unique=True, nullable=False)


class Session(UUIDBase, table=True):
    account_id: int = Field(foreign_key="account.id", ondelete="CASCADE", unique=True)
    account: Account = Relationship(back_populates="session")


class BlogPost(IdBase, table=True):
    name: str
    title: str
    info: str
    author: str | None
    account_id: int = Field(foreign_key="account.id", ondelete="CASCADE")
    account: Account = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(back_populates="post")

    @model_validator(mode="after")
    def auto_author(self):
        self.author = self.account.username
        return self


class Comment(IdBase, CommentSchema, table=True):
    account_id: int = Field(foreign_key="account.id", ondelete="CASCADE")
    account: Account = Relationship(back_populates="comments")
    author: str | None
    post: BlogPost = Relationship(back_populates="comments")

    @model_validator(mode="after")
    def auto_author(self):
        self.author = self.account.username
        return self
