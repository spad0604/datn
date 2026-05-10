#!/usr/bin/env python3
import rospy
import serial
import select
from enum import Enum
from std_msgs.msg import String


class State(Enum):
    WAITING = 1
    DOING = 2
    SUCCESS = 3


class ArduinoSerialNode:
    def __init__(self):
        port = rospy.get_param('~port_arduino', '/dev/arduino')
        baudrate_ard = rospy.get_param('~baudrate_ard', 9600)

        self.ser_ard = None
        try:
            self.ser_ard = serial.Serial(port, baudrate_ard, timeout=0)
        except Exception as e:
            rospy.logwarn("Khong mo duoc cong serial Arduino (%s): %s", port, e)
            self.ser_ard = None

        rospy.Subscriber('/Status_robot', String, self.state_callback)
        self.state_publish = rospy.Publisher('/Status_robot', String, queue_size=1)

        self.state = State.WAITING
        self.pending_action = None

        rospy.Subscriber('serial_ard_tx', String, self.send_to_arduino)

        rospy.on_shutdown(self.cleanup)

        rospy.loginfo("ArduinoSerialNode started on port: %s", port)

    def send_to_arduino(self, msg):
        if self.ser_ard is not None and self.ser_ard.is_open:
            rospy.loginfo("[Arduino TX] %s", msg.data)
            self.ser_ard.write((msg.data + '\n').encode('utf-8'))
        else:
            rospy.logwarn_throttle(
                10, "Arduino serial is not available; drop serial_ard_tx: %s", msg.data
            )

    def processDoing(self):
        if self.state == State.DOING and self.pending_action != "sent_doing":
            rospy.loginfo("DOING init")
            rospy.loginfo("Dang cho pin UNLOCK tu node socket truoc khi Arduino tra OK")

    def processSucess(self):
        if self.state == State.SUCCESS and self.pending_action != "sent_success":
            rospy.loginfo("SUCCESS STATE WAIT ARDUINO")
            if self.ser_ard is not None and self.ser_ard.is_open:
                self.ser_ard.write(b'L_ON\n')

    def state_callback(self, msg):
        if self.state == State.WAITING and msg.data == "DOING":
            rospy.loginfo("Get start transfer to DOING")
            self.state = State.DOING

        if self.state == State.DOING and msg.data == "SUCCESS":
            rospy.loginfo("Done navigation process SUCCESS action")
            self.state = State.SUCCESS

    def spin(self):
        rate = rospy.Rate(10)
        i = 0
        inputs = []
        if self.ser_ard is not None:
            inputs.append(self.ser_ard)

        while not rospy.is_shutdown():
            if inputs:
                rlist, _, _ = select.select(inputs, [], [], 0.01)
                for ser in rlist:
                    data = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not data:
                        continue
                    rospy.loginfo("[Arduino RX] %s", data)

                    if self.state == State.SUCCESS and data == "OK":
                        rospy.loginfo("GET arduino sucess transform cmd")
                        self.state = State.WAITING
                        self.pending_action = "sent_success"
                        rospy.loginfo("WAITING TRANSFER")

                    if self.state == State.DOING and data == "OK":
                        rospy.loginfo("GET arduino doing transform cmd")
                        self.pending_action = "sent_doing"
                        self.state_publish.publish("MOVING")
                        rospy.loginfo("WAITING DOING")

            if self.state == State.WAITING:
                self.pending_action = None
            i += 1
            if i >= 50:
                self.processDoing()
                self.processSucess()
                i = 0

            rate.sleep()

    def cleanup(self):
        rospy.loginfo("Dang dong cong serial Arduino...")
        if self.ser_ard is not None and self.ser_ard.is_open:
            self.ser_ard.close()
        rospy.loginfo("Da dong cong serial thanh cong.")


if __name__ == '__main__':
    rospy.init_node('arduino_serial_node')
    node = ArduinoSerialNode()
    node.spin()
