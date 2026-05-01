"""Compatibility client for robot communication over BE WebSocket/STOMP.

This module intentionally keeps the old names (`FirebaseClient`, `Order`, ...)
so existing ROS scripts can run without a large refactor.
"""

import json
import math
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from websocket import WebSocketTimeoutException, create_connection


@dataclass
class RoutePoint:
    lat: float
    lng: float
    order: int

    def to_dict(self) -> dict:
        return {"lat": self.lat, "lng": self.lng, "order": self.order}

    @classmethod
    def from_dict(cls, data: dict) -> "RoutePoint":
        return cls(
            lat=float(data.get("lat", 0.0)),
            lng=float(data.get("lng", 0.0)),
            order=int(data.get("order", 0)),
        )


@dataclass
class Order:
    id: str = ""
    createdAt: str = ""
    destinationLat: float = 0.0
    destinationLng: float = 0.0
    goods: str = ""
    pinCode: str = ""
    phoneNumber: str = ""
    receiverAge: int = 0
    receiverName: str = ""
    routePoints: List[RoutePoint] = None
    status: str = ""
    weight: float = 0.0

    def __post_init__(self) -> None:
        if self.routePoints is None:
            self.routePoints = []


@dataclass
class Robot:
    lat: float
    lon: float


@dataclass
class DatabaseData:
    orders: Dict[str, Order]
    robot: Robot


