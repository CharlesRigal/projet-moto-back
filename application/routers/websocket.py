from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from websocket import WebSocket

from models.users import User
from services.security import get_current_user
from services.utils import get_db

router = APIRouter(
    prefix='/ws',
    tags=['auth']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

@router.websocket("")
async def connect_websocket(user: user_dependency, websocket: WebSocket) -> None:
    await user.connect(websocket)

@router.websocket("say_hello")
async def send_message(user: user_dependency):
    (await user.get_websocket()).send_text("hello !")



