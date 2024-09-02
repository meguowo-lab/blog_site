from sqlmodel import Field, SQLModel


class CommentSchema(SQLModel):
    text: str
    post_id: int = Field(foreign_key="blogpost.id", ondelete="CASCADE")
