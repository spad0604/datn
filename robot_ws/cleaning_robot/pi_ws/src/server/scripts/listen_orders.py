"""
Script theo doi danh sach don hang qua BE WebSocket theo thoi gian thuc.
Chay: python Embedded/listen_orders.py
"""

from typing import List

from firebase_sample import FirebaseClient, Order


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
    firebase = FirebaseClient(
        ws_url="ws://127.0.0.1:8080/ws-delivery-native",
        api_base_url="http://127.0.0.1:8080/api/v1/robot",
        robot_id=1,
    )
    firebase.listen_orders(
        on_change=print_orders,
        on_error=log_error,
        retry_delay_seconds=5.0,
    )

