from typing import Optional
from uuid import UUID

from starlette.websockets import WebSocket


class WebSocketRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.websocket_dic = {}
        return cls._instance

    def add_websocket(self, user_id: UUID, websocket: WebSocket) -> None:
        self.websocket_dic[user_id] = websocket

    def user_websocket(self, user_id: UUID) -> Optional[WebSocket]:
        return self.websocket_dic.get(user_id)

    def remove_websocket(self, user_id: UUID) -> None:
        self.websocket_dic.pop(user_id)
