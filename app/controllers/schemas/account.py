from sqlmodel import Field, SQLModel


class AccountSchema(SQLModel):
    username: str = Field(unique=True)
    password: str = Field()
