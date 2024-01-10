from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from dto.auth import CreateUserRequest, Token, PasswordResetRequest
from models.users import User
from repositories.users import UserRepository
from services.security import authenticate_user, create_jwt
from services.utils import get_db
from fastapi.security import OAuth2PasswordRequestForm
from config.env import get_settings
from services.security import get_current_user

router = APIRouter(
    prefix='/api/v1/auth',
    tags=['auth']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

SECRET_KEY = get_settings().jwt_secret_key
ALGORITHM = get_settings().jwt_algorithm
DELTA_HOURS = get_settings().jwt_expire_hours
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    """
    Crée un compte utilisateur
    """
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_email(create_user_request.email)
    if user:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={'details': [{
            "type": 'already_used',
            "loc": [
                "body",
                "email"
            ],
            "msg": "Already used",
            'input': create_user_request.model_dump()
        }]})

    user = user_repository.get_user_by_username(create_user_request.username)
    if user:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={'details': [{
            "type": 'already_used',
            "loc": [
                "body",
                "username"
            ],
            "msg": "Already used",
            'input': create_user_request.model_dump()
        }]})

    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    user_repository.create(create_user_model)
    return {'success': True}


@router.post("/signin", status_code=status.HTTP_200_OK, response_model=Token)
def login_for_jwt(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                  db: db_dependency):
    """
    Vérifies les identifiants de l'utilisateur et récupère le Token JWT.
    Le champs "username" correspond à l'e-mail !!
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect")
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_email(form_data.username)
    token = create_jwt(user, timedelta(hours=DELTA_HOURS))
    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/me", status_code=status.HTTP_200_OK)
def get_connected_user(current_user: user_dependency, db: db_dependency):
    """
    Récupère les infos de l'utilisateur courant.
    À utiliser comme guard.
    """
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_id(current_user.get('id'))
    del user.hashed_password
    return user


@router.get('/username/{username}', status_code=status.HTTP_204_NO_CONTENT)
def username_exists(db: db_dependency, username: str):
    """
    Vérifie si le nom d'utilisateur est disponible.
    À utiliser dans le formulaire d'inscription.
    404 : dispo,
    204: pas dispo
    """
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# @router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
# async def change_password(user: user_dependency, db: db_dependency, password_request: PasswordResetRequest):
#     user_repository = UserRepository(db)
#     user_model = user_repository.get_by_id(user.get('id'))
#     if not bcrypt_context.verify(password_request.old_password, user_model.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password")
#     user_model.hashed_password = bcrypt_context.hash(password_request.new_password)
#     user_repository.update(user_model) # NOT TESTED !!!
