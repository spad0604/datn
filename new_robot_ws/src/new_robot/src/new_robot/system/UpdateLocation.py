#!/usr/bin/env python3

import math

import rospy
from sensor_msgs.msg import NavSatFix

from new_robot.server.ws_client import ServerService
from new_robot.server.config_ws import DEFAULT_API_BASE_URL, DEFAULT_SECRET, DEFAULT_WS_URL


def calculate_distance(lat1, lon1, lat2, lon2):
    r = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


class GPSLocationUpdater:
    def __init__(self):
        rospy.init_node('gps_location_updater', anonymous=False)

        self.latest_lat = None
        self.latest_lon = None

        ws_url = rospy.get_param("~ws_url", DEFAULT_WS_URL)
        api_base_url = rospy.get_param("~api_base_url", DEFAULT_API_BASE_URL)
        secret_key = rospy.get_param("~secret_key", DEFAULT_SECRET)
        self.ws_client = ServerService(
            ws_url=ws_url,
            api_base_url=api_base_url,
            robot_id=1,
            secret_key=secret_key,
        )

        self.interval = rospy.get_param("~interval_seconds", 10)
        self.min_distance = rospy.get_param("~max_distance_meters", 10.0)

        rospy.Subscriber("/fix", NavSatFix, self.gps_callback, queue_size=10)

        rospy.loginfo("GPSLocationUpdater khoi dong")

    def gps_callback(self, msg: NavSatFix):
        if msg.status.status >= 0:
            self.latest_lat = msg.latitude
            self.latest_lon = msg.longitude
        else:
            rospy.logwarn_throttle(60, "GPS chua co fix hop le")

    def update_location_if_needed(self):
        if self.latest_lat is None or self.latest_lon is None:
            return

        robot = self.ws_client.get_robot_location()
        if robot and robot.lat is not None and robot.lon is not None:
            prev_lat = robot.lat
            prev_lon = robot.lon
        else:
            success = self.ws_client.update_robot_location(self.latest_lat, self.latest_lon)
            if success:
                rospy.loginfo(f"Lan dau gui vi tri: {self.latest_lat:.6f}, {self.latest_lon:.6f}")
            return

        distance = calculate_distance(prev_lat, prev_lon, self.latest_lat, self.latest_lon)
        if distance >= self.min_distance:
            success = self.ws_client.update_robot_location(self.latest_lat, self.latest_lon)
            if success:
                rospy.loginfo(
                    f"Cap nhat BE: {self.latest_lat:.6f}, {self.latest_lon:.6f} (di chuyen {distance:.1f}m)"
                )
            else:
                rospy.logerr("Loi khi cap nhat BE")

    def run(self):
        rate = rospy.Rate(1.0 / float(self.interval))
        while not rospy.is_shutdown():
            self.update_location_if_needed()
            rate.sleep()


if __name__ == "__main__":
    try:
        node = GPSLocationUpdater()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Node dung")
