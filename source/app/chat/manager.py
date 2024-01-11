from fastapi.websockets import WebSocket

rooms: dict = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket, room_id: str, nickname: str):
        await websocket.accept()
        connection_info = {
            "websocket": websocket,
            "room_id": room_id,
            "nickname": nickname,
        }
        self.active_connections.append(connection_info)
        rooms.setdefault(room_id, []).append(connection_info)
        await self.broadcast_message(
            message=f"{nickname} joined the room",
            room_id=room_id,
            sender_websocket=websocket,
        )

    def disconnect(self, websocket: WebSocket, room_id: str):
        connection_info = next(
            (
                conn
                for conn in self.active_connections
                if conn["websocket"] == websocket
            ),
            None,
        )
        if connection_info:
            self.active_connections.remove(connection_info)
            rooms[room_id].remove(connection_info)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    @staticmethod
    async def broadcast_message(
        message: str, room_id: str, sender_websocket: WebSocket
    ):
        for connection in rooms.get(room_id, []):
            if connection["websocket"] != sender_websocket:
                await connection["websocket"].send_text(message)


manager = ConnectionManager()
