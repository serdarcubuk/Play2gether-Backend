from fastapi import Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from source.app.auth.auth import CurrentUser
from source.app.chat.manager import manager
from source.app.chat.services import get_nickname
from source.core.database import get_db
from source.core.middlewares import CustomAPIRouter

chat_router = CustomAPIRouter(prefix="/chat")


@chat_router.websocket("")
@chat_router.websocket("/")
async def websocket_endpoint(
    user: CurrentUser, websocket: WebSocket, db: AsyncSession = Depends(get_db)
):
    nickname = await get_nickname(user=user, db=db)
    if not nickname:
        return None

    await manager.connect(websocket=websocket, room_id=user.room_id, nickname=nickname)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_message(
                message=f"{nickname}: {data}",
                room_id=user.room_id,
                sender_websocket=websocket,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket=websocket, room_id=user.room_id)
        await manager.broadcast_message(
            message=f"{nickname} left the room",
            room_id=user.room_id,
            sender_websocket=websocket,
        )
