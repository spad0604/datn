#!/usr/bin/env python3
"""
LiDAR processor with optional XY plotting and a lightweight DWA-style obstacle
avoidance controller for test driving.
"""

import math
import os
import threading

import numpy as np
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class LidarProcessor:
    def __init__(self):
        rospy.init_node("lidar_processor", anonymous=False)

        self.scan_topic = rospy.get_param("~scan_topic", "/scan")
        self.cmd_topic = rospy.get_param("~cmd_topic", "/cmd_vel")
        self.enable_plot = rospy.get_param("~plot", rospy.get_param("~olot", False))
        self.enable_dwa_test = rospy.get_param("~enable_dwa_test", False)

        self.robot_radius = rospy.get_param("~robot_radius", 0.22)
        self.safety_margin = rospy.get_param("~safety_margin", 0.08)
        self.front_angle_deg = rospy.get_param("~front_angle_deg", 35.0)
        self.emergency_stop_distance = rospy.get_param("~emergency_stop_distance", 0.42)
        self.slow_down_distance = rospy.get_param("~slow_down_distance", 0.75)
        self.self_filter_x_min = rospy.get_param("~self_filter_x_min", -0.30)
        self.self_filter_x_max = rospy.get_param("~self_filter_x_max", 0.52)
        self.self_filter_y_min = rospy.get_param("~self_filter_y_min", -0.22)
        self.self_filter_y_max = rospy.get_param("~self_filter_y_max", 0.22)

        self.cruise_linear_speed = rospy.get_param("~cruise_linear_speed", 0.12)
        self.max_linear_speed = rospy.get_param("~max_linear_speed", 0.18)
        self.max_angular_speed = rospy.get_param("~max_angular_speed", 1.2)
        self.escape_angular_speed = rospy.get_param("~escape_angular_speed", 0.8)
        self.max_linear_accel = rospy.get_param("~max_linear_accel", 0.25)
        self.max_angular_accel = rospy.get_param("~max_angular_accel", 1.8)
        self.linear_samples = rospy.get_param("~linear_samples", 6)
        self.angular_samples = rospy.get_param("~angular_samples", 21)
        self.prediction_time = rospy.get_param("~prediction_time", 1.5)
        self.sim_dt = rospy.get_param("~sim_dt", 0.15)
        self.plot_limit = rospy.get_param("~plot_limit", 3.0)

        self.laser_offset_x = rospy.get_param("~laser_offset_x", 0.4)
        self.laser_offset_y = rospy.get_param("~laser_offset_y", 0.0)

        self.latest_scan = None
        self.latest_points = np.empty((0, 2))
        self.latest_trajectory = np.zeros((1, 3))
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.plot_backend = None
        self.headless = False
        self.plot_lock = threading.Lock()
        self.plot_dirty = False
        self.plot_points = np.empty((0, 2))
        self.plot_trajectory = np.zeros((1, 3))
        self.plot_linear = 0.0
        self.plot_angular = 0.0
        self.plot_rate_hz = rospy.get_param("~plot_rate_hz", 10.0)

        self.scan_sub = rospy.Subscriber(self.scan_topic, LaserScan, self.scan_callback)
        self.processed_pub = rospy.Publisher("/scan_processed", LaserScan, queue_size=10)
        self.cmd_pub = rospy.Publisher(self.cmd_topic, Twist, queue_size=1)

        self.plot_ready = False
        if self.enable_plot:
            self._setup_plot()

        rospy.on_shutdown(self.on_shutdown)
        rospy.loginfo(
            "LiDAR processor started | scan=%s | plot=%s | dwa_test=%s | cmd_topic=%s",
            self.scan_topic,
            self.enable_plot,
            self.enable_dwa_test,
            self.cmd_topic,
        )
        self.run()

    def _setup_plot(self):
        try:
            import matplotlib
            import matplotlib.pyplot as plt
        except ImportError:
            rospy.logwarn("matplotlib is not installed; disable plot mode.")
            self.enable_plot = False
            return

        self.plot_backend = matplotlib.get_backend()
        self.headless = not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))

        if self.headless:
            rospy.logwarn(
                "Plot requested but no GUI display is available (DISPLAY/WAYLAND_DISPLAY missing). "
                "Interactive popup will not appear. Current backend: %s",
                self.plot_backend,
            )

        try:
            self.plt = plt
            self.plt.ion()
            self.fig, self.ax = self.plt.subplots(figsize=(7, 7))
            self.scan_scatter = self.ax.scatter([], [], s=10, c="tab:blue", alpha=0.75, label="LiDAR XY")
            self.predicted_line, = self.ax.plot([], [], color="tab:red", linewidth=2.0, label="DWA predicted")
            self.heading_line, = self.ax.plot([], [], color="tab:green", linewidth=2.0, label="Robot heading")
            self.ax.set_title("LiDAR XY / DWA Preview")
            self.ax.set_xlabel("x (m)")
            self.ax.set_ylabel("y (m)")
            self.ax.set_xlim(-self.plot_limit, self.plot_limit)
            self.ax.set_ylim(-self.plot_limit, self.plot_limit)
            self.ax.set_aspect("equal", adjustable="box")
            self.ax.grid(True, alpha=0.3)
            self.ax.legend(loc="upper right")
            self.plt.show(block=False)
            self.plot_ready = True
            rospy.loginfo("Matplotlib plot initialized with backend: %s", self.plot_backend)
        except Exception as exc:
            rospy.logwarn("Cannot initialize plot window: %s", exc)
            self.enable_plot = False
            self.plot_ready = False

    def scan_callback(self, msg):
        self.latest_scan = msg
        processed_msg, points = self.process_scan(msg)
        self.latest_points = points
        self.processed_pub.publish(processed_msg)

        best_linear, best_angular, trajectory, clearance, front_clearance, left_clearance, right_clearance = self.compute_dwa_command(points)
        self.latest_trajectory = trajectory

        if self.enable_dwa_test:
            cmd = Twist()
            cmd.linear.x = best_linear
            cmd.angular.z = best_angular
            self.cmd_pub.publish(cmd)
            self.current_linear = best_linear
            self.current_angular = best_angular
            rospy.loginfo_throttle(
                1.0,
                "DWA cmd | v=%.2f m/s | w=%.2f rad/s | clr=%.2f m | front=%.2f | left=%.2f | right=%.2f",
                best_linear,
                best_angular,
                clearance,
                front_clearance,
                left_clearance,
                right_clearance,
            )
        else:
            self.current_linear = best_linear
            self.current_angular = best_angular
            rospy.loginfo_throttle(
                2.0,
                "DWA preview only | v=%.2f m/s | w=%.2f rad/s | clr=%.2f m | front=%.2f | left=%.2f | right=%.2f",
                best_linear,
                best_angular,
                clearance,
                front_clearance,
                left_clearance,
                right_clearance,
            )

        if self.plot_ready:
            with self.plot_lock:
                self.plot_points = np.array(points, copy=True)
                self.plot_trajectory = np.array(trajectory, copy=True)
                self.plot_linear = float(best_linear)
                self.plot_angular = float(best_angular)
                self.plot_dirty = True

    def process_scan(self, msg):
        ranges = np.asarray(msg.ranges, dtype=np.float32)
        angles = msg.angle_min + np.arange(len(ranges), dtype=np.float32) * msg.angle_increment
        valid_mask = np.isfinite(ranges) & (ranges >= msg.range_min) & (ranges <= msg.range_max)

        valid_ranges = ranges[valid_mask]
        valid_angles = angles[valid_mask]
        x_points = valid_ranges * np.cos(valid_angles) + self.laser_offset_x
        y_points = valid_ranges * np.sin(valid_angles) + self.laser_offset_y

        if valid_ranges.size > 0:
            points = np.column_stack((x_points, y_points))
        else:
            points = np.empty((0, 2))

        if points.size > 0:
            self_mask = (
                (points[:, 0] >= self.self_filter_x_min)
                & (points[:, 0] <= self.self_filter_x_max)
                & (points[:, 1] >= self.self_filter_y_min)
                & (points[:, 1] <= self.self_filter_y_max)
            )
            points = points[~self_mask]

        processed_ranges = np.array(msg.ranges, dtype=np.float32)
        invalid_mask = ~np.isfinite(processed_ranges) | (processed_ranges < msg.range_min)
        processed_ranges[invalid_mask] = float("inf")

        processed_msg = LaserScan()
        processed_msg.header = msg.header
        processed_msg.angle_min = msg.angle_min
        processed_msg.angle_max = msg.angle_max
        processed_msg.angle_increment = msg.angle_increment
        processed_msg.time_increment = msg.time_increment
        processed_msg.scan_time = msg.scan_time
        processed_msg.range_min = msg.range_min
        processed_msg.range_max = msg.range_max
        processed_msg.ranges = processed_ranges.tolist()
        processed_msg.intensities = list(msg.intensities)
        return processed_msg, points

    def compute_dwa_command(self, points):
        front_clearance = self._sector_clearance(points, -self.front_angle_deg, self.front_angle_deg)
        left_clearance = self._sector_clearance(points, 15.0, 120.0)
        right_clearance = self._sector_clearance(points, -120.0, -15.0)

        v_window_min = max(0.0, self.current_linear - self.max_linear_accel * self.sim_dt)
        v_window_max = min(self.max_linear_speed, self.current_linear + self.max_linear_accel * self.sim_dt)
        w_window_min = max(-self.max_angular_speed, self.current_angular - self.max_angular_accel * self.sim_dt)
        w_window_max = min(self.max_angular_speed, self.current_angular + self.max_angular_accel * self.sim_dt)

        linear_samples = np.linspace(v_window_min, v_window_max, max(2, self.linear_samples))
        angular_samples = np.linspace(w_window_min, w_window_max, max(3, self.angular_samples))

        if front_clearance < self.emergency_stop_distance:
            linear_samples = np.array([0.0])
            angular_samples = np.linspace(-self.max_angular_speed, self.max_angular_speed, max(5, self.angular_samples))

        best_score = -float("inf")
        best_linear = 0.0
        best_angular = 0.0
        best_traj = self.simulate_trajectory(0.0, 0.0)
        best_clearance = 0.0

        for linear_speed in linear_samples:
            for angular_speed in angular_samples:
                trajectory = self.simulate_trajectory(linear_speed, angular_speed)
                clearance = self.compute_trajectory_clearance(trajectory, points)
                if clearance < self.safety_margin:
                    continue

                end_x = trajectory[-1, 0]
                end_y = trajectory[-1, 1]
                heading_error = abs(trajectory[-1, 2])
                turn_penalty = abs(angular_speed)
                speed_bonus = linear_speed
                lateral_penalty = abs(end_y)

                score = (
                    2.6 * end_x
                    + 1.8 * clearance
                    + 1.0 * speed_bonus
                    - 0.7 * turn_penalty
                    - 0.4 * heading_error
                    - 0.6 * lateral_penalty
                )

                if front_clearance < self.slow_down_distance:
                    score -= max(0.0, linear_speed - self.cruise_linear_speed * 0.65) * 3.0

                if score > best_score:
                    best_score = score
                    best_linear = linear_speed
                    best_angular = angular_speed
                    best_traj = trajectory
                    best_clearance = clearance

        if best_score == -float("inf"):
            turn_left = left_clearance >= right_clearance
            best_linear = 0.0
            best_angular = self.escape_angular_speed if turn_left else -self.escape_angular_speed
            best_traj = self.simulate_trajectory(best_linear, best_angular)
            best_clearance = min(left_clearance, right_clearance, front_clearance)

        if front_clearance > self.slow_down_distance:
            best_linear = max(best_linear, self.cruise_linear_speed)
            best_linear = min(best_linear, self.max_linear_speed)
            best_traj = self.simulate_trajectory(best_linear, best_angular)
            best_clearance = self.compute_trajectory_clearance(best_traj, points)

        if front_clearance < self.emergency_stop_distance:
            best_linear = 0.0
            best_traj = self.simulate_trajectory(best_linear, best_angular)
            best_clearance = self.compute_trajectory_clearance(best_traj, points)

        return best_linear, best_angular, best_traj, best_clearance, front_clearance, left_clearance, right_clearance

    def _sector_clearance(self, points, angle_min_deg, angle_max_deg):
        if points.size == 0:
            return float("inf")

        angles = np.degrees(np.arctan2(points[:, 1], points[:, 0]))
        mask = (angles >= angle_min_deg) & (angles <= angle_max_deg)
        if not np.any(mask):
            return float("inf")

        sector_points = points[mask]
        distances = np.linalg.norm(sector_points, axis=1)
        return float(np.min(distances))

    def simulate_trajectory(self, linear_speed, angular_speed):
        steps = max(2, int(self.prediction_time / self.sim_dt))
        trajectory = np.zeros((steps + 1, 3), dtype=np.float32)

        x_pos = 0.0
        y_pos = 0.0
        yaw = 0.0
        for index in range(1, steps + 1):
            x_pos += linear_speed * math.cos(yaw) * self.sim_dt
            y_pos += linear_speed * math.sin(yaw) * self.sim_dt
            yaw += angular_speed * self.sim_dt
            trajectory[index] = (x_pos, y_pos, yaw)

        return trajectory

    def compute_trajectory_clearance(self, trajectory, points):
        if points.size == 0:
            return self.plot_limit

        min_clearance = float("inf")
        for state in trajectory[:, :2]:
            distances = np.linalg.norm(points - state, axis=1)
            state_clearance = float(np.min(distances)) - self.robot_radius
            if state_clearance < min_clearance:
                min_clearance = state_clearance
            if min_clearance < self.safety_margin:
                return min_clearance

        return min_clearance

    def update_plot(self, points, trajectory, linear_speed, angular_speed):
        if points.size > 0:
            self.scan_scatter.set_offsets(points)
        else:
            self.scan_scatter.set_offsets(np.empty((0, 2)))

        self.predicted_line.set_data(trajectory[:, 0], trajectory[:, 1])
        heading_length = 0.35
        self.heading_line.set_data([0.0, heading_length], [0.0, 0.0])
        mode_label = "ACTIVE" if self.enable_dwa_test else "PREVIEW"
        self.ax.set_title(
            "LiDAR XY / DWA Preview | %s | v=%.2f m/s | w=%.2f rad/s"
            % (mode_label, linear_speed, angular_speed)
        )
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        self.plt.pause(0.001)

    def run(self):
        rate = rospy.Rate(self.plot_rate_hz)
        while not rospy.is_shutdown():
            if self.plot_ready:
                payload = None
                with self.plot_lock:
                    if self.plot_dirty:
                        payload = (
                            np.array(self.plot_points, copy=True),
                            np.array(self.plot_trajectory, copy=True),
                            self.plot_linear,
                            self.plot_angular,
                        )
                        self.plot_dirty = False
                if payload is not None:
                    points, trajectory, linear_speed, angular_speed = payload
                    try:
                        self.update_plot(points, trajectory, linear_speed, angular_speed)
                    except Exception as exc:
                        rospy.logwarn_throttle(5.0, "Plot update failed: %s", exc)
            rate.sleep()

    def on_shutdown(self):
        if self.enable_dwa_test:
            stop_msg = Twist()
            self.cmd_pub.publish(stop_msg)
            rospy.loginfo("LiDAR processor shutdown: published zero cmd_vel.")


if __name__ == "__main__":
    try:
        LidarProcessor()
    except rospy.ROSInterruptException:
        pass
