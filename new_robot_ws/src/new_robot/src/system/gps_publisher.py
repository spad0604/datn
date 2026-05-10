#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GPS publisher node for SIM7600 NMEA stream.

Reads raw NMEA sentences from a USB serial port (default /dev/ttyUSB3 — the
dedicated NMEA port of the SIM7600X HAT) and publishes
`sensor_msgs/NavSatFix` on `/fix`.

This node does NOT send AT commands. The NMEA port streams data
automatically as soon as the module powers up, so no setup is required.

Parameters (private):
    ~port       Serial port (default: /dev/ttyUSB3)
    ~baud       Baud rate (default: 115200)
    ~frame_id   Frame id for published messages (default: gps)
    ~rate_hz    Publish rate (default: 1.0)
"""

import threading

import rospy
import serial
from sensor_msgs.msg import NavSatFix, NavSatStatus


def _nmea_checksum_ok(sentence: str) -> bool:
    if not sentence.startswith("$") or "*" not in sentence:
        return False
    body, _, chk = sentence[1:].partition("*")
    try:
        want = int(chk[:2], 16)
    except ValueError:
        return False
    got = 0
    for ch in body:
        got ^= ord(ch)
    return got == want


def _to_decimal(coord: str, hemi: str):
    """Convert NMEA ddmm.mmmm / dddmm.mmmm to decimal degrees."""
    if not coord or not hemi:
        return None
    try:
        dot = coord.index(".")
    except ValueError:
        return None
    deg_len = dot - 2
    if deg_len <= 0:
        return None
    try:
        deg = int(coord[:deg_len])
        minutes = float(coord[deg_len:])
    except ValueError:
        return None
    val = deg + minutes / 60.0
    if hemi in ("S", "W"):
        val = -val
    return val


def parse_gga(sentence: str):
    """Parse $xxGGA. Returns dict with lat/lon/alt/quality/sats or None."""
    if not _nmea_checksum_ok(sentence):
        return None
    body = sentence[1:].split("*", 1)[0]
    f = body.split(",")
    if len(f) < 10:
        return None
    quality = f[6]
    if quality in ("", "0"):
        return {"quality": 0, "lat": None, "lon": None, "alt": None, "sats": None}
    lat = _to_decimal(f[2], f[3])
    lon = _to_decimal(f[4], f[5])
    try:
        alt = float(f[9]) if f[9] else None
    except ValueError:
        alt = None
    try:
        sats = int(f[7]) if f[7] else None
    except ValueError:
        sats = None
    try:
        q = int(quality)
    except ValueError:
        q = 0
    return {"quality": q, "lat": lat, "lon": lon, "alt": alt, "sats": sats}


class GpsPublisher:
    def __init__(self):
        rospy.init_node("gps_publisher", anonymous=False)

        self.port = rospy.get_param("~port", "/dev/ttyUSB3")
        self.baud = int(rospy.get_param("~baud", 115200))
        self.frame_id = rospy.get_param("~frame_id", "gps")
        self.rate_hz = float(rospy.get_param("~rate_hz", 1.0))

        self.pub = rospy.Publisher("/fix", NavSatFix, queue_size=10)

        self.latest = None  # latest parsed fix dict
        self._lock = threading.Lock()
        self._ser = None

        rospy.on_shutdown(self._cleanup)
        rospy.loginfo(
            "gps_publisher: reading NMEA from %s @ %d, publishing /fix at %.1f Hz",
            self.port, self.baud, self.rate_hz,
        )

    def _open_serial(self):
        """Open the NMEA port, tolerating the SIM7600 USB-CDC DTR quirk."""
        try:
            return serial.Serial(
                self.port, self.baud, timeout=1.0,
                dsrdtr=True, rtscts=False, xonxoff=False,
            )
        except (BrokenPipeError, OSError) as first:
            ser = serial.Serial()
            ser.port = self.port
            ser.baudrate = self.baud
            ser.timeout = 1.0
            ser.dsrdtr = True
            ser.rtscts = False
            ser.xonxoff = False
            try:
                ser.dtr = None
                ser.rts = None
            except Exception:
                pass
            try:
                ser.open()
                return ser
            except (BrokenPipeError, OSError):
                if ser.is_open:
                    return ser
                raise first

    def _reader_loop(self):
        """Background thread: read serial, parse GGA, update self.latest."""
        while not rospy.is_shutdown():
            if self._ser is None:
                try:
                    self._ser = self._open_serial()
                except Exception as exc:
                    rospy.logwarn_throttle(5.0, "Cannot open %s: %s", self.port, exc)
                    rospy.sleep(2.0)
                    continue
            try:
                raw = self._ser.readline()
            except (serial.SerialException, OSError) as exc:
                rospy.logwarn_throttle(5.0, "Serial read error: %s. Reopening.", exc)
                try:
                    self._ser.close()
                except Exception:
                    pass
                self._ser = None
                continue
            if not raw:
                continue
            text = raw.decode("utf-8", errors="ignore").strip()
            if not text.startswith("$") or "GGA" not in text[:6]:
                continue
            fix = parse_gga(text)
            if fix is None:
                continue
            with self._lock:
                self.latest = fix

    def _publish_loop(self):
        rate = rospy.Rate(max(self.rate_hz, 0.1))
        while not rospy.is_shutdown():
            with self._lock:
                fix = self.latest

            msg = NavSatFix()
            msg.header.stamp = rospy.Time.now()
            msg.header.frame_id = self.frame_id

            if fix is None or fix["quality"] == 0 or fix["lat"] is None:
                msg.status.status = NavSatStatus.STATUS_NO_FIX
                msg.latitude = float("nan")
                msg.longitude = float("nan")
                msg.altitude = float("nan")
                rospy.logwarn_throttle(
                    5.0, "No GPS fix yet (waiting for satellites on %s)", self.port,
                )
            else:
                msg.status.status = NavSatStatus.STATUS_FIX
                msg.status.service = NavSatStatus.SERVICE_GPS
                msg.latitude = fix["lat"]
                msg.longitude = fix["lon"]
                msg.altitude = fix["alt"] if fix["alt"] is not None else 0.0
                rospy.loginfo_throttle(
                    5.0,
                    "Fix: lat=%.7f lon=%.7f alt=%.1fm sats=%s",
                    fix["lat"], fix["lon"], msg.altitude, fix["sats"],
                )

            # Unknown covariance from raw NMEA.
            msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_UNKNOWN

            self.pub.publish(msg)
            rate.sleep()

    def run(self):
        reader = threading.Thread(target=self._reader_loop, daemon=True)
        reader.start()
        self._publish_loop()

    def _cleanup(self):
        if self._ser is not None:
            try:
                self._ser.close()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        GpsPublisher().run()
    except rospy.ROSInterruptException:
        pass
