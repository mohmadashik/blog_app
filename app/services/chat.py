from typing import Dict, Set

from fastapi import WebSocket


class BlogChatManager:
    """
    Simple in-memory chat manager.
    Keeps a set of WebSocket connections per blog_id.
    """

    def __init__(self) -> None:
        self._connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, blog_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        if blog_id not in self._connections:
            self._connections[blog_id] = set()
        self._connections[blog_id].add(websocket)

    def disconnect(self, blog_id: int, websocket: WebSocket) -> None:
        conns = self._connections.get(blog_id)
        if not conns:
            return
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self._connections.pop(blog_id, None)

    async def broadcast(self, blog_id: int, message: str) -> None:
        conns = self._connections.get(blog_id, set())
        to_remove = []
        for ws in conns:
            try:
                await ws.send_text(message)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            conns.discard(ws)


blog_chat_manager = BlogChatManager()
