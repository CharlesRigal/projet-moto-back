from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from models.users import User
from services.security import web_socket_token_interceptor
from services.utils import get_db

router = APIRouter(
    prefix='/ws',
    tags=['websocket']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(web_socket_token_interceptor)]

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, user: user_dependency):
    await user.set_connection(websocket)
    try:
        while True:
            data = await user.get_connection().receive_text()
            await user.get_connection().send_text(f"Message text was: {data} as : {user}")
    except Exception as e:
        await websocket.send_text(str(e))

# @router.websocket("/say_hello")
# async def send_message(user: user_dependency):
#     (await user.get_websocket()).send_text("hello !")
