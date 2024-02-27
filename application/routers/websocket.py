from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from models.users import User
from repositories.users import UserRepository
from services.security import web_socket_token_interceptor
from services.utils import get_db
from services.WebsocketRegistry import WebSocketRegistry

router = APIRouter(prefix="/ws", tags=["websocket"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(web_socket_token_interceptor)]
websocket_registry = WebSocketRegistry()


@router.websocket("")
async def websocket_connect(user: user_dependency, db: db_dependency):
    user_repository = UserRepository(db)
    try:
        for friend in user_repository.get_friends_as_user(user):
            if websocket_registry.connection_is_active(friend.id):
                await websocket_registry.get_websocket_by_user_uuid(
                    friend.id
                ).send_text(f"user {user.username} connected !")
                await user.websocket.send_text(f"friend {friend.username} is connected")
            else:
                await user.websocket.send_text(
                    f"friend {friend.username} not connected"
                )
        while True:
            await user.websocket.receive_text()
    except WebSocketDisconnect:
        del user.websocket
