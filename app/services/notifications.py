import asyncio
from typing import Any, Dict, List


class NotificationManager:
    """
    Simple in-memory pub/sub for SSE.
    Each subscriber gets its own asyncio.Queue.
    """

    def __init__(self) -> None:
        self._subscribers: List[asyncio.Queue[Dict[str, Any]]] = []

    async def connect(self) -> asyncio.Queue[Dict[str, Any]]:
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def disconnect(self, queue: asyncio.Queue[Dict[str, Any]]) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def publish(self, event: Dict[str, Any]) -> None:
        # fan-out to all subscribers
        for queue in list(self._subscribers):
            await queue.put(event)


notifier = NotificationManager()
