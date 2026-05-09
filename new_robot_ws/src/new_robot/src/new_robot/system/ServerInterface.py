#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ROS Node: Theo doi don hang tu BE WebSocket voi State Machine."""

import math
import threading
from typing import Any, Dict, List

import rospy
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import PoseArray
from std_msgs.msg import String

import tf2_geometry_msgs
import tf2_ros
import utm

from new_robot.server.ws_client import Order, ServerService
from new_robot.server.config_ws import DEFAULT_API_BASE_URL, DEFAULT_SECRET, DEFAULT_WS_URL


class OrderListenerStateMachine:
    def __init__(self):
        rospy.init_node('order_listener_sm', anonymous=False)

        ws_url = rospy.get_param("~ws_url", DEFAULT_WS_URL)
        api_base_url = rospy.get_param("~api_base_url", DEFAULT_API_BASE_URL)
        secret_key = rospy.get_param("~secret_key", DEFAULT_SECRET)

        self.ws_client = ServerService(
            ws_url=ws_url,
            api_base_url=api_base_url,
            robot_id=1,
            secret_key=secret_key,
        )

        self.state = "LISTENING"
        self.is_listening = True
        self.listen_thread = None

        self.tf_buffer = tf2_ros.Buffer(rospy.Duration(60.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.map_to_utm_transform = None
        self._wait_and_get_static_transform()

        rospy.Subscriber("/Status_robot", String, self.start_listening_callback)
        self.waypoint_pub = rospy.Publisher('/waypoints', PoseArray, queue_size=10, latch=True)
        self.serial_ard_pub = rospy.Publisher('serial_ard_tx', String, queue_size=1)
        self.last_published_order_id = None

        self.start_listen_thread()
        self.ref_lat = None
        self.ref_lon = None

        rospy.loginfo("Order Listener State Machine khoi dong (LISTENING)")

    def _wait_and_get_static_transform(self):
        rospy.loginfo("Dang cho static transform tu 'utm' den 'map'...")
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            try:
                self.map_to_utm_transform = self.tf_buffer.lookup_transform(
                    "map", "utm", rospy.Time(0), rospy.Duration(5.0)
                )
                rospy.loginfo("Da lay duoc static transform utm -> map")
                break
            except (tf2_ros.LookupException, tf2_ros.ExtrapolationException) as exc:
                rospy.logwarn_throttle(10, f"Chua co TF utm -> map: {exc}. Dang cho navsat_transform set datum...")
                rate.sleep()

    def start_listening_callback(self, msg: String):
        if msg.data == "STARTING" and self.state == "WAITING":
            rospy.loginfo("Nhan STARTING -> LISTENING")
            self.state = "LISTENING"
            self.is_listening = True
            self.start_listen_thread()

    def publish_waypoints_from_route(self, route_points):
        if not route_points:
            return
        if self.map_to_utm_transform is None:
            rospy.logerr("Chua co transform utm -> map")
            return

        pose_array = PoseArray()
        pose_array.header.frame_id = "map"
        pose_array.header.stamp = rospy.Time.now()

        for pt in route_points:
            lat = pt.lat
            lon = pt.lng

            utm_x, utm_y, _, _ = utm.from_latlon(lat, lon)

            utm_pose = PoseStamped()
            utm_pose.header.frame_id = "utm"
            utm_pose.header.stamp = rospy.Time.now()
            utm_pose.pose.position.x = utm_x
            utm_pose.pose.position.y = utm_y
            utm_pose.pose.position.z = 0.0
            utm_pose.pose.orientation.w = 1.0

            map_pose = tf2_geometry_msgs.do_transform_pose(utm_pose, self.map_to_utm_transform)
            pose_array.poses.append(map_pose.pose)

        self.waypoint_pub.publish(pose_array)
        rospy.loginfo(f"Da publish {len(pose_array.poses)} waypoint")

    def publish_unlock_pin(self, order: Order):
        pin = str(getattr(order, 'pinCode', '') or '').strip()
        if not pin:
            rospy.logwarn(f"Don {order.id} khong co pinCode")
            return

        if pin.isdigit():
            pin = pin.zfill(8)

        if self.last_published_order_id == order.id:
            return

        command = f"UNLOCK {pin}"
        self.serial_ard_pub.publish(command)
        self.last_published_order_id = order.id
        rospy.loginfo(f"Da day pin xuong Arduino: {command}")

    def switch_to_waiting(self):
        if self.state == "LISTENING":
            rospy.loginfo("Co don hang moi -> WAITING")
            self.state = "WAITING"
            self.is_listening = False

    def start_listen_thread(self):
        if self.listen_thread is not None and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        self.listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        self.listen_thread.start()

    def handle_order_change(self, orders: List[Order], payload: Dict[str, Any], event_type: str):
        pending_orders = [o for o in orders if o.status == "pending"]
        if not pending_orders:
            return

        latest = pending_orders[0]
        rospy.logwarn(f"Nhan don hang moi: {latest.id}")
        self.publish_unlock_pin(latest)

        route_points = getattr(latest, 'routePoints', None)
        if route_points and len(route_points) > 0:
            self.ref_lat = None
            self.ref_lon = None
            self.publish_waypoints_from_route(route_points)
        else:
            rospy.logwarn("Don hang moi nhung khong co routePoints")

        self.switch_to_waiting()

    def _listen_worker(self):
        def on_error(exc: Exception):
            rospy.logerr(f"[ERROR] websocket: {exc}")

        def should_stop() -> bool:
            return (not self.is_listening) or rospy.is_shutdown()

        rospy.loginfo("Bat dau lang nghe don hang tu BE WebSocket...")
        self.ws_client.listen_orders(
            on_change=self.handle_order_change,
            on_error=on_error,
            retry_delay_seconds=5.0,
            should_stop=should_stop,
        )

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        node = OrderListenerStateMachine()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Order Listener Node da dung")
