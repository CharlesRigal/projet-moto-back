import os
from functools import lru_cache

from pydantic import ValidationError
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expire_hours: int = os.getenv("JWT_EXPIRE_HOURS")
    env: str = os.getenv("ENV")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    try:
        return Settings()
    except ValidationError:
        raise EnvironmentError("Missig environement variables or malformed")
