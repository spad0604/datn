from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class BridgeState:
    uart_connected: bool = False
    ws_connected: bool = False
    last_uart_rx: str = ""
    last_ws_rx: str = ""
    last_http_get: str = ""
    updated_at_utc: str = ""

    def touch(self) -> None:
        self.updated_at_utc = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)
