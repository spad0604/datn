import asyncio
import json
import logging
import urllib.error
import urllib.request
from typing import Any

from .config import Settings
from .models import BridgeState
from .services.local_ws_hub import LocalWebSocketHub
from .services.stomp_client_service import StompClientService, StompMessage
from .services.uart_service import UARTService
from .services.ws_client_service import WSClientService
from .mcu_protocol import cmd_motor, cmd_motor_stop, cmd_mpu_read, cmd_pin_set, cmd_pin_clear, cmd_unlock, parse_line


logger = logging.getLogger(__name__)


class BridgeApp:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.state = BridgeState()
        self.local_ws_hub = LocalWebSocketHub()

        self._lock = asyncio.Lock()
        self._tasks: list[asyncio.Task[Any]] = []
        self._last_polled_order_id: int | None = None

        self.uart = UARTService(
            port=settings.uart_port,
            baudrate=settings.uart_baudrate,
            on_line=self.on_uart_line,
            reconnect_sec=settings.ws_reconnect_sec,
        )

        ws_mode = (settings.ws_mode or "auto").strip().lower()
        if ws_mode == "auto":
            ws_mode = "stomp" if "/ws-delivery" in (settings.ws_server_url or "") else "raw"

        self._ws_mode = ws_mode
        if ws_mode == "stomp":
            subs: list[str] = []
            if settings.robot_id > 0:
                subs.append(f"/topic/robot-order/{settings.robot_id}")

            self.remote_ws = StompClientService(
                server_url=settings.ws_server_url,
                on_message=self.on_stomp_message,
                reconnect_sec=settings.ws_reconnect_sec,
                subscribe_destinations=subs,
                default_send_destination=settings.stomp_send_destination,
            )
        else:
            self.remote_ws = WSClientService(
                server_url=settings.ws_server_url,
                on_message=self.on_ws_message,
                reconnect_sec=settings.ws_reconnect_sec,
            )

    async def __aenter__(self) -> "BridgeApp":
        self._tasks.append(asyncio.create_task(self.uart.start(), name="uart-service"))
        self._tasks.append(asyncio.create_task(self.remote_ws.start(), name="ws-client-service"))

        if self.settings.api_base_url and self.settings.robot_id > 0 and self.settings.robot_secret:
            self._tasks.append(asyncio.create_task(self._poll_current_order_loop(), name="robot-order-poll"))
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

        # Parse standardized MCU frames and keep a friendly state trail.
        frame = parse_line(line)
        if frame is not None:
            await self.local_ws_hub.broadcast(
                {
                    "source": "uart",
                    "event": "mcu_frame",
                    "kind": frame.kind,
                    "name": frame.name,
                    "fields": frame.fields,
                }
            )

        # In STOMP mode, try to translate UART JSON -> /app/update-location.
        if self._ws_mode == "stomp":
            await self._maybe_send_location_to_server(line)
            return

        # RAW mode: Default forwarding: MCU -> remote websocket server.
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

    async def on_stomp_message(self, msg: StompMessage) -> None:
        body = msg.body
        async with self._lock:
            self.state.uart_connected = self.uart.is_connected
            self.state.ws_connected = self.remote_ws.is_connected
            self.state.last_ws_rx = body
            self.state.touch()

        # Fan-out to local UI.
        await self.local_ws_hub.broadcast({"source": "ws", "data": body})

        # Forward robot order events to MCU as one-line JSON.
        try:
            payload = json.loads(body)
            if isinstance(payload, dict) and payload.get("type") in {
                "ORDER_ASSIGNED",
                "ORDER_CANCELLED",
                "ORDER_STATUS_CHANGED",
            }:
                await self.uart.send_line(json.dumps({"type": "ROBOT_ORDER_EVENT", **payload}, ensure_ascii=True))

                # Push PIN down to MCU when a new order is assigned.
                if payload.get("type") == "ORDER_ASSIGNED":
                    pin = payload.get("pinCode") or payload.get("pin")
                    if pin:
                        await self.uart.send_line(cmd_pin_set(str(pin), order=payload.get("orderId")))

                # If order cancelled, clear PIN so MCU won't unlock.
                if payload.get("type") == "ORDER_CANCELLED":
                    await self.uart.send_line(cmd_pin_clear())
        except Exception:
            # Ignore non-JSON / unrelated events.
            return

    async def _maybe_send_location_to_server(self, uart_line: str) -> None:
        if not self.settings.robot_secret:
            return

        try:
            obj = json.loads(uart_line)
        except json.JSONDecodeError:
            return

        if not isinstance(obj, dict):
            return

        msg_type = str(obj.get("type", "")).lower()
        if msg_type not in {"location", "robot_location", "gps"}:
            return

        lat = obj.get("lat")
        lng = obj.get("lng")
        robot_id = obj.get("robotId") or self.settings.robot_id
        if robot_id in (None, 0) or lat is None or lng is None:
            return

        request = {
            "robotId": int(robot_id),
            "lat": float(lat),
            "lng": float(lng),
            "secretKey": self.settings.robot_secret,
        }

        # /app/update-location (STOMP SEND)
        send_to = self.settings.stomp_send_destination or "/app/update-location"
        await self.remote_ws.send_json_to(send_to, request)

    async def _poll_current_order_loop(self) -> None:
        base = self.settings.api_base_url.rstrip("/")
        robot_id = self.settings.robot_id
        if not base or robot_id <= 0 or not self.settings.robot_secret:
            return

        url = f"{base}/api/v1/robot/{robot_id}/current-order"
        headers = {"X-Robot-Secret": self.settings.robot_secret}

        while True:
            try:
                data = await asyncio.to_thread(self._http_get_json, url, headers)
                order = (data or {}).get("data") if isinstance(data, dict) else None
                order_id = order.get("id") if isinstance(order, dict) else None

                if order_id != self._last_polled_order_id:
                    self._last_polled_order_id = order_id
                    await self.uart.send_line(
                        json.dumps(
                            {
                                "type": "CURRENT_ORDER_SNAPSHOT",
                                "robotId": robot_id,
                                "order": order,
                                "message": (data or {}).get("message") if isinstance(data, dict) else None,
                            },
                            ensure_ascii=True,
                        )
                    )

                    # Auto push/clear PIN for MCU based on current order snapshot.
                    if isinstance(order, dict) and order.get("pinCode"):
                        await self.uart.send_line(cmd_pin_set(str(order.get("pinCode")), order=order.get("id")))
                    else:
                        await self.uart.send_line(cmd_pin_clear())
            except Exception:
                pass

            await asyncio.sleep(max(1, int(self.settings.robot_order_poll_sec)))

    @staticmethod
    def _http_get_json(url: str, headers: dict[str, str]) -> dict[str, Any] | None:
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8", errors="ignore")
                return json.loads(raw)
        except (urllib.error.URLError, json.JSONDecodeError):
            return None

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

    async def mcu_motor(self, left: int, right: int) -> dict[str, Any]:
        packet = cmd_motor(left, right)
        await self.uart.send_line(packet)
        return {"ok": True, "target": "mcu", "cmd": "MOTOR", "left": left, "right": right}

    async def mcu_stop(self) -> dict[str, Any]:
        packet = cmd_motor_stop()
        await self.uart.send_line(packet)
        return {"ok": True, "target": "mcu", "cmd": "MOTOR_STOP"}

    async def mcu_mpu_read(self) -> dict[str, Any]:
        packet = cmd_mpu_read()
        await self.uart.send_line(packet)
        return {"ok": True, "target": "mcu", "cmd": "MPU_READ"}

    async def mcu_pin_set(self, pin: str, order_id: int | None = None) -> dict[str, Any]:
        packet = cmd_pin_set(pin, order=order_id)
        await self.uart.send_line(packet)
        return {"ok": True, "target": "mcu", "cmd": "PIN_SET", "orderId": order_id}

    async def mcu_unlock(self, pin: str) -> dict[str, Any]:
        packet = cmd_unlock(pin)
        await self.uart.send_line(packet)
        return {"ok": True, "target": "mcu", "cmd": "UNLOCK"}

    async def send_to_remote_ws(self, data: str) -> dict[str, Any]:
        if self._ws_mode == "stomp":
            return {"ok": False, "error": "remote_ws_send_disabled_in_stomp_mode"}
        try:
            payload = json.loads(data)
            if isinstance(payload, dict):
                await self.remote_ws.send_json(payload)
            else:
                await self.remote_ws.send_text(data)
        except json.JSONDecodeError:
            await self.remote_ws.send_text(data)

        return {"ok": True, "target": "remote_ws", "data": data}
