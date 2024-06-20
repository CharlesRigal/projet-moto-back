import logging
from json import JSONDecodeError
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session

from models.routes import Route
from models.users import User
from repositories.users import UserRepository
from services.security import web_socket_token_interceptor
from services.utils import get_db
from services.WebsocketRegistry import WebSocketRegistry

router = APIRouter(prefix="/ws", tags=["websocket"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(web_socket_token_interceptor)]
websocket_registry = WebSocketRegistry()


async def send_message_to_users_list(users: list[User], dict_for_json: dict):
    user_names = [user.username for user in users]
    logging.info(f"send websocket to users list: {', '.join(user_names)}")
    for user in users:
        try:
            if websocket_registry.connection_is_active(user.id):
                await user.websocket.send_json(dict_for_json)
                logging.info(
                    f"send message to {user.username} with content : {dict_for_json}"
                )
        except RuntimeError:
            logging.info(
                f"log: user {user.username} have an closed websocket but we try to send ws: {dict_for_json}"
            )


async def send_message_to_connected_friends(
    user: User, dict_for_json: dict, db: db_dependency
):
    user_repository = UserRepository(db)
    connected_friends = user_repository.get_connected_friends(user)
    logging.info(
        f"send message to {user.username} connected friends[{connected_friends}]"
    )
    await send_message_to_users_list(connected_friends, dict_for_json)


async def send_message_to_other_user_of_route_except_sender(
    user: User, route: Route, dict_for_json: dict
):

    await send_message_to_users_list(
        [member for member in route.members + [route.owner] if member != user],
        dict_for_json,
    )


@router.websocket("")
async def websocket_connect(user: user_dependency, db: db_dependency):
    """
    WebSocket endpoint for connecting users.

    Establishes a WebSocket connection for the user and sends status messages to their friends.

    Args:
        user (User): The authenticated user connecting to the WebSocket.
        db (Session): The database session.

    Raises:
        WebSocketDisconnect: If the WebSocket connection is unexpectedly terminated.

    Returns:
        None

    WebSocket messages:
        - Upon connection, sends status messages to the user's friends indicating their connection status.
        - Listens for incoming JSON messages from the user.
        - Upon Route Update, sends route uuid to the member's of the route except sender
    """
    user_repository = UserRepository(db)
    try:
        for friend in user_repository.get_friends_as_user(user):
            if websocket_registry.connection_is_active(friend.id):
                await friend.websocket.send_json(
                    {"user-uuid": str(user.id), "status": 1}
                )
                await user.websocket.send_json(
                    {"user-uuid": str(friend.id), "status": 1}
                )
            else:
                await user.websocket.send_json(
                    {"user-uuid": str(friend.id), "status": 0}
                )
        while True:
            try:
                json = await user.websocket.receive_json()
                await user.websocket.send_json(json)
                logging.info(f"websocket message from {user.username}")
            except JSONDecodeError:
                await user.websocket.send_json({"error": "malformed JSON"})
    except WebSocketDisconnect:
        logging.info(f"websocket disconnected {user.username}")
        await send_message_to_connected_friends(
            user, {"user-uuid": str(user.id), "status": 0}, db
        )
        del user.websocket
