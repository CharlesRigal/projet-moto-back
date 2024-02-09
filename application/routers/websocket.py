from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from models.users import User
from services.security import get_current_user
from services.utils import get_db

router = APIRouter(
    prefix='/ws',
    tags=['websocket']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

@router.websocket("/")
async def connect_websocket(websocket: WebSocket) -> None:
    await websocket.accept(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text("you wrote")


@router.websocket("/say_hello")
async def send_message(user: user_dependency):
    (await user.get_websocket()).send_text("hello !")



