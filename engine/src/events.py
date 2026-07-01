import asyncio
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger("nhi-dex.events")


class EventManager:
    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []

    async def subscribe(self) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self._subscribers.remove(queue)

    async def broadcast(self, event_type: str, data: dict) -> None:
        message = json.dumps({"type": event_type, "data": data})
        dead = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                dead.append(queue)
        for q in dead:
            self._subscribers.remove(q)
        if self._subscribers:
            logger.debug("Broadcast %s to %d subscribers", event_type, len(self._subscribers))


event_manager = EventManager()
