#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ROS node: Bosch BNO055 9-DoF IMU publisher.

Reads the BNO055 over I2C (raw register protocol via smbus2, so no
adafruit_bno055 / CircuitPython dependency is needed) and publishes
`sensor_msgs/Imu` on `/imu/data`.

Parameters (private):
    ~bus          I2C bus number (default: 1)
    ~address      I2C address 0x28 or 0x29 (default: 0x29, robot wiring)
    ~frame_id     Frame id of published Imu message (default: imu_link)
    ~rate_hz      Publish rate in Hz (default: 100.0)

Topics:
    publish  /imu/data  sensor_msgs/Imu
"""

import math
import threading
import time

import rospy
from sensor_msgs.msg import Imu

try:
    from smbus2 import SMBus
except ImportError as exc:
    raise SystemExit(
        "imu_publisher requires 'smbus2'. Install with: pip install smbus2"
    ) from exc


# --- BNO055 register map ---
REG_CHIP_ID     = 0x00
REG_PAGE_ID     = 0x07
REG_ACC_DATA    = 0x08
REG_GYR_DATA    = 0x14
REG_QUAT        = 0x20
REG_LIN_ACC     = 0x28
REG_TEMP        = 0x34
REG_CALIB_STAT  = 0x35
REG_OPR_MODE    = 0x3D
REG_PWR_MODE    = 0x3E
REG_SYS_TRIGGER = 0x3F
REG_UNIT_SEL    = 0x3B

CHIP_ID    = 0xA0
OPR_CONFIG = 0x00
OPR_NDOF   = 0x0C
PWR_NORMAL = 0x00


def _s16(lsb, msb):
    v = (msb << 8) | lsb
    return v - 0x10000 if v & 0x8000 else v


class BNO055:
    def __init__(self, bus_num, address):
        self.addr = address
        self.bus = SMBus(bus_num)
        self._lock = threading.Lock()

    def _read(self, reg, length):
        with self._lock:
            return self.bus.read_i2c_block_data(self.addr, reg, length)

    def _write(self, reg, value):
        with self._lock:
            self.bus.write_byte_data(self.addr, reg, value)

    def begin(self):
        chip = self._read(REG_CHIP_ID, 1)[0]
        if chip != CHIP_ID:
            raise RuntimeError(
                "Wrong chip id 0x%02X (expected 0x%02X). Check wiring / address."
                % (chip, CHIP_ID)
            )
        self._write(REG_PAGE_ID, 0x00)
        self._write(REG_OPR_MODE, OPR_CONFIG)
        time.sleep(0.025)
        self._write(REG_SYS_TRIGGER, 0x20)  # reset
        time.sleep(0.7)
        for _ in range(20):
            try:
                if self._read(REG_CHIP_ID, 1)[0] == CHIP_ID:
                    break
            except OSError:
                pass
            time.sleep(0.05)
        self._write(REG_PWR_MODE, PWR_NORMAL)
        time.sleep(0.02)
        self._write(REG_SYS_TRIGGER, 0x00)
        time.sleep(0.02)
        self._write(REG_UNIT_SEL, 0x00)  # m/s^2, dps, deg
        self._write(REG_OPR_MODE, OPR_NDOF)
        time.sleep(0.025)

    def read_quaternion(self):
        d = self._read(REG_QUAT, 8)
        scale = 1.0 / (1 << 14)
        return (
            _s16(d[0], d[1]) * scale,
            _s16(d[2], d[3]) * scale,
            _s16(d[4], d[5]) * scale,
            _s16(d[6], d[7]) * scale,
        )

    def read_linear_accel(self):
        d = self._read(REG_LIN_ACC, 6)
        return tuple(_s16(d[i], d[i + 1]) / 100.0 for i in (0, 2, 4))

    def read_gyro_dps(self):
        d = self._read(REG_GYR_DATA, 6)
        return tuple(_s16(d[i], d[i + 1]) / 16.0 for i in (0, 2, 4))

    def read_calibration(self):
        v = self._read(REG_CALIB_STAT, 1)[0]
        return (v >> 6) & 0x03, (v >> 4) & 0x03, (v >> 2) & 0x03, v & 0x03

    def close(self):
        try:
            self.bus.close()
        except Exception:
            pass


class ImuPublisher:
    def __init__(self):
        rospy.init_node("imu_publisher", anonymous=False)

        self.bus_num = int(rospy.get_param("~bus", 1))
        self.address = int(rospy.get_param("~address", 0x29))
        self.frame_id = rospy.get_param("~frame_id", "imu_link")
        self.rate_hz = float(rospy.get_param("~rate_hz", 100.0))

        # Covariances copied from the legacy bno055 node in robot_ws; adjust
        # if you recalibrate the sensor.
        self.orientation_cov = [
            0.19320297061877081, 0.0, 0.0,
            0.0, 0.01985739557701275, 0.0,
            0.0, 0.0, 6.70298336970668e-03,
        ]
        self.angular_velocity_cov = [
            1.4056574841526518e-02, 0.0, 0.0,
            0.0, 2.504884899521743e-02, 0.0,
            0.0, 0.0, 2.407325369826665e-03,
        ]
        self.linear_acceleration_cov = [
            0.05417740681601826, 0.0, 0.0,
            0.0, 0.000143956145868615, 0.0,
            0.0, 0.0, 215.17343152207158,
        ]

        self.pub = rospy.Publisher("/imu/data", Imu, queue_size=50)
        self.last_msg = Imu()

        self.sensor = None
        self._connect()
        rospy.on_shutdown(self._cleanup)
        rospy.loginfo(
            "imu_publisher: bus=%d addr=0x%02X rate=%.1fHz frame=%s",
            self.bus_num, self.address, self.rate_hz, self.frame_id,
        )

    def _connect(self):
        try:
            sensor = BNO055(self.bus_num, self.address)
            sensor.begin()
            self.sensor = sensor
            rospy.loginfo("BNO055 initialized at 0x%02X", self.address)
            return True
        except Exception as exc:
            rospy.logwarn_throttle(5.0, "Cannot init BNO055: %s", exc)
            self.sensor = None
            return False

    def _read_imu(self):
        if self.sensor is None:
            return None
        msg = Imu()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.frame_id
        try:
            qw, qx, qy, qz = self.sensor.read_quaternion()
            norm = math.sqrt(qw * qw + qx * qx + qy * qy + qz * qz)
            if 0.9 < norm < 1.1:
                inv = 1.0 / norm
                msg.orientation.w = qw * inv
                msg.orientation.x = qx * inv
                msg.orientation.y = qy * inv
                msg.orientation.z = qz * inv
            else:
                msg.orientation = self.last_msg.orientation

            gx, gy, gz = self.sensor.read_gyro_dps()
            msg.angular_velocity.x = math.radians(gx)
            msg.angular_velocity.y = math.radians(gy)
            msg.angular_velocity.z = math.radians(gz)

            lax, lay, laz = self.sensor.read_linear_accel()
            msg.linear_acceleration.x = lax
            msg.linear_acceleration.y = lay
            msg.linear_acceleration.z = laz
        except OSError as exc:
            rospy.logwarn_throttle(2.0, "BNO055 read failed: %s", exc)
            try:
                self.sensor.close()
            except Exception:
                pass
            self.sensor = None
            return None

        msg.orientation_covariance = self.orientation_cov
        msg.angular_velocity_covariance = self.angular_velocity_cov
        msg.linear_acceleration_covariance = self.linear_acceleration_cov
        self.last_msg = msg
        return msg

    def run(self):
        rate = rospy.Rate(max(self.rate_hz, 1.0))
        while not rospy.is_shutdown():
            if self.sensor is None:
                self._connect()
                rate.sleep()
                continue
            msg = self._read_imu()
            if msg is not None:
                self.pub.publish(msg)
            rate.sleep()

    def _cleanup(self):
        if self.sensor is not None:
            self.sensor.close()


if __name__ == "__main__":
    try:
        ImuPublisher().run()
    except rospy.ROSInterruptException:
        pass
