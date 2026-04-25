#!/usr/bin/env python

import rospy
import tf
import tf.transformations as tr
import math
import numpy as np
from sensor_msgs.msg import NavSatFix, Imu

class GpsOdomCorrector:
    def __init__(self):
        rospy.init_node('gps_odom_corrector')

        self.gps_topic = rospy.get_param('~gps_topic', '/fix')  # Đảm bảo topic đúng
        self.imu_topic = rospy.get_param('~imu_topic', '/imu/data')
        self.map_frame = 'map'
        self.odom_frame = 'odom'
        self.base_frame = rospy.get_param('~base_frame', 'base_link')  # Kiểm tra đúng base_link hay base_footprint
        self.yaw_offset = rospy.get_param('~yaw_offset', 0.0)
        self.enu_rotation_offset = rospy.get_param('~enu_rotation_offset', math.pi / 2)  # Thử pi/2, -pi/2, 0, pi

        rospy.loginfo("=== GPS ODOM CORRECTOR DEBUG ===")
        rospy.loginfo("GPS topic: %s", self.gps_topic)
        rospy.loginfo("Base frame: %s", self.base_frame)
        rospy.loginfo("ENU rotation offset: %.2f rad (%.0f deg)", self.enu_rotation_offset, math.degrees(self.enu_rotation_offset))

        self.gps_sub = rospy.Subscriber(self.gps_topic, NavSatFix, self.gps_callback)
        self.imu_sub = rospy.Subscriber(self.imu_topic, Imu, self.imu_callback)

        self.br = tf.TransformBroadcaster()
        self.listener = tf.TransformListener()

        self.origin_lat = None
        self.origin_lon = None
        self.origin_set = False

        self.current_quat = (0.0, 0.0, 0.0, 1.0)

    def imu_callback(self, msg):
        if msg.orientation_covariance[0] >= 0:
            quat_orig = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]
            euler = tr.euler_from_quaternion(quat_orig)
            yaw_fixed = euler[2] + self.yaw_offset
            self.current_quat = tr.quaternion_from_euler(euler[0], euler[1], yaw_fixed)
            rospy.logdebug("IMU yaw fixed: %.2f deg", math.degrees(yaw_fixed))

    def gps_callback(self, msg):
        if msg.status.status < 0:
            rospy.logwarn("GPS no fix")
            return

        if not self.origin_set:
            self.origin_lat = msg.latitude
            self.origin_lon = msg.longitude
            self.origin_set = True
            rospy.loginfo("Origin set: lat=%.6f lon=%.6f", self.origin_lat, self.origin_lon)
            return

        # ENU raw
        delta_lat = msg.latitude - self.origin_lat
        delta_lon = msg.longitude - self.origin_lon
        x_east = delta_lon * 111139 * math.cos(math.radians(self.origin_lat))
        y_north = delta_lat * 111139

        rospy.loginfo("Raw GPS delta: East=%.2f m, North=%.2f m", x_east, y_north)

        # Rotation
        theta = self.enu_rotation_offset
        cos_th = math.cos(theta)
        sin_th = math.sin(theta)
        x_rot = x_east * cos_th - y_north * sin_th
        y_rot = x_east * sin_th + y_north * cos_th

        rospy.loginfo("After rotation (offset=%.2f rad): x=%.2f, y=%.2f", theta, x_rot, y_rot)

        t_map_base = (x_rot, y_rot, 0.0)
        q_map_base = self.current_quat

        # Lookup odom -> base
        try:
            (t_odom_base, q_odom_base) = self.listener.lookupTransform(
                self.odom_frame, self.base_frame, rospy.Time(0))
            rospy.logdebug("Lookup odom->base OK: t=(%.2f, %.2f, %.2f)", *t_odom_base)
        except Exception as e:
            rospy.logwarn("Lookup odom->%s failed: %s", self.base_frame, str(e))
            return

        # Compose
        q_base_odom = tr.quaternion_inverse(q_odom_base)
        rot_base_odom = tr.quaternion_matrix(q_base_odom)[:3, :3]
        t_base_odom = -rot_base_odom.dot(t_odom_base)

        q_map_odom = tr.quaternion_multiply(q_map_base, q_base_odom)
        rot_map_base = tr.quaternion_matrix(q_map_base)[:3, :3]
        t_map_odom = np.array(t_map_base) + rot_map_base.dot(t_base_odom)

        rospy.loginfo("Publishing map->odom: trans=(%.2f, %.2f, %.2f)", *t_map_odom)

        self.br.sendTransform(
            t_map_odom.tolist(),
            q_map_odom,
            rospy.Time.now(),
            self.odom_frame,
            self.map_frame
        )

def main():
    try:
        corrector = GpsOdomCorrector()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()