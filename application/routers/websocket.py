from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from models.users import User
from repositories.users import UserRepository
from services.security import web_socket_token_interceptor
from services.utils import get_db
from services.WebsocketRegistry import WebSocketRegistry

router = APIRouter(
    prefix='/ws',
    tags=['websocket']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(web_socket_token_interceptor)]
websocket_registry = WebSocketRegistry()

@router.websocket("")
async def websocket_connect(user: user_dependency, db: db_dependency):
    user_repository = UserRepository(db)
    for friend in user_repository.get_friends_as_user(user):
        try:
            friend_websocket = websocket_registry.get_websocket_by_user_uuid(friend.id)
            if friend_websocket is not None:
                #await friend_websocket.send_text("Hello")
                friend_websocket = websocket_registry.get_websocket_by_user_uuid(friend.id)
                user_websocket = user.get_connection()
                user_websocket.send_text()
                await friend_websocket.send_text("Hello")
            else:
                await user.get_connection().send_text(f"{friend.username} is not connected")
        except WebSocketDisconnect:
            print("WebSocket disconnected for friend:", friend)
        except Exception as e:
            print(f"friend connection {friend.get_connection()}")

@router.websocket("/me_coucou")
async def get_user_and_send_message(websocket: WebSocket, user: user_dependency):
    print(user)
    await user.get_connection().send_text("coucou {{user.username}}")

# @router.websocket("/say_hello")
# async def send_message(user: user_dependency):
#     (await user.get_websocket()).send_text("hello !")
