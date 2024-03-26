import pytest
from sqlalchemy.orm import Session
from application.config.database import Base, engine
from application.models.users import User
from .test_utils import engine, test_client, override_get_db


def setup_module(module):
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    yield next(override_get_db())


def teardown_module(module):
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db: Session):
    user = User(username="test_user", email="test@example.com", hashed_password="password123")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_delete_own_account_with_valid_credentials(test_user: User, db: Session):
    response = test_client.delete("/remove_my_self", headers={"Authorization": "Bearer ACCESS_TOKEN_HERE"})

    assert response.status_code == 204

    assert not db.query(User).filter_by(username="test_user").first()
