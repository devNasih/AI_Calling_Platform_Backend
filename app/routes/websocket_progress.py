from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import manager

router = APIRouter()

@router.websocket("/v1/ws/campaign-progress")
async def campaign_progress_socket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Just keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
