import os
from functools import lru_cache
from typing import Optional

from pydantic import ValidationError, FilePath, Field
from pydantic.v1 import PydanticValueError
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expire_hours: int = os.getenv("JWT_EXPIRE_HOURS")
    env: str = os.getenv("ENV")
    certfile: Optional[FilePath] = Field(None, description="Path to the certificate file")
    keyfile: Optional[FilePath] = Field(None, description="Path to the key file")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    try:
        return Settings()
    except ValidationError as e:
        raise EnvironmentError(f"Missig environement variables or malformed: {e.errors()}")

    except PydanticValueError as e:
        raise EnvironmentError(f"Invalid value for environment variable: {e}")

    except Exception as e:
        raise EnvironmentError(f"Error loading settings: {e}")