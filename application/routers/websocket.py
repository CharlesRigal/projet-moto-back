from typing import Annotated

from fastapi import APIRouter, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session

from models.routes import Route
from models.users import User
from repositories.users import UserRepository
from repositories.routes import RouteRepository
from services.security import web_socket_token_interceptor
from services.utils import get_db
from services.WebsocketRegistry import WebSocketRegistry

router = APIRouter(prefix="/ws", tags=["websocket"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(web_socket_token_interceptor)]
websocket_registry = WebSocketRegistry()

async def send_message_to_users_list(users: list[User],dict_for_json: dict):
    for user in users:
        await user.websocket.send_json(dict_for_json)


async def send_message_to_friends(user: User, dict_for_json: dict, db: db_dependency):
    user_repository = UserRepository(db)
    await send_message_to_users_list(user_repository.get_connected_friends(user), dict_for_json)

async def send_message_to_other_user_of_route_exept_sender(user: User, route: Route, dict_for_json: dict):
    await send_message_to_users_list([member for member in route.members if member != user], dict_for_json)



@router.websocket("")
async def websocket_connect(user: user_dependency, db: db_dependency):
    user_repository = UserRepository(db)
    try:
        for friend in user_repository.get_friends_as_user(user):
            if websocket_registry.connection_is_active(friend.id):
                await friend.websocket.send_json({"user-uuid": str(user.id), "status": 1})
                await user.websocket.send_json({"user-uuid": str(friend.id), "status": 1})
            else:
                await user.websocket.send_json({"user-uuid": str(friend.id), "status": 0})
        while True:
            data = await user.websocket.receive_json()
            print(data)
    except WebSocketDisconnect:
        await send_message_to_friends(user, {"user-uuid": str(user.id), "status": 0}, db)
        del user.websocket
