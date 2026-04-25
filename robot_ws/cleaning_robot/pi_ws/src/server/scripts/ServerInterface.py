#!/usr/bin/env python3
# -*- coding: utf-8__ 

"""
ROS Node: Theo dõi đơn hàng Firebase với State Machine
- Trạng thái LISTENING: Lắng nghe real-time đơn hàng
- Trạng thái WAITING: Dừng lắng nghe, chờ tín hiệu từ /start_listening để tiếp tục
"""

import rospy
from std_msgs.msg import String
import threading
import requests
import json
from typing import List, Dict, Any
from geometry_msgs.msg import PoseStamped, PoseArray

import utm
import tf.transformations
import math
import tf2_ros
import tf2_geometry_msgs
from firebase_sample import FirebaseClient, Order


class OrderListenerStateMachine:
    def __init__(self):
        rospy.init_node('order_listener_sm', anonymous=False)

        # Firebase
        firebase_url = "https://robot-delivery-cbdcf-default-rtdb.firebaseio.com"
        self.firebase = FirebaseClient(firebase_url)

        # State
        self.state = "LISTENING"  # Ban đầu lắng nghe ngay
        self.is_listening = True
        self.listen_thread = None
      
        # TF buffer
        self.tf_buffer = tf2_ros.Buffer(rospy.Duration(60.0))  # cache lâu
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        self.map_to_utm_transform = None
        self._wait_and_get_static_transform()
        # Subscriber điều khiển
        rospy.Subscriber("/Status_robot", String, self.start_listening_callback)
        self.waypoint_pub = rospy.Publisher('/waypoints', PoseArray, queue_size=10, latch=True)
        # Bắt đầu lắng nghe ngay khi khởi động
        self.start_listen_thread()
        self.ref_lat = None
        self.ref_lon = None
        rospy.loginfo("Order Listener State Machine khởi động!")
        rospy.loginfo("Trạng thái ban đầu: LISTENING (đang lắng nghe đơn hàng)")
    def _wait_and_get_static_transform(self):
        """Lấy transform map ← utm một lần, chờ đến khi có"""
        rospy.loginfo("Đang chờ static transform từ 'utm' đến 'map'...")
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            try:
                # lookup_transform(target_frame, source_frame, time)
                self.map_to_utm_transform = self.tf_buffer.lookup_transform(
                    "map", "utm", rospy.Time(0), rospy.Duration(5.0)
                    
                )
                rospy.loginfo("ĐÃ LẤY ĐƯỢC static transform utm → map! Có thể dùng vĩnh viễn.")
                break
            except (tf2_ros.LookupException, tf2_ros.ExtrapolationException) as e:
                rospy.logwarn_throttle(10, f"Chưa có TF utm -> map: {e}. Đang chờ navsat_transform set datum...")
                rate.sleep()

    # ====================== ĐIỀU KHIỂN STATE ======================
    def start_listening_callback(self, msg):
        if msg.data=="STARTING" and self.state == "WAITING":
            rospy.loginfo("Nhận tín hiệu từ /start_listening → Chuyển sang LISTENING")
            self.state = "LISTENING"
            self.is_listening = True
            self.start_listen_thread()
    def publish_waypoints_from_route(self, route_points):
        if not route_points:
            return

        if self.map_to_utm_transform is None:
            rospy.logerr("Chưa có transform utm -> map! Không thể chuyển waypoint.")
            return

        pose_array = PoseArray()
        pose_array.header.frame_id = "map"
        pose_array.header.stamp = rospy.Time.now()

        rospy.loginfo(f"Chuyển {len(route_points)} điểm lat/lon → map frame (dùng static TF)")

        for i, pt in enumerate(route_points):
            lat = pt.lat
            lon = pt.lng

            # 1. Lat/lon → UTM chính xác
            utm_x, utm_y,zone_num, zone_letter =utm.from_latlon(lat, lon)

            # 2. Tạo pose trong utm frame
            utm_pose = PoseStamped()
            utm_pose.header.frame_id = "utm"
            utm_pose.header.stamp = rospy.Time.now()  # static nên timestamp không quan trọng
            utm_pose.pose.position.x = utm_x
            utm_pose.pose.position.y = utm_y
            utm_pose.pose.position.z = 0.0
            utm_pose.pose.orientation.w = 1.0

            # 3. Transform sang map (chỉ 1 lần init, dùng lại mãi mãi)
            map_pose = tf2_geometry_msgs.do_transform_pose(utm_pose, self.map_to_utm_transform)

            # Thêm vào array
            pose_array.poses.append(map_pose.pose)

            rospy.loginfo(f"Waypoint {i}: ({lat:.7f}, {lon:.7f}) → map ({map_pose.pose.position.x:.3f}, {map_pose.pose.position.y:.3f})")

        self.waypoint_pub.publish(pose_array)
        rospy.loginfo(f"ĐÃ PUBLISH {len(pose_array.poses)} WAYPOINT trong frame map")
    def switch_to_waiting(self):
        if self.state == "LISTENING":
            rospy.loginfo("Có đơn hàng mới → Chuyển sang WAITING (dừng lắng nghe)")
            self.state = "WAITING"
            self.is_listening = False
            # Thread sẽ tự dừng nhờ kiểm tra self.is_listening

    def start_listen_thread(self):
        if self.listen_thread is not None and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)  # Dọn thread cũ nếu có
        self.listen_thread = threading.Thread(target=self._listen_worker, daemon=True)
        self.listen_thread.start()

    # ====================== CALLBACK XỬ LÝ ĐƠN HÀNG ======================
    def handle_order_change(self, orders: List[Order], payload: Dict[str, Any], event_type: str):
        pending_orders = [o for o in orders if o.status == "pending"]
        rospy.loginfo("=" * 80)
        rospy.loginfo(f"Event: {event_type}")
        rospy.loginfo(f"Tổng số đơn hàng: {len(orders)}")
        rospy.loginfo(f"Số đơn đang chờ (pending): {len(pending_orders)}")
        rospy.loginfo("-" * 80)

        for order in orders[:10]:  # In tối đa 10 đơn
            # In thông tin cơ bản
            rospy.loginfo(f"ID: {order.id}")
            rospy.loginfo(f"   Người nhận: {order.receiverName} | Trạng thái: {order.status}")
            rospy.loginfo(f"   Hàng: {order.goods}")
            rospy.loginfo(f"   Thời gian: {order.createdAt}")

            # === IN TỌA ĐỘ ĐÍCH ===
            dest_lat = getattr(order, 'destinationLat', None)
            dest_lng = getattr(order, 'destinationLng', None)
            if dest_lat is not None and dest_lng is not None:
                rospy.loginfo(f"   ĐIỂM ĐÍCH: lat={dest_lat}, lng={dest_lng}")
            else:
                rospy.loginfo("   ĐIỂM ĐÍCH: Không có")

            # === IN ROUTE POINTS ===
            route_points = getattr(order, 'routePoints', None)
            if route_points and isinstance(route_points, list):
                rospy.loginfo(f"   ĐƯỜNG ĐI: {len(route_points)} điểm")
                for i, pt in enumerate(route_points[:2]):  # In 8 điểm đầu
                    # Sửa ở đây: dùng .lat, .lng, .order thay vì dict
                    order_idx = getattr(pt, 'order', i)  # phòng trường hợp không có
                    lat = getattr(pt, 'lat', 'N/A')
                    lng = getattr(pt, 'lng', 'N/A')
                    rospy.loginfo(f"      [{order_idx:2d}] lat: {lat}, lng: {lng}")
                # if len(route_points) > 8:
                #     rospy.loginfo(f"      ... còn {len(route_points) - 8} điểm nữa")
            else:
                rospy.loginfo("   ĐƯỜNG ĐI: Không có")

            rospy.loginfo("-" * 80)

        # Phần xử lý waypoint cũ (nếu có thay đổi riêng)
        if payload and "data" in payload:
            changed = payload["data"]
            if isinstance(changed, dict):
                for oid, data in changed.items():
                    if data and "waypoints" in data:
                        rospy.loginfo(f" ⚑ Waypoint mới cho đơn {oid}: {len(data['waypoints'])} điểm")

        # Chuyển trạng thái nếu có pending
        if pending_orders:
            latest = pending_orders[0]  # Lấy đơn mới nhất (hoặc bạn có thể chọn theo ý)
            rospy.logwarn(f"✅ NHẬN ĐƯỢC ĐƠN HÀNG MỚI: {latest.id} - {latest.receiverName}")

            route_points = getattr(latest, 'routePoints', None)
            if route_points and len(route_points) > 0:
                # Reset điểm gốc
                self.ref_lat = None
                self.ref_lon = None

             

                rospy.loginfo(f"Đang chuyển đổi {len(route_points)} điểm Lat/Lon sang ENU và publish waypoint...")

                self.publish_waypoints_from_route(route_points)
               
            else:
                rospy.logwarn("Đơn hàng mới nhưng không có routePoints!")

            self.switch_to_waiting()

    # ====================== WORKER LẮNG NGHE ======================
    def _listen_worker(self):
        def on_error(exc):
            rospy.logerr(f"[ERROR] Lỗi stream orders: {exc}")

        while self.is_listening and not rospy.is_shutdown():
            try:
                rospy.loginfo("Bắt đầu lắng nghe đơn hàng real-time từ Firebase...")
                url = f"{self.firebase.base_url}/orders.json"
                headers = {"Accept": "text/event-stream"}
                params = {"print": "silent"}

                with requests.get(url, stream=True, headers=headers, params=params, timeout=60) as response:
                    response.raise_for_status()
                    event_type = None
                    data_buffer = []

                    for raw_line in response.iter_lines(decode_unicode=True):
                        if not self.is_listening or rospy.is_shutdown():
                            rospy.loginfo("Dừng lắng nghe (state WAITING hoặc shutdown)")
                            return

                        if raw_line is None:
                            continue
                        line = raw_line.strip()

                        if line == "":  # Kết thúc event
                            if data_buffer:
                                try:
                                    payload_str = "\n".join(data_buffer)
                                    payload = json.loads(payload_str) if payload_str else {}
                                except json.JSONDecodeError as exc:
                                    on_error(exc)
                                    data_buffer = []
                                    continue

                                orders_dict = self.firebase.get_all_orders()
                                orders_list = sorted(
                                    orders_dict.values(),
                                    key=lambda o: o.createdAt,
                                    reverse=True
                                )
                                self.handle_order_change(orders_list, payload, event_type or "message")

                                data_buffer = []
                                event_type = None

                        elif line.startswith("event:"):
                            event_type = line[len("event:"):].strip()
                        elif line.startswith("data:"):
                            data_buffer.append(line[len("data:"):].strip())

            except requests.exceptions.RequestException as exc:
                if not self.is_listening or rospy.is_shutdown():
                    return
                on_error(exc)
                rospy.logwarn("Mất kết nối → chờ 5s trước khi thử lại...")
                rospy.sleep(5.0)

            except Exception as exc:
                if not self.is_listening or rospy.is_shutdown():
                    return
                on_error(exc)
                rospy.sleep(5.0)

            if self.is_listening and not rospy.is_shutdown():
                rospy.sleep(1.0)  # Delay nhỏ trước reconnect

    # ====================== RUN ======================
    def run(self):
        # Chỉ cần giữ node sống, tất cả xử lý trong thread và callback
        rospy.spin()


if __name__ == "__main__":
    try:
        node = OrderListenerStateMachine()
        node.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("Order Listener Node đã dừng.")