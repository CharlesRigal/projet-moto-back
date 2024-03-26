import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from sqlalchemy.sql import text
from ..main import app
from ..config.database import Base
from ..services.utils import get_db

load_dotenv()

SQLALCHEMY_DATABASE_URL = f"postgresql://{os.environ.get('TEST_DATABASE_USER')}:{os.environ.get('TEST_DATABASE_PASSWORD')}@localhost:5433/testdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def purge_database():
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(text(f"IF EXISTS DELETE FROM {table.name};"))
        connection.commit()


@pytest.fixture(autouse=True)
def setup():
    purge_database()


app.dependency_overrides[get_db] = override_get_db

test_client = TestClient(app)
