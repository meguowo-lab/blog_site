from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(".env")


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="db_")
    drivername: str
    username: str
    password: str
    host: str
    port: int
    database: str = Field(alias="DB_NAME")


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()  # type: ignore
    secret: str


settings = Settings()  # type: ignore
