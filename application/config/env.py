import os
from functools import lru_cache

from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    database_hostname: str = os.getenv('DATABASE_HOSTNAME')
    database_username: str = os.getenv('DATABASE_USERNAME')
    database_password: str = os.getenv('DATABASE_PASSWORD')
    database_port: str = os.getenv('DATABASE_PORT')
    database_type: str = os.getenv('DATABASE_TYPE')
    database_name: str = os.getenv('DATABASE_NAME')
    jwt_secret_key: str = os.getenv('JWT_SECRET_KEY')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM')
    jwt_expire_hours: int = os.getenv('JWT_EXPIRE_HOURS')
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()