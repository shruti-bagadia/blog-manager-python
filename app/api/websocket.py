from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, msg: dict):
        for ws in list(self.active):
            await ws.send_json(msg)

manager = ConnectionManager()

@router.websocket("/ws/posts/")
async def websocket_posts(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text() #keep connection open
    except WebSocketDisconnect:
        manager.disconnect(ws)