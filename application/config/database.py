from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config.env as env

env_values = env.get_settings()
database_type = env_values.database_type
database_username = env_values.database_username
database_password = env_values.database_password
database_hostname = env_values.database_hostname
database_port = env_values.database_port
database_name = env_values.database_name
SQLALCHEMY_DATABASE_URL = f'{database_type}://{database_username}:{database_password}@{database_hostname}:{database_port}/{database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

