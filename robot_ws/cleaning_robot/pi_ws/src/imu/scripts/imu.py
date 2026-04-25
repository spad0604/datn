#!/usr/bin/env python3
import rospy
import board
import busio
import adafruit_bno055
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion
from geometry_msgs.msg import TransformStamped
import tf2_ros
import math
import time

class BNO055Node:
    def __init__(self):
        # --- ROS Node ---
        rospy.init_node("bno055_imu_node", anonymous=True)
        self.pub = rospy.Publisher("/imu/data", Imu, queue_size=10)
        self.rate_hz = rospy.get_param("~rate_hz", 100)
        self.rate = rospy.Rate(self.rate_hz)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()
        self.i2c_address = rospy.get_param("~i2c_address", 0x29)
        self.reconnect_interval = rospy.get_param("~reconnect_interval", 3.0)
        self.last_connect_attempt = 0.0
        self.bno = None
        self.last_imu_msg=Imu()
        # --- Covariance matrices ---
        self.orientation_cov = [0.19320297061877081, 0, 0, 0, 0.01985739557701275, 0, 0, 0, 6.70298336970668e-03]
        self.angular_velocity_cov = [1.4056574841526518e-02, 0, 0, 0, 2.504884899521743e-02, 0, 0, 0, 2.407325369826665e-03]
        self.linear_acceleration_cov = [0.05417740681601826, 0, 0, 0, 0.000143956145868615, 0, 0, 0, 215.17343152207158]

        self._connect_sensor(initial=True)
        rospy.loginfo("BNO055 IMU node started, publishing to /imu/data")

    def _connect_sensor(self, initial=False):
        now = time.time()
        if not initial and (now - self.last_connect_attempt) < float(self.reconnect_interval):
            return False

        self.last_connect_attempt = now
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.bno = adafruit_bno055.BNO055_I2C(i2c, address=int(self.i2c_address))
            time.sleep(0.1)
            if not self.wait_for_calibration(timeout=10.0):
                rospy.logwarn("BNO055 calibration not ready, will continue and retry reads.")
            rospy.loginfo("Connected to BNO055 at I2C address 0x%02X", int(self.i2c_address))
            return True
        except Exception as exc:
            self.bno = None
            rospy.logerr("Cannot connect BNO055 (0x%02X): %s", int(self.i2c_address), exc)
            return False

    def normalize_quat(self, q):
        w, x, y, z = q
        norm = math.sqrt(w*w + x*x + y*y + z*z)
        if norm < 1e-6:
            return [1.0, 0.0, 0.0, 0.0]
        inv = 1.0 / norm
        return [w*inv, x*inv, y*inv, z*inv]

    def wait_for_calibration(self, timeout=10.0):
        if self.bno is None:
            return False
   
        deadline = time.time() + timeout
        while time.time() < deadline and not rospy.is_shutdown():
            try:
                sys, gyro, accel, mag = self.bno.calibration_status
                rospy.loginfo(f"Calibration → System:{sys}  Gyro:{gyro}  Accel:{accel}  Mag:{mag}")

               
                if sys >= 0 and gyro >= 3 and accel >= 0 and mag >= 0:
                    rospy.loginfo("BNO055 calibration complete!")
                    return True
            except Exception as e:
                rospy.logwarn(f"Error reading calibration status: {e}")
                self.bno = None
                return False

            time.sleep(0.5)

        return False

    def read_imu(self):
        if self.bno is None:
            return None

        imu_msg = Imu()
        imu_msg.header.stamp = rospy.Time.now()
        imu_msg.header.frame_id = "imu_link"
        orient_var=self.orientation_cov
        accel_var=self.linear_acceleration_cov
        gyro_var=self.angular_velocity_cov
        try:
            # --- Linear Acceleration ---
            accel = self.bno.acceleration
            if accel and all(v is not None for v in accel):
                imu_msg.linear_acceleration.x = accel[0]
                imu_msg.linear_acceleration.y = accel[1]
                imu_msg.linear_acceleration.z = accel[2]
            else:
                accel_var=[1e6,0,0, 0,1e6,0, 0,0,1e6]

            # --- Angular Velocity (deg/s -> rad/s) ---
            gyro = self.bno.gyro
            if gyro is not None:
                imu_msg.angular_velocity.x = math.radians(gyro[0])
                imu_msg.angular_velocity.y = math.radians(gyro[1])
                imu_msg.angular_velocity.z = math.radians(gyro[2])
            else:
                imu_msg.angular_velocity=self.last_imu_msg.angular_velocity

            # --- Orientation quaternion ---
            quat = self.bno.quaternion  # [w, x, y, z]

            if quat and all(v is not None for v in quat):
                w, x, y, z = quat
                norm = math.sqrt(w*w + x*x + y*y + z*z)
                if 0.9 < norm < 1.1:  # cho phép sai số nhỏ
                    inv_norm = 1.0 / norm
                    w *= inv_norm
                    x *= inv_norm
                    y *= inv_norm
                    z *= inv_norm

                    # Quaternion offset: quay +90° quanh trục Z
                    offset_angle = math.radians(0)
                    offset_w = math.cos(offset_angle / 2)
                    offset_z = math.sin(offset_angle / 2)
                    ow, ox, oy, oz = offset_w, 0.0, 0.0, offset_z

                    # Nhân hai quaternion: offset * original (quay offset trước, rồi quay original)
                    # Công thức: q_result = q_offset * q_original
                    nw = ow * w - ox * x - oy * y - oz * z
                    nx = ow * x + ox * w + oy * z - oz * y
                    ny = ow * y - ox * z + oy * w + oz * x
                    nz = ow * z + ox * y - oy * x + oz * w

                    # Gán vào message
                    q = Quaternion()
                    q.w = nw
                    q.x = nx
                    q.y = ny
                    q.z = nz
                    imu_msg.orientation = q

                    # Nếu bạn muốn chuẩn hóa lại lần nữa (khuyến nghị)
                    norm_final = math.sqrt(nw*nw + nx*nx + ny*ny + nz*nz)
                    if norm_final > 1e-6:
                        inv_final = 1.0 / norm_final
                        imu_msg.orientation.w *= inv_final
                        imu_msg.orientation.x *= inv_final
                        imu_msg.orientation.y *= inv_final
                        imu_msg.orientation.z *= inv_final
                else:
                    imu_msg.orientation=self.last_imu_msg.orientation
            else:
                imu_msg.orientation=self.last_imu_msg.orientation
        except Exception as exc:
            rospy.logwarn_throttle(2.0, f"BNO055 read failed: {exc}. Will reconnect...")
            self.bno = None
            return None
       
        # --- Covariances ---
        imu_msg.orientation_covariance = orient_var
        imu_msg.angular_velocity_covariance = gyro_var
        imu_msg.linear_acceleration_covariance = accel_var
        self.last_imu_msg=imu_msg
 
        return self.last_imu_msg

    def run(self):
        while not rospy.is_shutdown():
            if self.bno is None:
                self._connect_sensor(initial=False)
                self.rate.sleep()
                continue

            imu_msg = self.read_imu()
            if imu_msg is not None:
                self.pub.publish(imu_msg)
               

        # Dữ liệu lỗi → vẫn publish TF identity (không làm EKF bị drift)
      

               
            self.rate.sleep()

# === Main ===
if __name__ == "__main__":
    try:
        node = BNO055Node()
        node.run()
    except rospy.ROSInterruptException:
        pass