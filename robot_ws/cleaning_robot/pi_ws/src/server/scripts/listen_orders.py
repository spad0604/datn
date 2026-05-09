#!/usr/bin/env python3

"""
Script theo doi danh sach don hang qua BE WebSocket theo thoi gian thuc.
Chay: python Embedded/listen_orders.py
"""

from typing import List

from ws_client import ServerService, Order
from config_ws import DEFAULT_WS_URL, DEFAULT_API_BASE_URL, DEFAULT_SECRET, DEFAULT_ROBOT_ID


def print_orders(orders: List[Order], payload: dict, event_type: str) -> None:
    print("=" * 60)
    print(f"Event: {event_type}")
    print(f"Payload: {payload}")
    print(f"Tổng số đơn hàng: {len(orders)}")
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
    )
    ws_client.listen_orders(
        on_change=print_orders,
        on_error=log_error,
        retry_delay_seconds=5.0,
    )

