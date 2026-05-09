#!/usr/bin/env python3

"""Script to run periodic robot location updates to BE WebSocket server.

Usage: python run_periodic_update.py
"""

from ws_client import ServerService, run_periodic_location_update
from config_ws import DEFAULT_WS_URL, DEFAULT_API_BASE_URL, DEFAULT_SECRET, DEFAULT_ROBOT_ID

if __name__ == "__main__":
    # Initialize BE websocket client
    ws_client = ServerService(
        ws_url=DEFAULT_WS_URL,
        api_base_url=DEFAULT_API_BASE_URL,
        robot_id=DEFAULT_ROBOT_ID,
    )
    
    # Chay dinh ky day toa do robot len BE WebSocket
    # - interval_seconds=10: Cập nhật mỗi 10 giây
    # - max_distance_meters=200.0: Khoảng cách tối đa giữa các điểm là 200 mét
    # - initial_lat, initial_lon: Co the chi dinh vi tri ban dau (None = lay vi tri cu)
    run_periodic_location_update(
        firebase_client=ws_client,
        interval_seconds=10,
        max_distance_meters=200.0,
        initial_lat=None,  # None = lấy từ Firebase, hoặc chỉ định ví dụ: 21.0285
        initial_lon=None  # None = lấy từ Firebase, hoặc chỉ định ví dụ: 105.8542
    )

