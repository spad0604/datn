import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    http_host: str
    http_port: int
    uart_port: str
    uart_baudrate: int
    ws_server_url: str
    ws_reconnect_sec: int

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            http_host=os.getenv("HTTP_HOST", "0.0.0.0"),
            http_port=int(os.getenv("HTTP_PORT", "8080")),
            uart_port=os.getenv("UART_PORT", ""),
            uart_baudrate=int(os.getenv("UART_BAUDRATE", "115200")),
            ws_server_url=os.getenv("WS_SERVER_URL", ""),
            ws_reconnect_sec=int(os.getenv("WS_RECONNECT_SEC", "3")),
        )
