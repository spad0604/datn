import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from websockets import connect


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StompMessage:
    command: str
    headers: dict[str, str]
    body: str


def _build_frame(command: str, headers: dict[str, str], body: str = "") -> str:
    header_lines = [f"{k}:{v}" for k, v in headers.items()]
    return command + "\n" + "\n".join(header_lines) + "\n\n" + body + "\x00"


def _parse_frames(buffer: str) -> tuple[list[StompMessage], str]:
    # STOMP frames are terminated by NULL (\x00). Heartbeats can be a single '\n'.
    messages: list[StompMessage] = []

    while True:
        nul = buffer.find("\x00")
        if nul < 0:
            return messages, buffer

        raw = buffer[:nul]
        buffer = buffer[nul + 1 :]

        raw = raw.lstrip("\n")
        if not raw:
            continue

        head, sep, body = raw.partition("\n\n")
        if not sep:
            continue

        lines = head.split("\n")
        command = lines[0].strip()
        headers: dict[str, str] = {}
        for line in lines[1:]:
            if not line or ":" not in line:
                continue
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()

        messages.append(StompMessage(command=command, headers=headers, body=body))


class StompClientService:
    def __init__(
        self,
        server_url: str,
        on_message: Callable[[StompMessage], Awaitable[None]],
        reconnect_sec: int = 3,
        subscribe_destinations: Optional[list[str]] = None,
        default_send_destination: str = "/app/update-location",
    ) -> None:
        self._server_url = server_url
        self._on_message = on_message
        self._reconnect_sec = reconnect_sec
        self._subscribe_destinations = subscribe_destinations or []
        self._default_send_destination = default_send_destination

        self._running = False
        self._conn: Optional[Any] = None
        self._outgoing: asyncio.Queue[tuple[str, str, str]] = asyncio.Queue()

        # Hard-coded liveness checks for demo/dev: log ping/pong.
        self._ping_interval_sec = 10
        self._ping_timeout_sec = 5

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
                async with connect(
                    self._server_url,
                    subprotocols=["v12.stomp", "v11.stomp", "v10.stomp"],
                    ping_interval=None,
                    ping_timeout=None,
                ) as websocket:
                    self._conn = websocket
                    logger.info("Connected STOMP websocket: %s", self._server_url)

                    await self._stomp_connect(websocket)
                    await self._stomp_subscribe_all(websocket)

                    recv_task = asyncio.create_task(self._recv_loop(websocket))
                    send_task = asyncio.create_task(self._send_loop(websocket))
                    ping_task = asyncio.create_task(self._ping_loop(websocket))

                    done, pending = await asyncio.wait(
                        {recv_task, send_task, ping_task},
                        return_when=asyncio.FIRST_EXCEPTION,
                    )
                    for task in pending:
                        task.cancel()
                    for task in done:
                        task.result()
            except Exception as exc:
                logger.warning("STOMP websocket reconnect in %ss due to error: %s", self._reconnect_sec, exc)
                await asyncio.sleep(self._reconnect_sec)
            finally:
                self._conn = None

    async def stop(self) -> None:
        self._running = False

    async def send_json(self, payload: dict[str, Any]) -> None:
        await self.send_json_to(self._default_send_destination, payload)

    async def send_json_to(self, destination: str, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=True)
        await self._outgoing.put((destination, body, "application/json"))

    async def send_text(self, data: str) -> None:
        await self._outgoing.put((self._default_send_destination, data, "text/plain"))

    async def _stomp_connect(self, websocket: Any) -> None:
        frame = _build_frame(
            "CONNECT",
            {
                "accept-version": "1.2",
                "host": "localhost",
                "heart-beat": "0,0",
            },
        )
        await websocket.send(frame)

        # Wait for CONNECTED
        buffer = ""
        while True:
            chunk = await websocket.recv()
            if isinstance(chunk, bytes):
                buffer += chunk.decode("utf-8", errors="ignore")
            else:
                buffer += str(chunk)
            frames, buffer = _parse_frames(buffer)
            for msg in frames:
                if msg.command == "CONNECTED":
                    logger.info("STOMP connected")
                    return
                if msg.command == "ERROR":
                    raise RuntimeError(f"STOMP ERROR: {msg.body}")

    async def _stomp_subscribe_all(self, websocket: Any) -> None:
        for idx, destination in enumerate(self._subscribe_destinations):
            frame = _build_frame(
                "SUBSCRIBE",
                {
                    "id": f"sub-{idx}",
                    "destination": destination,
                    "ack": "auto",
                },
            )
            await websocket.send(frame)
            logger.info("STOMP subscribed: %s", destination)

    async def _recv_loop(self, websocket: Any) -> None:
        buffer = ""
        async for chunk in websocket:
            if isinstance(chunk, bytes):
                buffer += chunk.decode("utf-8", errors="ignore")
            else:
                buffer += str(chunk)

            frames, buffer = _parse_frames(buffer)
            for msg in frames:
                if msg.command == "MESSAGE":
                    await self._on_message(msg)
                elif msg.command == "ERROR":
                    raise RuntimeError(f"STOMP ERROR: {msg.body}")

    async def _send_loop(self, websocket: Any) -> None:
        while self._running and self._conn is websocket:
            destination, body, content_type = await self._outgoing.get()

            headers = {
                "destination": destination,
                "content-type": content_type,
                "content-length": str(len(body.encode("utf-8"))),
            }
            frame = _build_frame("SEND", headers, body)
            await websocket.send(frame)

    async def _ping_loop(self, websocket: Any) -> None:
        # Send explicit websocket PING frames and log PONG replies.
        while self._running and self._conn is websocket:
            await asyncio.sleep(self._ping_interval_sec)
            try:
                logger.info("WS ping -> %s", self._server_url)
                pong_waiter = websocket.ping()
                await asyncio.wait_for(pong_waiter, timeout=self._ping_timeout_sec)
                logger.info("WS pong <- %s", self._server_url)
            except Exception as exc:
                logger.warning("WS ping/pong failed: %s", exc)
                raise
