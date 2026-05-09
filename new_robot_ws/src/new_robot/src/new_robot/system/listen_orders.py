#!/usr/bin/env python3

"""Utility: print orders from BE websocket in real-time.

Migrate from server/scripts/listen_orders.py.
"""

from typing import List

from new_robot.server.ws_client import Order, ServerService
from new_robot.server.config_ws import (
    DEFAULT_API_BASE_URL,
    DEFAULT_ROBOT_ID,
    DEFAULT_SECRET,
    DEFAULT_WS_URL,
)


def print_orders(orders: List[Order], payload: dict, event_type: str) -> None:
    print("=" * 60)
    print(f"Event: {event_type}")
    print(f"Payload: {payload}")
    print(f"Tong so don hang: {len(orders)}")
    for order in orders:
        print(
            f"- {order.id}: {order.receiverName} ({order.status}) | "
            f"{order.goods} | {order.createdAt}"
        )


def log_error(exc: Exception) -> None:
    print(f"[ERROR] {exc}")


if __name__ == "__main__":
    ws_client = ServerService(
        ws_url=DEFAULT_WS_URL,
        api_base_url=DEFAULT_API_BASE_URL,
        robot_id=DEFAULT_ROBOT_ID,
        secret_key=DEFAULT_SECRET,
    )
    ws_client.listen_orders(
        on_change=print_orders,
        on_error=log_error,
        retry_delay_seconds=5.0,
    )
