#!/usr/bin/env python3
import time
import rospy
import serial
from std_msgs.msg import String
import re

class SimSerialNode:
    def __init__(self):
        # Lấy thông số từ ROS param
        self.port = rospy.get_param('~port_sim', '/dev/ttyUSB4')
        self.baudrate = rospy.get_param('~baudrate_sim', 115200)
        self.phone_number = rospy.get_param('~phone_number', "+84982352665")

        self.ser_sim = None
        self.current_charset = "GSM"  # Mặc định dùng GSM (dễ hơn, 160 ký tự)

        # Mở cổng serial
        try:
            self.ser_sim = serial.Serial(self.port, self.baudrate, timeout=1)
            rospy.loginfo(f"Đã mở cổng SIM: {self.port} @ {self.baudrate} baud")
        except serial.SerialException as e:
            rospy.logerr(f"Không mở được cổng SIM: {e}")
            rospy.signal_shutdown("Serial error")
            return

        # Kiểm tra module sẵn sàng
        if not self.wait_for_module_ready():
            rospy.logerr("SIM7600 not ready")
            rospy.signal_shutdown("SIM7600 not ready")
            return

        # Kiểm tra tín hiệu
        self.check_signal()

        # Publisher trạng thái
        self.status_pub = rospy.Publisher('~status', String, queue_size=1)

        # Subscriber
        rospy.Subscriber('~send_sms', String, self.handle_send_sms)
        rospy.Subscriber('~set_phone_number', String, self.handle_set_phone_number)

        rospy.loginfo(f"SimSerialNode started. Số mặc định: {self.phone_number}")

    def send_command(self, command):
        cmd = command + "\r\n"
        self.ser_sim.write(cmd.encode('utf-8'))
        rospy.logdebug(f"Send: {cmd.strip()}")

    def read_response(self, timeout=5):
        response = ""
        start = time.time()
        while time.time() - start < timeout:
            if self.ser_sim.in_waiting > 0:
                line = self.ser_sim.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    response += line + "\n"
                    rospy.logdebug(f"Recv: {line}")
            time.sleep(0.05)
        return response.strip()

    def send_command_and_check(self, command, timeout=5, wait_for="OK"):
        self.send_command(command)
        response = self.read_response(timeout)
        if wait_for in response:
            return True, response
        return False, response

    def wait_for_module_ready(self, max_attempts=5):
        rospy.loginfo("Đang chờ SIM7600 sẵn sàng...")
        for attempt in range(max_attempts):
            success, _ = self.send_command_and_check("AT", timeout=2)
            if success:
                rospy.loginfo("SIM7600 đã sẵn sàng!")
                return True
            rospy.logwarn(f"Thử lại lần {attempt+1}/{max_attempts}")
            time.sleep(1)
        return False

    def check_signal(self):
        success, response = self.send_command_and_check("AT+CSQ", timeout=3)
        if success:
            match = re.search(r'\+CSQ:\s*(\d+)', response)
            if match:
                csq = int(match.group(1))
                rospy.loginfo(f"Chất lượng tín hiệu: {csq}/31")
                return csq < 99
        rospy.logwarn("Không lấy được chất lượng tín hiệu")
        return False

    def detect_charset(self, message):
        """Phát hiện có cần UCS2 không (có ký tự ngoài GSM-7)"""
        gsm7_chars = set(' @£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !"#%&\'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà')
        for c in message:
            if c not in gsm7_chars:
                return "UCS2"
        return "GSM"

    def to_ucs2_hex(self, text):
        """Chuyển chuỗi sang UCS2 hex (mỗi ký tự 4 hex)"""
        return ''.join(f'{ord(c):04X}' for c in text)

    def send_sms(self, message):
        message = message.strip()
        if not message:
            rospy.logwarn("Tin nhắn rỗng, bỏ qua")
            return False

        # Tự động chọn charset phù hợp
        self.current_charset = self.detect_charset(message)
        rospy.loginfo(f"Sử dụng charset: {self.current_charset}")

        # Kiểm tra độ dài
        if self.current_charset == "UCS2":
            if len(message) > 70:
                rospy.logerr(f"Tin nhắn quá dài cho UCS2 ({len(message)} > 70)")
                return False
        else:
            if len(message) > 160:
                rospy.logerr(f"Tin nhắn quá dài cho GSM ({len(message)} > 160)")
                return False

        # Thiết lập chế độ text
        success, _ = self.send_command_and_check("AT+CMGF=1", timeout=3)
        if not success:
            rospy.logerr("Không đặt được chế độ text mode")
            return False

        # Thiết lập charset
        success, _ = self.send_command_and_check(f'AT+CSCS="{self.current_charset}"', timeout=3)
        if not success:
            rospy.logerr(f"Không đặt được charset {self.current_charset}")
            return False

        # Chuẩn bị số điện thoại
        if self.current_charset == "UCS2":
            phone_ucs2 = self.to_ucs2_hex(self.phone_number)
            cmd = f'AT+CMGS="{phone_ucs2}"'
        else:
            cmd = f'AT+CMGS="{self.phone_number}"'

        # Gửi lệnh CMGS
        success, resp = self.send_command_and_check(cmd, timeout=5, wait_for=">")
        if not success:
            rospy.logerr("Không nhận được dấu nhắc '>'")
            rospy.logerr(f"Phản hồi: {resp}")
            return False

        # Gửi nội dung tin nhắn
        rospy.loginfo(f"Đang gửi nội dung tin nhắn đến {self.phone_number} ({len(message)} ký tự): '{message}'")

        if self.current_charset == "UCS2":
            hex_content = self.to_ucs2_hex(message)
            content_bytes = bytes.fromhex(hex_content)
        else:
            content_bytes = message.encode('ascii')  # GSM-7 dùng ascii

        self.ser_sim.write(content_bytes)
        self.ser_sim.write(b'\r')  # Carriage Return
        time.sleep(0.1)
        self.ser_sim.write(bytes([26]))  # Ctrl+Z (0x1A)
        self.ser_sim.flush()

        # Chờ xác nhận
        start = time.time()
        while time.time() - start < 30:
            if self.ser_sim.in_waiting:
                line = self.ser_sim.readline().decode('utf-8', errors='ignore').strip()
                rospy.logdebug(f"Recv: {line}")
                if "+CMGS:" in line:
                    rospy.loginfo("Đã gửi thành công (có mã CMGS)")
                if "OK" in line:
                    rospy.loginfo("SMS gửi thành công!")
                    self.status_pub.publish("SMS_SENT_OK")
                    return True
                if "ERROR" in line or "+CMS ERROR" in line:
                    rospy.logerr(f"Lỗi khi gửi SMS: {line}")
                    return False
            time.sleep(0.3)

        rospy.logerr("Timeout khi chờ xác nhận gửi SMS")
        return False

    def handle_send_sms(self, msg):
        success = self.send_sms(msg.data)
        if success:
            rospy.loginfo("Gửi SMS thành công")
        else:
            rospy.logerr("Gửi SMS thất bại")

    def handle_set_phone_number(self, msg):
        new_number = msg.data.strip()
        if not new_number.startswith('+'):
            rospy.logwarn("Số phải bắt đầu bằng '+', bỏ qua: %s", new_number)
            return
        self.phone_number = new_number
        rospy.loginfo(f"Đã cập nhật số điện thoại: {self.phone_number}")
        self.status_pub.publish(f"PHONE_UPDATED:{self.phone_number}")

    def spin(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            rate.sleep()

    def cleanup(self):
        rospy.loginfo("Đang đóng cổng SIM...")
        if self.ser_sim and self.ser_sim.is_open:
            self.ser_sim.close()
        rospy.loginfo("Đã đóng cổng SIM.")

if __name__ == '__main__':
    rospy.init_node('sim_serial_node')
    node = SimSerialNode()
    try:
        node.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        node.cleanup()