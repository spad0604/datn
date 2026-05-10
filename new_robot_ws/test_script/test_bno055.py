#!/usr/bin/env python3
"""
Standalone reader for the Bosch BNO055 9-DoF IMU over I2C.

Prints Euler angles, quaternion, linear acceleration, angular velocity and
calibration status in a loop. Designed to run on a Raspberry Pi (or any
Linux board exposing /dev/i2c-*). No ROS dependency.

Dependencies:
    pip install smbus2

Wiring (BNO055 -> Raspberry Pi):
    VIN -> 3V3
    GND -> GND
    SDA -> SDA (GPIO2)
    SCL -> SCL (GPIO3)
    ADR -> VCC (address 0x29, matches the robot's existing IMU wiring)
           GND gives 0x28 if you rewire it.

Usage:
    python3 test_bno055.py
    python3 test_bno055.py --bus 1 --address 0x29 --rate 20
"""

import argparse
import signal
import sys
import time

try:
    from smbus2 import SMBus
except ImportError:
    sys.stderr.write(
        "Missing dependency 'smbus2'. Install it with:\n"
        "    pip install smbus2\n"
    )
    sys.exit(1)


# --- BNO055 register map (from datasheet) ---
REG_CHIP_ID        = 0x00
REG_PAGE_ID        = 0x07
REG_ACC_DATA       = 0x08  # 6 bytes: X/Y/Z m/s^2
REG_MAG_DATA       = 0x0E  # 6 bytes
REG_GYR_DATA       = 0x14  # 6 bytes
REG_EULER          = 0x1A  # 6 bytes: heading/roll/pitch (1/16 deg)
REG_QUAT           = 0x20  # 8 bytes: w/x/y/z (1/(2^14))
REG_LIN_ACC        = 0x28  # 6 bytes: m/s^2 (gravity removed)
REG_GRAVITY        = 0x2E  # 6 bytes
REG_TEMP           = 0x34
REG_CALIB_STAT     = 0x35
REG_OPR_MODE       = 0x3D
REG_PWR_MODE       = 0x3E
REG_SYS_TRIGGER    = 0x3F
REG_UNIT_SEL       = 0x3B

CHIP_ID            = 0xA0

OPR_CONFIG         = 0x00
OPR_NDOF           = 0x0C  # 9-DoF fusion with fast magnetometer calibration

PWR_NORMAL         = 0x00


class BNO055:
    def __init__(self, bus_num=1, address=0x28):
        self.bus = SMBus(bus_num)
        self.addr = address

    def _read(self, reg, length):
        return self.bus.read_i2c_block_data(self.addr, reg, length)

    def _write(self, reg, value):
        self.bus.write_byte_data(self.addr, reg, value)

    @staticmethod
    def _s16(lsb, msb):
        v = (msb << 8) | lsb
        return v - 0x10000 if v & 0x8000 else v

    def begin(self):
        chip = self._read(REG_CHIP_ID, 1)[0]
        if chip != CHIP_ID:
            raise RuntimeError(
                f"Wrong chip id: 0x{chip:02X} (expected 0x{CHIP_ID:02X}). "
                "Check wiring / I2C address."
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

        # Units: m/s^2, dps, deg, Celsius, Android orientation
        self._write(REG_UNIT_SEL, 0x00)

        self._write(REG_OPR_MODE, OPR_NDOF)
        time.sleep(0.025)

    def read_euler(self):
        """(heading, roll, pitch) in degrees."""
        d = self._read(REG_EULER, 6)
        h = self._s16(d[0], d[1]) / 16.0
        r = self._s16(d[2], d[3]) / 16.0
        p = self._s16(d[4], d[5]) / 16.0
        return h, r, p

    def read_quaternion(self):
        """(w, x, y, z) unit quaternion."""
        d = self._read(REG_QUAT, 8)
        scale = 1.0 / (1 << 14)
        w = self._s16(d[0], d[1]) * scale
        x = self._s16(d[2], d[3]) * scale
        y = self._s16(d[4], d[5]) * scale
        z = self._s16(d[6], d[7]) * scale
        return w, x, y, z

    def read_linear_accel(self):
        """(x, y, z) in m/s^2, gravity removed."""
        d = self._read(REG_LIN_ACC, 6)
        return tuple(self._s16(d[i], d[i + 1]) / 100.0 for i in (0, 2, 4))

    def read_gyro(self):
        """(x, y, z) in deg/s."""
        d = self._read(REG_GYR_DATA, 6)
        return tuple(self._s16(d[i], d[i + 1]) / 16.0 for i in (0, 2, 4))

    def read_accel(self):
        """(x, y, z) raw accel in m/s^2."""
        d = self._read(REG_ACC_DATA, 6)
        return tuple(self._s16(d[i], d[i + 1]) / 100.0 for i in (0, 2, 4))

    def read_temp(self):
        t = self._read(REG_TEMP, 1)[0]
        return t - 256 if t & 0x80 else t

    def read_calibration(self):
        """(sys, gyro, accel, mag) each 0-3 (3 = fully calibrated)."""
        v = self._read(REG_CALIB_STAT, 1)[0]
        return (v >> 6) & 0x03, (v >> 4) & 0x03, (v >> 2) & 0x03, v & 0x03

    def close(self):
        try:
            self.bus.close()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser(description="BNO055 standalone test reader.")
    ap.add_argument("--bus", type=int, default=1, help="I2C bus number (default: 1)")
    ap.add_argument("--address", type=lambda s: int(s, 0), default=0x29,
                    help="I2C address 0x28 or 0x29 (default: 0x29, robot wiring)")
    ap.add_argument("--rate", type=float, default=10.0, help="Polling rate in Hz")
    args = ap.parse_args()

    imu = BNO055(bus_num=args.bus, address=args.address)
    print(f"Opening BNO055 on bus {args.bus}, address 0x{args.address:02X}...")
    imu.begin()
    print("BNO055 ready. Press Ctrl+C to stop.\n")

    running = {"flag": True}

    def stop(*_):
        running["flag"] = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    period = 1.0 / max(args.rate, 0.1)
    try:
        while running["flag"]:
            t0 = time.time()
            try:
                heading, roll, pitch = imu.read_euler()
                qw, qx, qy, qz = imu.read_quaternion()
                lax, lay, laz = imu.read_linear_accel()
                gx, gy, gz = imu.read_gyro()
                temp_c = imu.read_temp()
                cs, cg, ca, cm = imu.read_calibration()

                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"Euler(H/R/P)={heading:7.2f}/{roll:7.2f}/{pitch:7.2f} deg | "
                    f"Quat=({qw:+.3f},{qx:+.3f},{qy:+.3f},{qz:+.3f}) | "
                    f"LinAcc=({lax:+.2f},{lay:+.2f},{laz:+.2f}) m/s^2 | "
                    f"Gyro=({gx:+.2f},{gy:+.2f},{gz:+.2f}) dps | "
                    f"T={temp_c}C | Cal S/G/A/M={cs}/{cg}/{ca}/{cm}"
                )
            except OSError as e:
                print(f"I2C read error: {e}")

            elapsed = time.time() - t0
            sleep_for = period - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
    finally:
        imu.close()
        print("\nStopped.")


if __name__ == "__main__":
    main()
