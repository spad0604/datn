#!/usr/bin/env python3
import rospy
import tf2_ros
import tf2_geometry_msgs  # <<<--- THÊM DÒNG NÀY ĐỂ FIX LỖI TypeException
from geometry_msgs.msg import PoseStamped, PoseArray
import utm  # Giờ bạn đã cài thành công utm rồi đúng không?

class LatLonToMapChecker:
    def __init__(self):
        rospy.init_node('latlon_to_map_checker', anonymous=True)

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)

        self.map_to_utm_transform = None

        # Hardcode các điểm lat/long bạn muốn kiểm tra
        self.route_points = [
           {"lat": 21.01149008333333, "lon": 105.82648918333334},  
            {"lat": 21.0115071, "lon": 105.8264791},
            {"lat":21.011508466666665, "lon": 105.82647778333333},
            {"lat": 10.764000, "lon": 106.662000},
            # Thêm điểm khác ở đây
        ]

        rospy.loginfo("Đang chờ static TF giữa 'map' và 'utm'...")
        self.wait_for_transform()

        if self.map_to_utm_transform is not None:
            self.convert_and_print_waypoints()
        else:
            rospy.logerr("Không lấy được transform. Kết thúc.")

    def wait_for_transform(self):
        rate = rospy.Rate(10.0)
        while not rospy.is_shutdown():
            try:
                # Thử lấy transform map → utm (static TF thường là map → utm hoặc ngược lại)
                trans = self.tf_buffer.lookup_transform("map", "utm", rospy.Time(0), rospy.Duration(5.0))
                self.map_to_utm_transform = trans
                rospy.loginfo("Đã nhận được static TF: map → utm")
                rospy.loginfo(f"   Translation: ({trans.transform.translation.x:.3f}, "
                              f"{trans.transform.translation.y:.3f}, {trans.transform.translation.z:.3f})")
                rospy.loginfo(f"   Rotation (quat x,y,z,w): {trans.transform.rotation.x:.3f}, "
                              f"{trans.transform.rotation.y:.3f}, {trans.transform.rotation.z:.3f}, "
                              f"{trans.transform.rotation.w:.3f}")
                break
            except (tf2_ros.LookupException, tf2_ros.ConnectivityException,
                    tf2_ros.ExtrapolationException) as e:
                rospy.logwarn_throttle(5, f"Chưa có TF map ↔ utm: {e}")
                rate.sleep()

    def convert_and_print_waypoints(self):
        rospy.loginfo(f"Chuyển {len(self.route_points)} điểm lat/lon hardcode → frame map\n")

        pose_array = PoseArray()
        pose_array.header.frame_id = "map"
        pose_array.header.stamp = rospy.Time.now()

        for i, pt in enumerate(self.route_points):
            lat = pt["lat"]
            lon = pt["lon"]

            # 1. Lat/Lon → UTM chính xác
            utm_e, utm_n, zone_num, zone_letter = utm.from_latlon(lat, lon)

            # 2. Tạo PoseStamped trong frame utm
            utm_pose = PoseStamped()
            utm_pose.header.frame_id = "utm"
            utm_pose.header.stamp = rospy.Time(0)  # static
            utm_pose.pose.position.x = utm_e
            utm_pose.pose.position.y = utm_n
            utm_pose.pose.position.z = 0.0
            utm_pose.pose.orientation.w = 1.0

            # 3. Transform sang map — giờ sẽ hoạt động nhờ tf2_geometry_msgs
            try:
                map_pose = self.tf_buffer.transform(utm_pose, "map", rospy.Duration(1.0))
            except Exception as e:
                rospy.logerr(f"Transform thất bại cho waypoint {i}: {e}")
                continue

            pose_array.poses.append(map_pose.pose)

            rospy.loginfo(f"Waypoint {i}: ({lat:.7f}, {lon:.7f}) → "
                          f"UTM ({utm_e:.3f}, {utm_n:.3f}) → "
                          f"map ({map_pose.pose.position.x:.3f}, {map_pose.pose.position.y:.3f})")

        # Publish để visualize trong RViz
        pub = rospy.Publisher('/checked_waypoints', PoseArray, queue_size=10, latch=True)
        pub.publish(pose_array)
        rospy.loginfo("Đã publish PoseArray tới topic /checked_waypoints (xem trong RViz)")

if __name__ == '__main__':
    try:
        checker = LatLonToMapChecker()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass