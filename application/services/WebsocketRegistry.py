from typing import Optional, Dict, List
from uuid import UUID

from fastapi import WebSocket


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

    def get_websocket_list_from_uuid_list(self, uuid_list: List[UUID]) -> List[WebSocket]:
        return [self.websocket_dic[uuid] for uuid in uuid_list if uuid in self.websocket_dic]
