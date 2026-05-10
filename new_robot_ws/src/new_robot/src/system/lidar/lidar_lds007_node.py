#!/usr/bin/env python3
"""
ROS node wrapper for LDS-007 LiDAR reader
Subscribes to serial port and publishes /scan topic
"""

import rospy
from sensor_msgs.msg import LaserScan
import math
import numpy as np
import sys
import os

# Add lidar folder to path so we can import the sibling uart reader whether
# the node is launched from the installed location or from the source tree.
lidar_dir = os.path.dirname(os.path.abspath(__file__))
if lidar_dir not in sys.path:
    sys.path.insert(0, lidar_dir)

try:
    # Preferred: use the catkin-installed Python package (catkin_python_setup
    # registers `system.lidar` on the PYTHONPATH via setup.py).
    from system.lidar.lds007_uart_reader import Lds007Stream
except ImportError:
    try:
        # Fallback when running directly from the source tree.
        from lds007_uart_reader import Lds007Stream
    except ImportError as e:
        rospy.logerr(f"Failed to import lds007_uart_reader: {e}")
        sys.exit(1)


class LidarLDS007Node:
    def __init__(self):
        rospy.init_node('lidar_lds007', anonymous=False)
        
        # Get parameters
        port = rospy.get_param('~port', '/dev/ttyUSB0')
        baud = rospy.get_param('~baud_rate', 115200)
        frame_id = rospy.get_param('~frame_id', 'laser')
        no_checksum = rospy.get_param('~no_checksum', True)
        send_start_command = rospy.get_param('~send_start_command', True)
        start_command = rospy.get_param('~start_command', 'startlds$')

        # If roslaunch auto-coerced the string "true"/"false" into a bool, or
        # someone passed an int, normalize it back to the expected string.
        if not isinstance(start_command, str):
            rospy.logwarn(
                "~start_command was %r (%s); expected string. Using default 'startlds$'.",
                start_command, type(start_command).__name__,
            )
            start_command = 'startlds$'
        
        rospy.loginfo(f"LDS-007 LiDAR node starting...")
        rospy.loginfo(f"  Port: {port}")
        rospy.loginfo(f"  Baud rate: {baud}")
        rospy.loginfo(f"  Frame ID: {frame_id}")
        rospy.loginfo(f"  Checksum validation: {not no_checksum}")
        rospy.loginfo(f"  Send start command: {send_start_command}")
        
        # Create LDS007 stream reader
        try:
            start_command_bytes = start_command.encode('ascii') if send_start_command else None
            self.stream = Lds007Stream(
                port=port,
                baud=baud,
                start_command=start_command_bytes,
                validate_checksum=not no_checksum
            )
        except Exception as e:
            rospy.logerr(f"Failed to initialize LDS007Stream: {e}")
            raise
        
        self.pub = rospy.Publisher('/scan', LaserScan, queue_size=10)
        self.frame_id = frame_id
        self.last_rpm = 0.0
        
        rospy.loginfo("LDS-007 node initialized. Starting to read packets...")
        self.run()
    
    def run(self):
        """Main loop: read packets and publish as LaserScan"""
        scan_buffer = [float('inf')] * 360
        intensity_buffer = [0] * 360
        packets_received = 0
        last_packet_ts = rospy.Time.now().to_sec()
        retries = 0

        try:
            for packet in self.stream.packets():
                now = rospy.Time.now().to_sec()
                if packet is None:
                    # Watchdog: re-send start command if no packets for >3s.
                    if now - last_packet_ts > 3.0:
                        rospy.logwarn(
                            "No LDS-007 packets for %.1fs (retry #%d). "
                            "Re-sending start command.",
                            now - last_packet_ts, retries + 1,
                        )
                        self.stream.send_start_command()
                        retries += 1
                        last_packet_ts = now  # reset so we wait another 3s
                    continue

                packets_received += 1
                last_packet_ts = now
                retries = 0
                self.last_rpm = packet.rpm

                for point in packet.points:
                    angle = point.angle_deg
                    distance_m = point.distance_mm / 1000.0
                    if point.invalid or point.warning:
                        distance_m = float('inf')
                    if distance_m < 0.05:
                        distance_m = float('inf')
                    if distance_m > 6.0:
                        distance_m = float('inf')
                    scan_buffer[angle] = distance_m
                    intensity_buffer[angle] = point.intensity

                if packets_received % 90 == 0:
                    self.publish_scan(scan_buffer, intensity_buffer)
                    scan_buffer = [float('inf')] * 360
                    intensity_buffer = [0] * 360
        
        except KeyboardInterrupt:
            rospy.loginfo("Keyboard interrupt received")
        except Exception as e:
            rospy.logerr(f"Error in main loop: {e}")
        finally:
            rospy.loginfo("Closing LDS007 stream...")
            self.stream.close()
    
    def publish_scan(self, ranges, intensities):
        """Create and publish a LaserScan message"""
        scan_msg = LaserScan()
        scan_msg.header.frame_id = self.frame_id
        scan_msg.header.stamp = rospy.Time.now()
        
        scan_msg.angle_min = 0.0
        scan_msg.angle_max = 2.0 * math.pi
        scan_msg.angle_increment = 2.0 * math.pi / 360.0
        scan_msg.time_increment = 0.0
        
        scan_msg.range_min = 0.05
        scan_msg.range_max = 6.0
        
        scan_msg.ranges = ranges
        scan_msg.intensities = intensities
        
        self.pub.publish(scan_msg)
        
        # Log stats
        valid_points = sum(1 for r in ranges if math.isfinite(r))
        rospy.loginfo(f"Published scan: {valid_points}/360 valid points, RPM: {self.last_rpm:.1f}")


if __name__ == '__main__':
    try:
        node = LidarLDS007Node()
    except Exception as e:
        rospy.logerr(f"Failed to start LiDAR node: {e}")
        sys.exit(1)
