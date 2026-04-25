#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ROS node đơn giản: Nhận GPS từ /fix → định kỳ gửi lên Firebase nếu di chuyển >= 200m
Không sửa hàm run_periodic_location_update, không thêm tham số thừa.
"""

import rospy
from sensor_msgs.msg import NavSatFix
import math
from firebase_sample import FirebaseClient  # Chỉ import Client, không import hàm cũ


# Hàm tính khoảng cách Haversine (mét)
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

        # Firebase
        firebase_url = "https://robot-delivery-cbdcf-default-rtdb.firebaseio.com"
        self.firebase = FirebaseClient(firebase_url)

        # Tham số
        self.interval = rospy.get_param("~interval_seconds", 10)
        self.min_distance = rospy.get_param("~max_distance_meters", 200.0)

        # Subscribe GPS
        rospy.Subscriber("/fix", NavSatFix, self.gps_callback, queue_size=10)

        rospy.loginfo("Simple GPS Firebase node khởi động.")
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

        # Lấy vị trí hiện tại trên Firebase (làm vị trí "cũ")
        robot = self.firebase.get_robot_location()
        if robot and robot.lat is not None and robot.lon is not None:
            prev_lat = robot.lat
            prev_lon = robot.lon
        else:
            # Nếu Firebase chưa có → gửi luôn lần đầu
            success = self.firebase.update_robot_location(self.latest_lat, self.latest_lon)
            if success:
                rospy.loginfo(f"Lần đầu gửi vị trí: {self.latest_lat:.6f}, {self.latest_lon:.6f}")
            return

        # Tính khoảng cách
        distance = calculate_distance(prev_lat, prev_lon, self.latest_lat, self.latest_lon)

        if distance >= self.min_distance:
            success = self.firebase.update_robot_location(self.latest_lat, self.latest_lon)
            if success:
                rospy.loginfo(f"✓ Cập nhật Firebase: {self.latest_lat:.6f}, {self.latest_lon:.6f} "
                              f"(di chuyển {distance:.1f}m)")
            else:
                rospy.logerr("✗ Lỗi khi cập nhật Firebase")
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
