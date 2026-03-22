import asyncio
import logging
from typing import Awaitable, Callable, Optional

import serial


logger = logging.getLogger(__name__)


class UARTService:
    def __init__(
        self,
        port: str,
        baudrate: int,
        on_line: Callable[[str], Awaitable[None]],
        reconnect_sec: int = 3,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._on_line = on_line
        self._reconnect_sec = reconnect_sec

        self._serial: Optional[serial.Serial] = None
        self._running = False

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    async def start(self) -> None:
        self._running = True

        while self._running:
            if not self._port:
                logger.info("UART_PORT is empty. UART layer is disabled.")
                await asyncio.sleep(self._reconnect_sec)
                continue

            try:
                self._serial = serial.Serial(
                    port=self._port,
                    baudrate=self._baudrate,
                    timeout=1,
                )
                logger.info("UART connected: %s @ %d", self._port, self._baudrate)
                await self._read_loop()
            except Exception as exc:
                logger.warning("UART reconnect in %ss due to error: %s", self._reconnect_sec, exc)
                await asyncio.sleep(self._reconnect_sec)
            finally:
                self._close_serial()

    async def stop(self) -> None:
        self._running = False
        self._close_serial()

    async def send_line(self, data: str) -> None:
        if not self.is_connected or not self._serial:
            raise RuntimeError("UART is not connected")

        packet = (data.rstrip("\n") + "\n").encode("utf-8")
        await asyncio.to_thread(self._serial.write, packet)

    async def _read_loop(self) -> None:
        while self._running and self.is_connected and self._serial:
            raw = await asyncio.to_thread(self._serial.readline)
            if not raw:
                continue
            line = raw.decode("utf-8", errors="ignore").strip()
            if line:
                await self._on_line(line)

    def _close_serial(self) -> None:
        if self._serial is not None:
            try:
                if self._serial.is_open:
                    self._serial.close()
            finally:
                self._serial = None