class FirebaseClient:
    """Backward-compatible API now backed by BE websocket + REST."""

    DEFAULT_WS_URL = "ws://127.0.0.1:8080/ws-delivery-native"
    DEFAULT_API_BASE_URL = "http://127.0.0.1:8080/api/v1/robot"
    DEFAULT_SECRET = "DATN_2025_2_GIAP"

    def __init__(
        self,
        database_url: Optional[str] = None,
        ws_url: Optional[str] = None,
        api_base_url: Optional[str] = None,
        robot_id: int = 1,
        secret_key: Optional[str] = None,
    ):
        self.robot_id = int(robot_id)
        self.secret_key = secret_key or os.getenv("ROBOT_SHARED_SECRET", self.DEFAULT_SECRET)
        self.ws_url, self.api_base_url = self._resolve_endpoints(
            database_url=database_url,
            ws_url=ws_url,
            api_base_url=api_base_url,
        )

        # Keep attribute name for old callers that used `base_url`.
        self.base_url = self.ws_url

        self._last_robot: Optional[Robot] = None
        self._orders_cache: Dict[str, Order] = {}

    def _resolve_endpoints(
        self,
        database_url: Optional[str],
        ws_url: Optional[str],
        api_base_url: Optional[str],
    ) -> Tuple[str, str]:
        if ws_url and api_base_url:
            return ws_url.rstrip("/"), api_base_url.rstrip("/")

        if database_url:
            candidate = database_url.rstrip("/")
            if candidate.startswith("ws://") or candidate.startswith("wss://"):
                return (
                    candidate,
                    api_base_url.rstrip("/") if api_base_url else self.DEFAULT_API_BASE_URL,
                )

            if "firebaseio" not in candidate:
                parsed = urlparse(candidate)
                if parsed.scheme in ("http", "https"):
                    inferred_ws = self._infer_ws_from_http(candidate)
                    inferred_api = f"{parsed.scheme}://{parsed.netloc}/api/v1/robot"
                    return (
                        ws_url.rstrip("/") if ws_url else inferred_ws,
                        api_base_url.rstrip("/") if api_base_url else inferred_api,
                    )

        return (
            ws_url.rstrip("/") if ws_url else os.getenv("ROBOT_WS_URL", self.DEFAULT_WS_URL),
            api_base_url.rstrip("/")
            if api_base_url
            else os.getenv("ROBOT_API_BASE_URL", self.DEFAULT_API_BASE_URL),
        )

    def _infer_ws_from_http(self, http_url: str) -> str:
        parsed = urlparse(http_url)
        ws_scheme = "wss" if parsed.scheme == "https" else "ws"
        return f"{ws_scheme}://{parsed.netloc}/ws-delivery-native"

    def _build_frame(self, command: str, headers: Dict[str, str], body: str = "") -> str:
        lines = [command]
        for key, value in headers.items():
            lines.append(f"{key}:{value}")
        return "\n".join(lines) + "\n\n" + body + "\x00"

    def _parse_frame(self, raw_frame: str) -> Optional[Tuple[str, Dict[str, str], str]]:
        frame = raw_frame.lstrip("\n")
        if not frame.strip():
            return None

        head, sep, body = frame.partition("\n\n")
        if not sep:
            body = ""

        lines = head.split("\n")
        command = lines[0].strip()
        headers: Dict[str, str] = {}

        for line in lines[1:]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

        return command, headers, body

    def _recv_frames(self, ws, buffer: str, timeout_seconds: float = 1.0):
        ws.settimeout(timeout_seconds)
        try:
            chunk = ws.recv()
        except WebSocketTimeoutException:
            return [], buffer

        if isinstance(chunk, bytes):
            chunk = chunk.decode("utf-8", errors="ignore")
        if not isinstance(chunk, str):
            chunk = str(chunk)

        buffer += chunk
        frames = []
        while "\x00" in buffer:
            raw_frame, buffer = buffer.split("\x00", 1)
            parsed = self._parse_frame(raw_frame)
            if parsed:
                frames.append(parsed)

        return frames, buffer

    def _open_stomp_connection(self, timeout_seconds: float = 8.0):
        ws = create_connection(self.ws_url, timeout=timeout_seconds)

        host_header = urlparse(self.ws_url).hostname or "localhost"
        connect_frame = self._build_frame(
            "CONNECT",
            {
                "accept-version": "1.2",
                "host": host_header,
                "heart-beat": "10000,10000",
            },
        )
        ws.send(connect_frame)

        buffer = ""
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            frames, buffer = self._recv_frames(ws, buffer, timeout_seconds=1.0)
            for command, _, body in frames:
                if command == "CONNECTED":
                    return ws
                if command == "ERROR":
                    raise RuntimeError(f"STOMP ERROR while CONNECT: {body}")

            ws.send("\n")

        ws.close()
        raise TimeoutError("Timeout waiting for STOMP CONNECTED frame")

    def _send_json(self, destination: str, payload: Dict[str, Any]) -> bool:
        ws = None
        try:
            ws = self._open_stomp_connection()
            body = json.dumps(payload)
            ws.send(
                self._build_frame(
                    "SEND",
                    {
                        "destination": destination,
                        "content-type": "application/json",
                    },
                    body,
                )
            )
            ws.send(self._build_frame("DISCONNECT", {}))
            return True
        except Exception as exc:
            print(f"[WS] send error: {exc}")
            return False
        finally:
            if ws is not None:
                try:
                    ws.close()
                except Exception:
                    pass

    def _order_from_payload(self, payload: Dict[str, Any]) -> Optional[Order]:
        if not payload:
            return None

        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        order_id = data.get("id") or data.get("orderId")
        if order_id is None:
            return None

        status_raw = data.get("status")
        if status_raw is None:
            status_raw = data.get("orderStatus")
        status = str(status_raw).lower() if status_raw is not None else ""

        created_at = data.get("createdAt")
        if created_at is None:
            ts = data.get("ts")
            if ts is not None:
                try:
                    created_at = datetime.utcfromtimestamp(float(ts) / 1000.0).isoformat() + "Z"
                except Exception:
                    created_at = str(ts)
            else:
                created_at = ""

        destination_lat = data.get("deliveryLat")
        if destination_lat is None:
            destination_lat = data.get("destinationLat")

        destination_lng = data.get("deliveryLng")
        if destination_lng is None:
            destination_lng = data.get("destinationLng")

        route_points: List[RoutePoint] = []
        raw_route = data.get("routePoints")
        if isinstance(raw_route, list) and raw_route:
            for idx, item in enumerate(raw_route):
                if isinstance(item, dict):
                    route_points.append(
                        RoutePoint(
                            lat=float(item.get("lat", 0.0)),
                            lng=float(item.get("lng", 0.0)),
                            order=int(item.get("order", idx)),
                        )
                    )
        else:
            start_lat = data.get("startLat")
            start_lng = data.get("startLng")
            if start_lat is not None and start_lng is not None:
                route_points.append(RoutePoint(float(start_lat), float(start_lng), 0))
            if destination_lat is not None and destination_lng is not None:
                route_points.append(RoutePoint(float(destination_lat), float(destination_lng), 1))

        receiver_name = (
            data.get("receiverName")
            or data.get("recipientName")
            or data.get("recipientFullName")
            or data.get("senderName")
            or data.get("deliveryAddress")
            or "unknown"
        )

        phone = data.get("phoneNumber") or data.get("recipientPhone") or ""
        goods = data.get("goods") or data.get("orderCode") or ""
        pin_code = data.get("pinCode") or data.get("pin_code") or ""

        try:
            dest_lat_val = float(destination_lat) if destination_lat is not None else 0.0
            dest_lng_val = float(destination_lng) if destination_lng is not None else 0.0
        except Exception:
            dest_lat_val = 0.0
            dest_lng_val = 0.0

        return Order(
            id=str(order_id),
            createdAt=str(created_at),
            destinationLat=dest_lat_val,
            destinationLng=dest_lng_val,
            goods=str(goods),
            pinCode=str(pin_code),
            phoneNumber=str(phone),
            receiverAge=int(data.get("receiverAge") or 0),
            receiverName=str(receiver_name),
            routePoints=route_points,
            status=status,
            weight=float(data.get("weight") or 0.0),
        )

    def fetch_current_order(self) -> Optional[Order]:
        url = f"{self.api_base_url}/{self.robot_id}/current-order"
        try:
            response = requests.get(
                url,
                headers={"X-Robot-Secret": self.secret_key},
                timeout=10,
            )
            if response.status_code != 200:
                return None
            payload = response.json()
            order = self._order_from_payload(payload)
            if order:
                self._orders_cache[order.id] = order
            return order
        except Exception:
            return None

    def update_robot_location(self, lat: float, lon: float) -> bool:
        payload = {
            "lat": float(lat),
            "lng": float(lon),
            "robotId": self.robot_id,
            "secretKey": self.secret_key,
            "heading": 0.0,
        }
        success = self._send_json("/app/update-location", payload)
        if success:
            self._last_robot = Robot(lat=float(lat), lon=float(lon))
        return success

    def get_robot_location(self) -> Optional[Robot]:
        return self._last_robot

    def get_all_orders(self) -> Dict[str, Order]:
        return dict(self._orders_cache)

    def get_order(self, order_id: str) -> Optional[Order]:
        key = str(order_id)
        order = self._orders_cache.get(key)
        if order is not None:
            return order

        current = self.fetch_current_order()
        if current and current.id == key:
            return current
        return None

    def get_all_data(self) -> Optional[DatabaseData]:
        robot = self._last_robot or Robot(lat=0.0, lon=0.0)
        return DatabaseData(orders=self.get_all_orders(), robot=robot)

    def listen_orders(
        self,
        on_change: Callable[[List[Order], Dict[str, Any], str], None],
        on_error: Optional[Callable[[Exception], None]] = None,
        retry_delay_seconds: float = 5.0,
        should_stop: Optional[Callable[[], bool]] = None,
    ) -> None:
        def stop_requested() -> bool:
            return bool(should_stop and should_stop())

        def emit_error(exc: Exception) -> None:
            if on_error:
                on_error(exc)
            else:
                print(f"[WS] listen error: {exc}")

        while not stop_requested():
            ws = None
            try:
                ws = self._open_stomp_connection()
                ws.send(
                    self._build_frame(
                        "SUBSCRIBE",
                        {
                            "id": f"robot-order-{self.robot_id}",
                            "destination": f"/topic/robot-order/{self.robot_id}",
                            "ack": "auto",
                        },
                    )
                )

                snapshot = self.fetch_current_order()
                if snapshot is not None:
                    ordered = sorted(self._orders_cache.values(), key=lambda o: o.createdAt, reverse=True)
                    on_change(ordered, {"source": "rest-snapshot"}, "snapshot")

                buffer = ""
                while not stop_requested():
                    frames, buffer = self._recv_frames(ws, buffer, timeout_seconds=1.0)
                    if not frames:
                        # heart-beat
                        ws.send("\n")
                        continue

                    for command, _, body in frames:
                        if command == "MESSAGE":
                            payload = json.loads(body) if body else {}
                            order = self._order_from_payload(payload)
                            if order is None:
                                continue

                            self._orders_cache[order.id] = order
                            ordered = sorted(
                                self._orders_cache.values(),
                                key=lambda o: o.createdAt,
                                reverse=True,
                            )

                            event_type = str(payload.get("type", "message"))
                            on_change(ordered, payload, event_type)

                        elif command == "ERROR":
                            raise RuntimeError(body or "STOMP ERROR frame received")

            except KeyboardInterrupt:
                break
            except Exception as exc:
                if stop_requested():
                    break
                emit_error(exc)
            finally:
                if ws is not None:
                    try:
                        ws.close()
                    except Exception:
                        pass

            if not stop_requested():
                time.sleep(retry_delay_seconds)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def generate_next_location(
    current_lat: float,
    current_lon: float,
    max_distance_meters: float = 200.0,
) -> Tuple[float, float]:
    hanoi_lat_min = 20.9
    hanoi_lat_max = 21.1
    hanoi_lon_min = 105.7
    hanoi_lon_max = 105.9

    lat_degree_per_meter = 1.0 / 111000.0
    lon_degree_per_meter = 1.0 / (111000.0 * math.cos(math.radians(current_lat)))

    max_lat_delta = max_distance_meters * lat_degree_per_meter
    max_lon_delta = max_distance_meters * lon_degree_per_meter

    for _ in range(50):
        new_lat = current_lat + random.uniform(-max_lat_delta, max_lat_delta)
        new_lon = current_lon + random.uniform(-max_lon_delta, max_lon_delta)

        new_lat = max(hanoi_lat_min, min(hanoi_lat_max, new_lat))
        new_lon = max(hanoi_lon_min, min(hanoi_lon_max, new_lon))

        if calculate_distance(current_lat, current_lon, new_lat, new_lon) <= max_distance_meters:
            return new_lat, new_lon

    new_lat = current_lat + random.uniform(-max_lat_delta * 0.5, max_lat_delta * 0.5)
    new_lon = current_lon + random.uniform(-max_lon_delta * 0.5, max_lon_delta * 0.5)
    return (
        max(hanoi_lat_min, min(hanoi_lat_max, new_lat)),
        max(hanoi_lon_min, min(hanoi_lon_max, new_lon)),
    )


