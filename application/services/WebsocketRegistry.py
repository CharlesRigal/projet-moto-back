from typing import Optional, Dict
from uuid import UUID

from fastapi import WebSocket



class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}

    async def connect(self, uuid: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[uuid] = websocket

    def disconnect(self, uuid: UUID) -> None:
        del self.active_connections[uuid]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_message_to_user(self, message: str, uuid: UUID):
        if uuid in self.active_connections:
            await self.send_personal_message(message, self.active_connections[uuid])
            return True
        else:
            return False
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


class WebSocketRegistry:
    _instance: Optional["WebSocketRegistry"] = None

    def __new__(cls) -> "WebSocketRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.websocket_dic: Dict[UUID, WebSocket] = {}
        return cls._instance

    def connection_is_active(self, uuid: UUID) -> bool:
        return uuid in self.websocket_dic

    def add_websocket(self, user_id: UUID, websocket: WebSocket) -> None:
        self.websocket_dic[user_id] = websocket

    def get_websocket_by_user_uuid(self, user_uuid: UUID) -> Optional[WebSocket]:
        return self.websocket_dic.get(user_uuid)

    def remove_websocket(self, user_id: UUID) -> None:
        if user_id in self.websocket_dic:
            del self.websocket_dic[user_id]
