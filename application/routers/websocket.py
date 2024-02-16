from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session

from services.security import get_current_user
from services.utils import get_db

router = APIRouter(
    prefix='/ws',
    tags=['websocket']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    print(websocket)
    #user = get_current_user(websocket.headers["Authorization"], db_dependency)
    token = websocket.headers['Authorization']
    print(token)

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        await websocket.send_text(str(e))
    token.split()

# @router.websocket("/say_hello")
# async def send_message(user: user_dependency):
#     (await user.get_websocket()).send_text("hello !")



