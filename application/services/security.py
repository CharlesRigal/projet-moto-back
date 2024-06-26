import logging
from datetime import timedelta, datetime
from sqlite3 import DatabaseError
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, WebSocketException, WebSocket, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from config.env import get_settings
from exceptions.general import InvalidJWTError, SelectNotFoundError
from models.users import User
from repositories.users import UserRepository
from services.WebsocketRegistry import WebSocketRegistry
from services.utils import get_db

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = get_settings().jwt_secret_key
ALGORITHM = get_settings().jwt_algorithm
DELTA_HOURS = get_settings().jwt_expire_hours
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v0.1/auth/signin")

db_dependency = Annotated[Session, Depends(get_db)]
websocket_registry = WebSocketRegistry()


async def web_socket_token_interceptor(
    websocket: WebSocket,
    db: db_dependency,
    authorization: str = Query(..., alias="token"),
) -> User:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise WebSocketException(
                status.WS_1008_POLICY_VIOLATION, "Invalid authentication scheme"
            )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        try:
            user = UserRepository(db).get_user_by_id(user_id=payload.get("id"))
        except DatabaseError:
            logging.info(f"error on get user in database {payload}")
            raise InvalidJWTError()
        user.websocket = websocket
        await user.websocket.accept()
        return user

    except (ValueError, IndexError, JWTError):
        raise WebSocketException(status.WS_1008_POLICY_VIOLATION, "Invalid token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: UUID = payload.get("id")
        if email is None or user_id is None:
            raise InvalidJWTError()
        user_repository = UserRepository(db)
        try:
            user = user_repository.get_user_by_id(user_id)
            return user
        except Exception:
            logging.info(f"Error on request loggin for user {payload}")
            raise InvalidJWTError()
    except JWTError:
        raise InvalidJWTError()
    except SelectNotFoundError:
        raise InvalidJWTError()


user_dependency = Annotated[dict, Depends(get_current_user)]


def get_current_user_admin(user: user_dependency):
    if user.role == "admin":
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
    )


def authenticate_user(db: Session, email: str, password: str):
    try:
        user = db.query(User).filter(User.email == email).first()
    except DatabaseError:
        logging.info(f"error on get user in database {email}")
        raise InvalidJWTError()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_jwt(user: User, expires_delta: timedelta):
    encode = {"sub": user.email, "id": str(user.id), "role": user.role}
    expires = datetime.now() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
