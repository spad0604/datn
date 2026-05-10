#!/usr/bin/env python3

import math
import time

import numpy as np
import rospy
import serial
import tf
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool, Float32, Int32


class MecanumRobot:
    def __init__(self):
        rospy.init_node('mecanum_robot')
        print("INIT")
        self.NMOTORS = 4
        self.MotorError = False
        self.total_length = 52.89
        self.onOffMor = False
        self.M_LEFT = 0
        self.M_RIGHT = 1
        self.M_RIGHT_DOWN = 3
        self.acc_time = 10
        self.dec_time = 10
        self.M_RIGHT_UP = 2
        self.M_LEFT_DOWN = 1
        self.M_LEFT_UP = 0
        self.coeff_speed = 1.0
        self.moving = False
        self.use_imu = rospy.get_param('~use_imu', False)
        print(self.use_imu)

        self.tf_broadcaster = tf.TransformBroadcaster()
        self.last_pose = None
        self.last_time = rospy.Time.now()
        self.odom_pub = rospy.Publisher('/odom', Odometry, queue_size=5)
        self.WHEEL_DIAMETER = rospy.get_param('~wheel_diameter', 9.5)
        self.ENCODER_TOTAL = rospy.get_param('~encoder_total', 1798)
        self.encoder_total = np.zeros(4)
        self.test_mode = rospy.get_param('~test_mode', 0)
        self.start_velocity_test = rospy.get_param('~start_run', 1.0)
        self.x_offset = rospy.get_param('~x_offset', 1.0)
        self.y_offset = rospy.get_param('~y_offset', 1.0)
        self.theta_offset = rospy.get_param('~theta_offset', 1.0)
        self.distance_move = rospy.get_param('~distance_move', 1.0)
        self.axis_move = rospy.get_param('~axis_move', 1.0)
        self.velocity_move = rospy.get_param('~velocity_move', 1.0)
        self.robot_pose = np.zeros(3)
        self.speed_desired = np.zeros(self.NMOTORS)
        self.speed_filter_x = 0.0
        self.speed_filter_y = 0.0
        self.speed_filter_z = 0.0
        self.last_speed_x = 0.0
        self.last_speed_y = 0.0
        self.last_speed_z = 0.0
        self.a_coeff = 0.52188555
        self.b_coeff = 0.23905722
        self.last_encod = np.zeros(4)
        self.xylanh = 1
        self.dtheta = 0.0
        self.cmd_msg = Twist()
        self.MotorErrorPub = rospy.Publisher('MOTOR_ERROR', Bool, queue_size=1)
        self.tf_broadcaster = tf.TransformBroadcaster()
        self.delta_encod_total1 = np.zeros(4)
        self.serial_port_name = rospy.get_param('~port', '/dev/esp32')
        self.baud = rospy.get_param('~baud', 57600)
        self.serial_port = serial.Serial(self.serial_port_name, self.baud)
        self.desired = rospy.Publisher('/speed_desired', Float32, queue_size=1)
        self.feedback = rospy.Publisher('/speed_feedback', Float32, queue_size=1)
        self.last_time_encod = rospy.Time.now()
        self.inverseDir = []
        self.teleop = False
        self.lastEncoderTick = [0, 0, 0, 0]
        self.delta_cvt = 60.0 / (math.pi * self.WHEEL_DIAMETER)
        self.vx_now = 0
        self.vy_now = 0
        self.theta_now = 0
        self.last_msg = 1

        self.vx_run = 0
        self.vy_run = 0
        self.w_run = 0

        self.speed_wheel_cm_s = [0, 0, 0, 0]
        self.getCmdVel = False
        encoder_parameter = (math.pi * self.WHEEL_DIAMETER) / self.ENCODER_TOTAL
        self.cmPerCount = encoder_parameter
        self.stop_all = False
        self.ms_pub_encoder = 50.0
        self.rate_hz = (2000.0 / self.ms_pub_encoder)
        self.ms_pid = 10.0
        print(f"total:{self.total_length}")
        self.rpm_to_cm_s = np.zeros(2)
        self.rate = rospy.Rate(self.rate_hz)
        rospy.Subscriber("/cmd_vel_timeout", Twist, self.cmdVelCb)
        rospy.Subscriber("/pid_config", Twist, self.pidConfigCb)

    def pidConfigCb(self, msg):
        kp = msg.linear.x
        ki = msg.linear.y
        kd = msg.linear.z
        self.send_pid_config(kp, ki, kd)

    def cmdVelCb(self, msg):
        self.getCmdVel = True
        self.vx_run = msg.linear.x * 100
        self.w_run = msg.angular.z
        self.calSpeed(self.vx_run, self.w_run)
        self.runRobot()

    def send_pid_config(self, kp, ki, kd):
        pid_data = "{:.2f}:{:.2f}#{:.2f};".format(kp, ki, kd)
        try:
            self.serial_port.write(pid_data.encode())
            rospy.loginfo("Sent PID config: KP={}, KI={}, KD={}".format(kp, ki, kd))
        except Exception as e:
            rospy.logerr("Error sending PID config: {}".format(e))

    def NormalizeOverflow(self, encoder_now, last_encod):
        new_delta = encoder_now - last_encod
        if new_delta > 10000:
            new_delta = (encoder_now - 32768) - (32768 + last_encod)
        elif new_delta < -10000:
            new_delta = (32768 + encoder_now) + (32768 - last_encod)
        return new_delta

    def CaldiffEncoder(self, motor_left, motor_right):
        delta_encod_l = self.NormalizeOverflow(self.encoder_total[motor_left], self.last_encod[motor_left])
        delta_encod_r = self.NormalizeOverflow(self.encoder_total[motor_right], self.last_encod[motor_right])
        self.last_encod[motor_left] = self.encoder_total[motor_left]
        self.last_encod[motor_right] = self.encoder_total[motor_right]
        return delta_encod_l, delta_encod_r

    def CylinderCB(self, msg):
        self.xylanh = msg.data

    def updatePos(self):
        encoderTick = [0, 0]
        delta_tick = [0, 0, 0, 0]
        delta = [0, 0]
        delta_l_u, delta_r_u = self.CaldiffEncoder(self.M_LEFT_UP, self.M_RIGHT_UP)
        delta_l, delta_r = self.CaldiffEncoder(self.M_LEFT_DOWN, self.M_RIGHT_DOWN)
        encoderTick = [delta_l_u, delta_l, delta_r_u, delta_r]

        for i in range(self.NMOTORS):
            delta_tick[i] = encoderTick[i] * self.cmPerCount
        delta[self.M_LEFT] = delta_tick[self.M_LEFT_DOWN]
        delta[self.M_RIGHT] = delta_tick[self.M_RIGHT_DOWN]

        dxy = (delta[self.M_LEFT] + delta[self.M_RIGHT]) / 2.0
        dtheta = ((delta[self.M_LEFT] - delta[self.M_RIGHT])) / self.total_length

        dx = math.cos(self.robot_pose[2] + (dtheta / 2.0)) * dxy
        dy = math.sin(self.robot_pose[2] + (dtheta / 2.0)) * dxy

        self.vx_now = 0
        self.vy_now = 0
        self.theta_now = 0
        current_time = rospy.Time.now()

        dt = (current_time - self.last_time_encod).to_sec()
        dxy = dxy / 100.0
        dx = dx / 100.0
        dy = dy / 100.0

        if dt > 0:
            self.vx_now = dxy / dt
            self.vy_now = 0
            self.theta_now = dtheta / dt

            self.robot_pose[0] += dx
            self.robot_pose[1] += dy
            self.robot_pose[2] += dtheta

            if self.robot_pose[2] >= math.pi:
                self.robot_pose[2] -= 2.0 * math.pi
            elif self.robot_pose[2] <= -math.pi:
                self.robot_pose[2] += 2.0 * math.pi

            odom = Odometry()
            odom.header.stamp = rospy.Time.now()
            odom.header.frame_id = "odom"
            odom.child_frame_id = "base_link"
            odom_x = self.robot_pose[0]
            odom_y = self.robot_pose[1]
            odom.pose.pose.position.x = odom_x
            odom.pose.pose.position.y = odom_y
            odom.pose.pose.position.z = 0.0

            q = tf.transformations.quaternion_from_euler(0, 0, self.robot_pose[2])
            odom.pose.pose.orientation.x = q[0]
            odom.pose.pose.orientation.y = q[1]
            odom.pose.pose.orientation.z = q[2]
            odom.pose.pose.orientation.w = q[3]
            odom_twist_yaw = 0.35
            if dtheta == 0:
                odom_twist_yaw = 1e-4

            odom.pose.covariance = [
                0.1, 0, 0, 0, 0, 0,
                0, 0.1, 0, 0, 0, 0,
                0, 0, 1e6, 0, 0, 0,
                0, 0, 0, 1e6, 0, 0,
                0, 0, 0, 0, 1e6, 0,
                0, 0, 0, 0, 0, odom_twist_yaw,
            ]

            odom.twist.covariance = [
                0.05, 0, 0, 0, 0, 0,
                0, 0.05, 0, 0, 0, 0,
                0, 0, 1e6, 0, 0, 0,
                0, 0, 0, 1e6, 0, 0,
                0, 0, 0, 0, 1e6, 0,
                0, 0, 0, 0, 0, odom_twist_yaw,
            ]

            speed_measure_x = self.vx_now
            speed_measure_y = self.vy_now
            speed_measure_z = self.theta_now
            self.speed_filter_x = self.a_coeff * self.speed_filter_x + self.b_coeff * speed_measure_x + self.last_speed_x * self.b_coeff
            self.speed_filter_y = self.a_coeff * self.speed_filter_y + self.b_coeff * speed_measure_y + self.last_speed_y * self.b_coeff
            self.speed_filter_z = self.a_coeff * self.speed_filter_z + self.b_coeff * speed_measure_z + self.last_speed_z * self.b_coeff
            self.last_speed_x = speed_measure_x
            self.last_speed_y = speed_measure_y
            self.last_speed_z = speed_measure_z
            odom.twist.twist.linear.x = self.speed_filter_x
            odom.twist.twist.angular.z = -self.speed_filter_z
            odom.twist.twist.linear.y = self.speed_filter_y
            self.odom_pub.publish(odom)

        self.last_time_encod = current_time

    def calSpeed(self, vx, dtheta):
        speed_cm_s = np.zeros(self.NMOTORS)

        left = (vx * self.coeff_speed - dtheta * self.total_length / 2.0)
        right = (vx * self.coeff_speed + dtheta * self.total_length / 2.0)
        speed_cm_s[self.M_LEFT_UP] = left
        speed_cm_s[self.M_LEFT_DOWN] = left
        speed_cm_s[self.M_RIGHT_UP] = right
        speed_cm_s[self.M_RIGHT_DOWN] = right

        for i in range(self.NMOTORS):
            self.speed_desired[i] = speed_cm_s[i] * ((self.ms_pid / 1000.0) / (self.cmPerCount))
            self.speed_desired[i] = int(speed_cm_s[i])
        print(self.speed_desired)

    def runRobot(self):
        speed_wheel = [0, 0, 0, 0]
        max_speed = 30
        scale_factor = 0.71
        for i in range(self.NMOTORS):
            speed_wheel[i] = int(self.speed_desired[i] * scale_factor)
            if speed_wheel[i] > max_speed:
                speed_wheel[i] = max_speed
            elif speed_wheel[i] < -max_speed:
                speed_wheel[i] = -max_speed
        serial_data = "{:.1f}/{:.1f};".format(self.speed_desired[self.M_LEFT_UP], self.speed_desired[self.M_RIGHT_UP])
        self.moving = True
        self.serial_port.write(serial_data.encode())

    def run(self):
        print("Encoder:" + str(self.ENCODER_TOTAL))
        print("Mode: " + str(self.test_mode))
        print("Wheel: " + str(self.WHEEL_DIAMETER))
        print("x_offset:" + str(self.x_offset))
        print("cm_per_count:" + str(self.cmPerCount))
        first_rec = 0
        while not rospy.is_shutdown():
            try:
                if self.serial_port.in_waiting > 0:
                    data_line = self.serial_port.readline().decode('utf-8').strip()
                    data_line = data_line.rstrip(';')
                    parts = data_line.split('/')

                    if len(parts) == 2:
                        try:
                            encoder_left = int(parts[0])
                            encoder_right = int(parts[1])

                            self.encoder_total[self.M_LEFT_UP] = encoder_left
                            self.encoder_total[self.M_LEFT_DOWN] = encoder_left
                            self.encoder_total[self.M_RIGHT_UP] = encoder_right
                            self.encoder_total[self.M_RIGHT_DOWN] = encoder_right

                            if not first_rec:
                                for i in range(0, self.NMOTORS):
                                    self.last_encod[i] = self.encoder_total[i]
                                    if self.encoder_total[i] != 0:
                                        first_rec = 1
                            else:
                                self.updatePos()
                        except ValueError:
                            rospy.logwarn(f"Invalid encoder data: {data_line}")
            except Exception as e:
                rospy.logwarn(f"Error reading serial data: {e}")
            self.rate.sleep()


if __name__ == '__main__':
    robot = None
    try:
        robot = MecanumRobot()
        robot.run()
    except rospy.ROSInterruptException:
        if robot is not None:
            robot.calSpeed(0, 0)
            robot.runRobot()
        rospy.loginfo("ROS node interrupted.")
    finally:
        rospy.loginfo("Exiting program.")
