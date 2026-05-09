#!/usr/bin/env python3
"""
Custom LiDAR processor node - subscribes to /scan topic
Allows flexible processing of LaserScan messages
"""

import rospy
from sensor_msgs.msg import LaserScan
import numpy as np

class LidarProcessor:
    def __init__(self):
        rospy.init_node('lidar_processor', anonymous=False)
        
        # Subscribe to /scan topic
        rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        
        # Optional: Publisher for processed data
        self.processed_pub = rospy.Publisher('/scan_processed', LaserScan, queue_size=10)
        
        # Store latest scan
        self.latest_scan = None
        
        rospy.loginfo("LiDAR Processor initialized. Waiting for /scan messages...")
        rospy.spin()
    
    def scan_callback(self, msg):
        """
        Called whenever a LaserScan message arrives
        Args:
            msg: sensor_msgs/LaserScan
        """
        self.latest_scan = msg
        
        # Extract ranges and angles
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(msg.ranges))
        
        # Example: Filter out invalid readings
        valid_mask = np.isfinite(ranges) & (ranges > msg.range_min) & (ranges < msg.range_max)
        valid_ranges = ranges[valid_mask]
        valid_angles = angles[valid_mask]
        
        # Example: Find obstacles closer than 1.0m
        obstacles = valid_ranges[valid_ranges < 1.0]
        
        if len(obstacles) > 0:
            rospy.loginfo(f"Obstacles detected: {len(obstacles)} points within 1.0m")
            rospy.loginfo(f"Closest obstacle: {np.min(obstacles):.3f}m")
        
        # Optional: republish cleaned data
        # processed_msg = self.process_scan(msg)
        # self.processed_pub.publish(processed_msg)
    
    def process_scan(self, msg):
        """
        Apply custom processing to scan message
        Returns modified LaserScan message
        """
        # Example: filter noisy ranges
        processed_ranges = list(msg.ranges)
        for i in range(len(processed_ranges)):
            if not np.isfinite(processed_ranges[i]):
                processed_ranges[i] = msg.range_max  # Replace NaN with max range
        
        # Create new message
        processed_msg = LaserScan()
        processed_msg.header = msg.header
        processed_msg.angle_min = msg.angle_min
        processed_msg.angle_max = msg.angle_max
        processed_msg.angle_increment = msg.angle_increment
        processed_msg.time_increment = msg.time_increment
        processed_msg.range_min = msg.range_min
        processed_msg.range_max = msg.range_max
        processed_msg.ranges = processed_ranges
        processed_msg.intensities = msg.intensities
        
        return processed_msg

if __name__ == '__main__':
    try:
        processor = LidarProcessor()
    except rospy.ROSInterruptException:
        pass