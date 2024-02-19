from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from models.users import User
from repositories.users import UserRepository
from services.security import web_socket_token_interceptor
from services.utils import get_db

router = APIRouter(
    prefix='/ws',
    tags=['websocket']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(web_socket_token_interceptor)]

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, user: user_dependency, db: db_dependency):
    user.set_connection(websocket)
    await user.get_connection().accept()
    user_repository = UserRepository(db)
    await user_repository.send_friend_status(user)

@router.websocket("/me_coucou")
async def get_user_and_send_message(websocket: WebSocket, user: user_dependency):
    print(user)
    await user.get_connection().send_text("coucou {{user.username}}")

# @router.websocket("/say_hello")
# async def send_message(user: user_dependency):
#     (await user.get_websocket()).send_text("hello !")