def run_periodic_location_update(
    firebase_client: FirebaseClient,
    interval_seconds: int = 10,
    max_distance_meters: float = 200.0,
    initial_lat: Optional[float] = None,
    initial_lon: Optional[float] = None,
):
    print(f"=== Start periodic robot location update (every {interval_seconds}s) ===")
    print(f"Max distance between points: {max_distance_meters}m")
    print("Press Ctrl+C to stop\n")

    if initial_lat is None or initial_lon is None:
        robot = firebase_client.get_robot_location()
        if robot:
            current_lat, current_lon = robot.lat, robot.lon
        else:
            current_lat, current_lon = 21.0285, 105.8542
            firebase_client.update_robot_location(current_lat, current_lon)
    else:
        current_lat, current_lon = initial_lat, initial_lon
        firebase_client.update_robot_location(current_lat, current_lon)

    try:
        update_count = 0
        while True:
            new_lat, new_lon = generate_next_location(current_lat, current_lon, max_distance_meters)
            distance = calculate_distance(current_lat, current_lon, new_lat, new_lon)

            success = firebase_client.update_robot_location(new_lat, new_lon)
            if success:
                update_count += 1
                print(
                    f"[{update_count}] ok lat={new_lat:.6f}, lon={new_lon:.6f} "
                    f"(distance={distance:.1f}m)"
                )
            else:
                print(f"[{update_count + 1}] failed to update location")

            current_lat, current_lon = new_lat, new_lon
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print(f"\n\nStopped. Total updates: {update_count}")
        print(f"Last location: lat={current_lat:.6f}, lon={current_lon:.6f}")

