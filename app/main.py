from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Messenger")


class ConnectionManager:
    """Keeps track of active WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: str) -> None:
        for ws in list(self.active):
            await ws.send_text(message)


manager = ConnectionManager()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.websocket("/ws/{username}")
async def chat(ws: WebSocket, username: str) -> None:
    await manager.connect(ws)
    await manager.broadcast(f"{username} приєднався до чату")
    try:
        while True:
            text = await ws.receive_text()
            await manager.broadcast(f"{username}: {text}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
        await manager.broadcast(f"{username} вийшов з чату")
