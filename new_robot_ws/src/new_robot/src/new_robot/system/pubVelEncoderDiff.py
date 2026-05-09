#!/usr/bin/env python3

import rospy
from nav_msgs.msg import Odometry
import tf
from enum import Enum
from geometry_msgs.msg import TransformStamped
from geometry_msgs.msg import Pose2D
from nav_msgs.msg import Odometry
from tf.transformations import quaternion_from_euler
import numpy as np
import math
import sys
import os
import time
import rospkg
from std_msgs.msg import Bool,Int32,Float32
from geometry_msgs.msg import Twist
import serial

class MecanumRobot:
    def __init__(self):
        rospy.init_node('mecanum_robot')
        print("INIT")
        self.NMOTORS = 4  
        self.MotorError=False
        self.total_length = 52.89
          # Adjust this value based on your robot design
        #length=41.5/2=20.75
        #width =34.3/2=17.15
        self.onOffMor=False
        self.M_LEFT=0
        self.M_RIGHT=1
        self.M_RIGHT_DOWN=3
        self.acc_time=10
        self.dec_time=10
        self.M_RIGHT_UP=2
        self.M_LEFT_DOWN=1
        self.M_LEFT_UP=0
        self.coeff_speed=1.0
        self.moving=False
        # self.x_offset = 1.0  # Scaling factor for x
        # self.y_offset = 1.0  # Scaling factor for y
        # self.theta_offset = 1.0  # Scaling factor for theta
        self.use_imu=rospy.get_param('~use_imu',False) #cm
        print(self.use_imu)
        
        # rospy.Subscriber('/toggle_topic',Int32, self.CylinderCB)
        self.tf_broadcaster = tf.TransformBroadcaster()
        self.last_pose = None
        self.last_time = rospy.Time.now()
        self.odom_pub = rospy.Publisher('/odom', Odometry, queue_size=5)
        # print("not use imu")
        self.WHEEL_DIAMETER=rospy.get_param('~wheel_diameter',9.5) #cm
        self.ENCODER_TOTAL=rospy.get_param('~encoder_total',1798)
        self.encoder_total=np.zeros(4)
        self.test_mode=rospy.get_param('~test_mode',0) # 0 - speed 1 - position 2 - normal
        self.start_velocity_test=rospy.get_param('~start_run', 1.0)
        self.x_offset= rospy.get_param('~x_offset', 1.0)
        self.y_offset = rospy.get_param('~y_offset', 1.0)
        self.theta_offset = rospy.get_param('~theta_offset', 1.0)
        self.distance_move= rospy.get_param('~distance_move', 1.0)
        self.axis_move = rospy.get_param('~axis_move', 1.0)
        self.velocity_move = rospy.get_param('~velocity_move', 1.0)
        self.robot_pose = np.zeros(3)  # [x, y, theta]
        self.speed_desired = np.zeros(self.NMOTORS)  # Desired speeds for each motor cm/s
        # "/final_cmd_vel_mux/output"
        self.speed_filter_x=0.0
        self.speed_filter_y=0.0
        self.speed_filter_z=0.0
        self.last_speed_x=0.0
        self.last_speed_y=0.0
        self.last_speed_z=0.0
        self.a_coeff=0.52188555
        self.b_coeff=0.23905722
        self.last_encod=np.zeros(4)
        self.xylanh=1
        self.dtheta=0.0
        self.cmd_msg = Twist()  # Initialize a Twist message
        # self.odom_pub = rospy.Publisher('odom', Odometry, queue_size=10)
        self.MotorErrorPub=rospy.Publisher('MOTOR_ERROR',Bool,queue_size=1)
        self.tf_broadcaster = tf.TransformBroadcaster()
        self.delta_encod_total1=np.zeros(4)
        self.serial_port_name = rospy.get_param('~port', '/dev/esp32')
        self.baud = rospy.get_param('~baud', 57600)
        # self.pub_encoder=rospy.publish
        self.serial_port = serial.Serial(self.serial_port_name,  self.baud)
        # modbus_connection = ZLAC8015D.ModbusConnection(port="/dev/ttyUSB0")
        # rospy.sleep(1.5)
        self.desired = rospy.Publisher('/speed_desired', Float32, queue_size=1)
        self.feedback = rospy.Publisher('/speed_feedback', Float32, queue_size=1)
        self.last_time_encod=rospy.Time.now()
        self.inverseDir=[]
        self.teleop=False
        self.lastEncoderTick=[0,0,0,0]
        self.delta_cvt = 60.0/(math.pi * self.WHEEL_DIAMETER)  # cm_s --> rpm
        self.vx_now=0
        self.vy_now=0
        self.theta_now=0
        self.last_msg=1
       
        self.vx_run=0
        self.vy_run=0
        self.w_run=0
     
        # self.motors=[self.motorUp,self.motorDown]
        # self.last_time=time.time()
        self.speed_wheel_cm_s=[0,0,0,0]
        self.getCmdVel=False
        encoder_parameter= (math.pi * self.WHEEL_DIAMETER) / self.ENCODER_TOTAL
        self.cmPerCount= encoder_parameter# 7.05
        # rospy.sleep(1.5)
        # self.motorUp=ZLAC8015D.Controller(modbus_connection,id=1) # 0 forn
        # self.motorDown=ZLAC8015D.Controller(modbus_connection,id=2) # 1
        self.stop_all=False
        self.ms_pub_encoder=50.0
        self.rate_hz=(2000.0/self.ms_pub_encoder)
        # self.dt=1.0/self.rate_hz
        self.ms_pid=10.0
        print(f"total:{self.total_length}")
        self.rpm_to_cm_s=np.zeros(2)
        self.rate = rospy.Rate(self.rate_hz)  # 10 Hz
        rospy.Subscriber("/cmd_vel_timeout", Twist, self.cmdVelCb)  # Change to Twist message
        
        # Subscriber PID config: linear.x=KP, linear.y=KI, linear.z=KD
        rospy.Subscriber("/pid_config", Twist, self.pidConfigCb)
    
    def pidConfigCb(self, msg):
        """Nhan cau hinh PID tu topic.
        linear.x = KP, linear.y = KI, linear.z = KD
        """
        kp = msg.linear.x
        ki = msg.linear.y
        kd = msg.linear.z
        self.send_pid_config(kp, ki, kd)
    def cmdVelCb(self,msg):
        self.getCmdVel=True
        self.vx_run=msg.linear.x*100
        self.w_run=msg.angular.z
        self.calSpeed(self.vx_run,self.w_run)
        self.runRobot()
    
    def send_pid_config(self, kp, ki, kd):
        """Gui cau hinh PID den Arduino.
        Format: KP:KI#KD;
        Vi du: 1.5:0.1#0.05;
        """
        pid_data = "{:.2f}:{:.2f}#{:.2f};".format(kp, ki, kd)
        try:
            self.serial_port.write(pid_data.encode())
            rospy.loginfo("Sent PID config: KP={}, KI={}, KD={}".format(kp, ki, kd))
        except Exception as e:
            rospy.logerr("Error sending PID config: {}".format(e))
        
    # Chuẩn hóa sự cố tràn số của encoder
    def NormalizeOverflow(self,encoder_now,last_encod):
        new_delta=encoder_now-last_encod
        if new_delta>10000: # last_encod = -32760 --> motor quay nguoc encoder_now = 32760 --> quay nguoc -16 xung
            new_delta=(encoder_now-32768)-(32768+last_encod)
        elif new_delta<-10000: #last_encod=32760 --> motor quay thuan encoder_now=-32760 --> xung = +16
            new_delta=(32768+encoder_now)+(32768-last_encod)
        return new_delta
    
    # Tính toán sự khác biệt của encoder giữa lần đọc hiện tại và lần đọc trước đó
    def CaldiffEncoder(self,motor_left, motor_right):
        delta_encod_l=self.NormalizeOverflow(self.encoder_total[motor_left],self.last_encod[motor_left])
        delta_encod_r=self.NormalizeOverflow(self.encoder_total[motor_right],self.last_encod[motor_right])          
        self.last_encod[motor_left]=self.encoder_total[motor_left]
        self.last_encod[motor_right]=self.encoder_total[motor_right]
        return delta_encod_l,delta_encod_r
    
    
    def CylinderCB(self,msg):
        self.xylanh=msg.data
        
    # Tính toán vị trí và vận tốc dựa trên encoder
    def updatePos(self):
        encoderTick=[0,0]
        delta_tick=[0,0,0,0]
        delta=[0,0]
        # Bước 1 - 2: Đọc & normalize encoder counts
        delta_l_u,delta_r_u=self.CaldiffEncoder(self.M_LEFT_UP,self.M_RIGHT_UP)
        delta_l,delta_r=self.CaldiffEncoder(self.M_LEFT_DOWN,self.M_RIGHT_DOWN)
        encoderTick=[delta_l_u,delta_l,delta_r_u,delta_r]
        
        for i in range(self.NMOTORS):
            # Bước 3: Chuyển đổi xung encoder thành khoảng cách di chuyển (cm)
            delta_tick[i] =  encoderTick[i] *self.cmPerCount  # 0.14260
        # delta[self.M_LEFT]= (delta_tick[self.M_LEFT_UP]+delta_tick[self.M_LEFT_DOWN])
        # delta[self.M_RIGHT]= (delta_tick[self.M_RIGHT_UP]+delta_tick[self.M_RIGHT_DOWN])
        delta[self.M_LEFT]= delta_tick[self.M_LEFT_DOWN]
        delta[self.M_RIGHT]= delta_tick[self.M_RIGHT_DOWN]
        
        # vxy = (delta(Left) + delta(Right))/2.0
        dxy = (delta[self.M_LEFT]+delta[self.M_RIGHT])/2.0
        
        # dtheta = (delta(Right) - delta(Left))/total_length (total_length = distance between the two wheels)
        dtheta = ((delta[self.M_LEFT]-delta[self.M_RIGHT]))/self.total_length
        
        # dtheta=self.dtheta
        dx = math.cos(self.robot_pose[2]+(dtheta/2.0)) * dxy
        dy = math.sin(self.robot_pose[2]+(dtheta/2.0)) * dxy
        
        self.vx_now=0
        self.vy_now=0
        self.theta_now=0
        current_time = rospy.Time.now()
        
        # Tính toán khoảng thời gian giữa lần cập nhật hiện tại và lần cập nhật trước đó
        dt = (current_time - self.last_time_encod).to_sec()
        dxy=dxy/100.0
        dx=dx/100.0
        dy=dy/100.0
        
        # print(dt)
        #encoder chay lau troi --> 
        #gps sai so tinh 1-2m 
        ## fusion localization--> EKF extended kalmen filter
        if dt>0:
            # dt=dt
            # dtheta=dtheta
            self.vx_now=dxy/dt
            self.vy_now=0
            self.theta_now=dtheta/dt

            # Cập nhật vị trí của robot dựa trên sự khác biệt đã tính toán
            self.robot_pose[0] +=dx 
            self.robot_pose[1] += dy 
            self.robot_pose[2] += dtheta 
            
            # Chuẩn hóa góc theta để nằm trong [-pi, pi]
            if(self.robot_pose[2])>=math.pi:
                self.robot_pose[2]-=2.0*math.pi
            elif(self.robot_pose[2]<=-math.pi):
                self.robot_pose[2]+=2.0*math.pi
                
        # print(f"x:{self.theta_now} ; y:{self.robot_pose[2]}")
            odom = Odometry()
            odom.header.stamp = rospy.Time.now()
            odom.header.frame_id = "odom"
            odom.child_frame_id = "base_link"
            # print(f"x:{self.robot_pose[0]} y:{self.robot_pose[1]}")
            odom_x=self.robot_pose[0]
            odom_y=self.robot_pose[1]
            odom.pose.pose.position.x = odom_x
            odom.pose.pose.position.y = odom_y
            odom.pose.pose.position.z = 0.0
            
            # Quaternion from yaw angle
            q = tf.transformations.quaternion_from_euler(0, 0, self.robot_pose[2])
            odom.pose.pose.orientation.x = q[0]
            odom.pose.pose.orientation.y = q[1]
            odom.pose.pose.orientation.z = q[2]
            odom.pose.pose.orientation.w = q[3]
            odom_twist_yaw=0.35
            if(dtheta==0):
                odom_twist_yaw=1e-4
                
            # Hàng 1: X, Hàng 2: Y, Hàng 3: Z, Hàng 4: Roll, Hàng 5: Pitch, Hàng 6: Yaw
            # Tin tưởng vào x, y, hoàn toàn không tin tưởng vào z, roll, pitch
