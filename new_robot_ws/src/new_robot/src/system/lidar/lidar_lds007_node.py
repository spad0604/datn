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

# Add lidar folder to path to import lds007_uart_reader
lidar_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, lidar_dir)

try:
    from new_robot_ws.src.new_robot.src.system.lidar.lds007_uart_reader import Lds007Stream
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
        
        try:
            for packet in self.stream.packets():
                packets_received += 1
                self.last_rpm = packet.rpm
                
                # Store 4 points from this packet
                for point in packet.points:
                    angle = point.angle_deg
                    distance_m = point.distance_mm / 1000.0
                    
                    # Mark invalid/warning points as inf (out of range)
                    if point.invalid or point.warning:
                        distance_m = float('inf')
                    
                    # Clamp to valid range
                    if distance_m < 0.05:
                        distance_m = float('inf')
                    if distance_m > 6.0:
                        distance_m = float('inf')
                    
                    scan_buffer[angle] = distance_m
                    intensity_buffer[angle] = point.intensity
                
                # Publish complete scan after 90 packets (360 points total)
                if packets_received % 90 == 0:
                    self.publish_scan(scan_buffer, intensity_buffer)
                    
                    # Reset buffer for next scan
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
