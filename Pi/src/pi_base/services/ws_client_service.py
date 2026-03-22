import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Optional

from websockets import connect


logger = logging.getLogger(__name__)


class WSClientService:
    def __init__(
        self,
        server_url: str,
        on_message: Callable[[str], Awaitable[None]],
        reconnect_sec: int = 3,
    ) -> None:
        self._server_url = server_url
        self._on_message = on_message
        self._reconnect_sec = reconnect_sec

        self._running = False
        self._conn: Optional[Any] = None
        self._outgoing: asyncio.Queue[str] = asyncio.Queue()

    @property
    def is_connected(self) -> bool:
        return self._conn is not None

    async def start(self) -> None:
        self._running = True
        while self._running:
            if not self._server_url:
                logger.info("WS_SERVER_URL is empty. Remote websocket layer is disabled.")
                await asyncio.sleep(self._reconnect_sec)
                continue

            try:
                async with connect(self._server_url) as websocket:
                    self._conn = websocket
                    logger.info("Connected remote websocket: %s", self._server_url)

                    recv_task = asyncio.create_task(self._recv_loop(websocket))
                    send_task = asyncio.create_task(self._send_loop(websocket))

                    done, pending = await asyncio.wait(
                        {recv_task, send_task},
                        return_when=asyncio.FIRST_EXCEPTION,
                    )
                    for task in pending:
                        task.cancel()
                    for task in done:
                        task.result()
            except Exception as exc:
                logger.warning("Remote websocket reconnect in %ss due to error: %s", self._reconnect_sec, exc)
                await asyncio.sleep(self._reconnect_sec)
            finally:
                self._conn = None

    async def stop(self) -> None:
        self._running = False

    async def send_json(self, payload: dict[str, Any]) -> None:
        await self._outgoing.put(json.dumps(payload, ensure_ascii=True))

    async def send_text(self, data: str) -> None:
        await self._outgoing.put(data)

    async def _recv_loop(self, websocket: Any) -> None:
        async for message in websocket:
            if isinstance(message, bytes):
                text = message.decode("utf-8", errors="ignore")
            else:
                text = str(message)
            await self._on_message(text)

    async def _send_loop(self, websocket: Any) -> None:
        while self._running and self._conn is websocket:
            data = await self._outgoing.get()
            await websocket.send(data)
