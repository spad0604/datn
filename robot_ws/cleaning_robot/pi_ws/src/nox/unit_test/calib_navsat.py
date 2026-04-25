#!/usr/bin/env python3
import rospy
import tf2_ros
import math
from tf.transformations import euler_from_quaternion
import yaml
import os
import select
import sys
import termios
import tty

# Đường dẫn file YAML (có thể thay đổi)
YAML_FILE = '/home/gps_robot/robot_ws/cleaning_robot/pi_ws/src/nox/cfg/navsat_param.yaml'

def get_key():
    """Đọc phím không blocking để nhấn 's' lưu file."""
    settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
            return key.lower()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return None

def load_yaml(file_path):
    """Đọc file YAML, nếu không tồn tại thì tạo mới với nội dung gốc."""
    default_yaml = """
navsat_transform:
  frequency: 10
  delay: 3.0
  magnetic_declination_radians: 0.0842
  yaw_offset: -1.57080
  zero_altitude: true
  broadcast_utm_transform: true
  broadcast_cartesian_transform: true
  publish_filtered_gps: true
  use_odometry_yaw: false
  wait_for_datum: false
"""
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại. Tạo mới với nội dung mặc định.")
        with open(file_path, 'w') as f:
            f.write(default_yaml.strip())
    
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def save_yaml(file_path, data):
    """Ghi file YAML mới."""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, indent=2)
    print(f"\n✅ Đã cập nhật yaw_offset vào file {file_path}!")
    print("Nội dung file mới:")
    with open(file_path, 'r') as f:
        print(f.read())

def main():
    rospy.init_node('yaw_offset_updater', anonymous=True)
    
    # Tạo buffer và listener cho tf
    tf_buffer = tf2_ros.Buffer()
    tf_listener = tf2_ros.TransformListener(tf_buffer)
    
    rospy.sleep(1.0)  # chờ tf khởi động
    
    # Load file YAML
    try:
        config = load_yaml(YAML_FILE)
    except Exception as e:
        rospy.logerr(f"Lỗi đọc file YAML: {e}")
        return
    
    print("\n=== Tự động cập nhật yaw_offset vào navsat_transform.yaml ===\n")
    print("Hướng dẫn:")
    print("- Xoay robot hướng Bắc (0° GPS).")
    print("- Nhấn 's' để lưu yaw_offset hiện tại vào file YAML.")
    print("- Nhấn Ctrl+C để thoát.\n")
    
    rate = rospy.Rate(2.0)  # 2 Hz
    
    while not rospy.is_shutdown():
        key = get_key()
        if key == 's':
            try:
                # Lấy transform
                trans = tf_buffer.lookup_transform(
                    target_frame="odom",
                    source_frame="base_link",
                    time=rospy.Time(0),
                    timeout=rospy.Duration(1.0)
                )
                
                # Tính yaw_offset
                q = trans.transform.rotation
                quat = [q.x, q.y, q.z, q.w]
                roll, pitch, yaw = euler_from_quaternion(quat)
                yaw_offset_rad = -yaw
                yaw_deg = math.degrees(yaw)
                
                print(f"\nLưu yaw_offset: {yaw_offset_rad:.5f} rad ({yaw_deg:.2f}°)")
                
                # Cập nhật config
                config['navsat_transform']['yaw_offset'] = yaw_offset_rad
                
                # Xác nhận trước khi lưu (có thể bỏ comment nếu muốn auto-save)
                confirm = input("Xác nhận lưu? (y/n): ")
                if confirm.lower() == 'y':
                    save_yaml(YAML_FILE, config)
                else:
                    print("Hủy lưu.")
                
            except Exception as e:
                rospy.logerr(f"Lỗi khi lưu: {e}")
            continue
        
        try:
            # Hiển thị yaw hiện tại
            trans = tf_buffer.lookup_transform(
                target_frame="odom",
                source_frame="base_link",
                time=rospy.Time(0),
                timeout=rospy.Duration(1.0)
            )
            
            q = trans.transform.rotation
            quat = [q.x, q.y, q.z, q.w]
            roll, pitch, yaw = euler_from_quaternion(quat)
            yaw_offset_rad = -yaw
            yaw_deg = math.degrees(yaw)
            
            print(f"Yaw hiện tại: {yaw_deg:.2f}° | yaw_offset gợi ý: {yaw_offset_rad:.5f} rad")
            print("Nhấn 's' để lưu vào file...")
            
        except Exception as e:
            rospy.logwarn_throttle(5.0, f"Không tìm thấy tf: {e}")
        
        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass