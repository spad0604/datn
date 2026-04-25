"""
Script de chay dinh ky day toa do robot len BE WebSocket
Chay: python Embedded/run_periodic_update.py
"""

from firebase_sample import FirebaseClient, run_periodic_location_update

if __name__ == "__main__":
    # Initialize BE websocket client
    firebase = FirebaseClient(
        ws_url="ws://127.0.0.1:8080/ws-delivery-native",
        api_base_url="http://127.0.0.1:8080/api/v1/robot",
        robot_id=1,
    )
    
    # Chay dinh ky day toa do robot len BE WebSocket
    # - interval_seconds=10: Cập nhật mỗi 10 giây
    # - max_distance_meters=200.0: Khoảng cách tối đa giữa các điểm là 200 mét
    # - initial_lat, initial_lon: Co the chi dinh vi tri ban dau (None = lay vi tri cu)
    run_periodic_location_update(
        firebase_client=firebase,
        interval_seconds=10,
        max_distance_meters=200.0,
        initial_lat=None,  # None = lấy từ Firebase, hoặc chỉ định ví dụ: 21.0285
        initial_lon=None  # None = lấy từ Firebase, hoặc chỉ định ví dụ: 105.8542
    )

