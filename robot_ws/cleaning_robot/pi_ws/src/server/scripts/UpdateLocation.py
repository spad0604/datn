#!/usr/bin/env python3


import rospy
from sensor_msgs.msg import NavSatFix
import math
from firebase_sample import FirebaseClient 
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class SimpleGPSFirebase:
    def __init__(self):
        rospy.init_node('simple_gps_firebase', anonymous=False)

        # GPS mới nhất
        self.latest_lat = None
        self.latest_lon = None

        # BE websocket client (robot_id fixed to 1)
        ws_url = rospy.get_param("~ws_url", "ws://127.0.0.1:8080/ws-delivery-native")
        api_base_url = rospy.get_param("~api_base_url", "http://127.0.0.1:8080/api/v1/robot")
        secret_key = rospy.get_param("~secret_key", "DATN_2025_2_GIAP")
        self.firebase = FirebaseClient(
            ws_url=ws_url,
            api_base_url=api_base_url,
            robot_id=1,
            secret_key=secret_key,
        )

        # Tham số
        self.interval = rospy.get_param("~interval_seconds", 10)
        self.min_distance = rospy.get_param("~max_distance_meters", 10.0)

        # Subscribe GPS
        rospy.Subscriber("/fix", NavSatFix, self.gps_callback, queue_size=10)

        rospy.loginfo("Simple GPS BE WebSocket node khoi dong.")
        rospy.loginfo(f"   Kiểm tra mỗi {self.interval}s, cập nhật nếu di chuyển >= {self.min_distance}m")

    def gps_callback(self, msg):
        if msg.status.status >= 0:  # Có fix
            self.latest_lat = msg.latitude
            self.latest_lon = msg.longitude
        else:
            rospy.logwarn_throttle(60, "GPS chưa có fix hợp lệ")

    def update_firebase_if_needed(self):
        if self.latest_lat is None or self.latest_lon is None:
            return  # Chưa có dữ liệu GPS

        # Lay vi tri gan nhat da gui len BE (lam vi tri "cu")
        robot = self.firebase.get_robot_location()
        if robot and robot.lat is not None and robot.lon is not None:
            prev_lat = robot.lat
            prev_lon = robot.lon
        else:
            # Neu chua co vi tri truoc do -> gui ngay lan dau
            success = self.firebase.update_robot_location(self.latest_lat, self.latest_lon)
            if success:
                rospy.loginfo(f"Lần đầu gửi vị trí: {self.latest_lat:.6f}, {self.latest_lon:.6f}")
            return

        # Tính khoảng cách
        distance = calculate_distance(prev_lat, prev_lon, self.latest_lat, self.latest_lon)

        if distance >= self.min_distance:
            success = self.firebase.update_robot_location(self.latest_lat, self.latest_lon)
            if success:
                rospy.loginfo(f"✓ Cap nhat BE WebSocket: {self.latest_lat:.6f}, {self.latest_lon:.6f} "
                              f"(di chuyển {distance:.1f}m)")
            else:
                rospy.logerr("✗ Loi khi cap nhat BE WebSocket")
        # else: Không đủ xa → bỏ qua (không log để đỡ spam)

    def run(self):
        rate = rospy.Rate(1.0 / self.interval)  # 10 giây/lần
        while not rospy.is_shutdown():
            self.update_firebase_if_needed()
            rate.sleep()


if __name__ == "__main__":
    try:
        node = SimpleGPSFirebase()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Node dừng.")