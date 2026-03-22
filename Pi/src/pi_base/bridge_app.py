import asyncio
import json
import logging
from typing import Any

from .config import Settings
from .models import BridgeState
from .services.local_ws_hub import LocalWebSocketHub
from .services.uart_service import UARTService
from .services.ws_client_service import WSClientService


logger = logging.getLogger(__name__)


class BridgeApp:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.state = BridgeState()
        self.local_ws_hub = LocalWebSocketHub()

        self._lock = asyncio.Lock()
        self._tasks: list[asyncio.Task[Any]] = []

        self.uart = UARTService(
            port=settings.uart_port,
            baudrate=settings.uart_baudrate,
            on_line=self.on_uart_line,
            reconnect_sec=settings.ws_reconnect_sec,
        )
        self.remote_ws = WSClientService(
            server_url=settings.ws_server_url,
            on_message=self.on_ws_message,
            reconnect_sec=settings.ws_reconnect_sec,
        )

    async def __aenter__(self) -> "BridgeApp":
        self._tasks.append(asyncio.create_task(self.uart.start(), name="uart-service"))
        self._tasks.append(asyncio.create_task(self.remote_ws.start(), name="ws-client-service"))
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.uart.stop()
        await self.remote_ws.stop()

        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def on_uart_line(self, line: str) -> None:
        async with self._lock:
            self.state.uart_connected = self.uart.is_connected
            self.state.ws_connected = self.remote_ws.is_connected
            self.state.last_uart_rx = line
            self.state.touch()

        payload = {"source": "uart", "data": line}
        await self.local_ws_hub.broadcast(payload)

        # Default forwarding: MCU -> remote websocket server.
        await self.remote_ws.send_json(payload)

    async def on_ws_message(self, message: str) -> None:
        async with self._lock:
            self.state.uart_connected = self.uart.is_connected
            self.state.ws_connected = self.remote_ws.is_connected
            self.state.last_ws_rx = message
            self.state.touch()

        await self.local_ws_hub.broadcast({"source": "ws", "data": message})

        # Optional example to send websocket commands to MCU:
        # await self.uart.send_line(message)

    async def mark_http_get(self, route: str) -> None:
        async with self._lock:
            self.state.uart_connected = self.uart.is_connected
            self.state.ws_connected = self.remote_ws.is_connected
            self.state.last_http_get = route
            self.state.touch()

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            self.state.uart_connected = self.uart.is_connected
            self.state.ws_connected = self.remote_ws.is_connected
            return self.state.to_dict()

    async def send_to_mcu(self, data: str) -> dict[str, Any]:
        await self.uart.send_line(data)
        return {"ok": True, "target": "mcu", "data": data}

    async def send_to_remote_ws(self, data: str) -> dict[str, Any]:
        try:
            payload = json.loads(data)
            if isinstance(payload, dict):
                await self.remote_ws.send_json(payload)
            else:
                await self.remote_ws.send_text(data)
        except json.JSONDecodeError:
            await self.remote_ws.send_text(data)

        return {"ok": True, "target": "remote_ws", "data": data}
