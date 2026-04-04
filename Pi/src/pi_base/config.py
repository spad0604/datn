import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    http_host: str
    http_port: int
    uart_port: str
    uart_baudrate: int
    ws_server_url: str
    ws_mode: str
    ws_reconnect_sec: int

    robot_id: int
    robot_secret: str

    api_base_url: str
    robot_order_poll_sec: int

    stomp_send_destination: str

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            http_host=os.getenv("HTTP_HOST", "0.0.0.0"),
            http_port=int(os.getenv("HTTP_PORT", "8080")),
            uart_port=os.getenv("UART_PORT", ""),
            uart_baudrate=int(os.getenv("UART_BAUDRATE", "115200")),
            ws_server_url=os.getenv("WS_SERVER_URL", "ws://192.168.100.153:8080/ws-delivery-native"),
            ws_mode=os.getenv("WS_MODE", "auto"),
            ws_reconnect_sec=int(os.getenv("WS_RECONNECT_SEC", "3")),

            # Single-device thesis setup: default to the robot shown in DB (id=1).
            robot_id=int(os.getenv("ROBOT_ID", "1")),
            # Must match `robot.shared-secret` in BE `application.properties`.
            robot_secret=os.getenv("ROBOT_SECRET", "DATN_2025_2_GIAP"),
    
            api_base_url=os.getenv("API_BASE_URL", "http://192.168.100.153:8080"),
            robot_order_poll_sec=int(os.getenv("ROBOT_ORDER_POLL_SEC", "5")),

            stomp_send_destination=os.getenv("STOMP_SEND_DESTINATION", "/app/update-location"),
        )
