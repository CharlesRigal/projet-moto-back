from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from config.env import get_settings
from exceptions.general import InvalidJWTError
from models.users import User
from repositories.users import UserRepository
from services.utils import get_db

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = get_settings().jwt_secret_key
ALGORITHM = get_settings().jwt_algorithm
DELTA_HOURS = get_settings().jwt_expire_hours
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/signin')

db_dependency = Annotated[Session, Depends(get_db)]
def get_current_user(
        token: Annotated[str, Depends(oauth2_bearer)],
        db: db_dependency
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        user_id: str = payload.get('id')
        if email is None or user_id is None:
            raise InvalidJWTError()
        user_repository = UserRepository(db)
        user = user_repository.get_user_by_id(user_id)
        return user
    except JWTError:
        raise InvalidJWTError()

user_dependency = Annotated[dict, Depends(get_current_user)]


def get_current_user_admin(user: user_dependency):
    if user.role == 'admin':
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_jwt(user: User, expires_delta: timedelta):
    encode = {'sub': user.email, 'id': str(user.id), 'role': user.role}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
