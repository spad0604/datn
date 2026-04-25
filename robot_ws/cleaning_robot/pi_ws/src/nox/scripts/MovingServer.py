#!/usr/bin/env python3
import rospy
import actionlib
from smach import State, StateMachine
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import PoseArray, PoseWithCovarianceStamped, PoseStamped
from std_msgs.msg import String
from tf import TransformListener
import tf
import math
import time

# Global variables
waypoints = []
start_moving = False
is_cancelled = False 

state_topic = "Status_robot"
state_publisher = None

def init_global_publisher():
    global state_publisher
    if state_publisher is None:
        state_publisher = rospy.Publisher(state_topic, String, queue_size=10)
        rospy.loginfo("Global state publisher created on topic: %s", state_topic)

def publish_status(status):
    if state_publisher:
        state_publisher.publish(String(data=status))
        rospy.loginfo("Published status: '%s'", status)

# Change Pose to the correct frame
def changePose(waypoint, target_frame):
    if waypoint.header.frame_id == target_frame:
        return waypoint
    if not hasattr(changePose, 'listener'):
        changePose.listener = tf.TransformListener()
    tmp = PoseStamped()
    tmp.header.frame_id = waypoint.header.frame_id
    tmp.pose = waypoint.pose.pose
    try:
        changePose.listener.waitForTransform(target_frame, tmp.header.frame_id, rospy.Time(0), rospy.Duration(3.0))
        pose = changePose.listener.transformPose(target_frame, tmp)
        ret = PoseWithCovarianceStamped()
        ret.header.frame_id = target_frame
        ret.pose.pose = pose.pose
        return ret
    except Exception as e:
        rospy.logwarn("CAN'T TRANSFORM POSE TO %s FRAME: %s", target_frame, str(e))
        return None

def convert_PoseWithCovArray_to_PoseArray(waypoints):
    poses = PoseArray()
    poses.header.frame_id = rospy.get_param('~goal_frame_id', 'map')
    poses.header.stamp = rospy.Time.now()
    poses.poses = [wp.pose.pose for wp in waypoints if wp is not None]
    return poses

class GetPath(State):
    def __init__(self):
        State.__init__(self, outcomes=['success', 'preempted'],
                         input_keys=['waypoints'], output_keys=['waypoints'])
        self.waypoints_topic = rospy.get_param('~waypoints_topic', '/waypoints')
        self.posearray_topic = rospy.get_param('~posearray_topic', '/waypoints_viz')
        self.frame_id = rospy.get_param('~goal_frame_id', 'map')

        self.poseArray_publisher = rospy.Publisher(self.posearray_topic, PoseArray, queue_size=1)
        
        init_global_publisher()
        publish_status("IDLE")

        # Subscribe
        rospy.Subscriber(self.waypoints_topic, PoseArray, self.waypoints_callback)
        rospy.Subscriber(state_topic, String, self.command_callback)

    def command_callback(self, msg):
        global start_moving, is_cancelled
        if msg.data == "MOVING":
            start_moving = True
            rospy.loginfo("Received MOVING command")
        elif msg.data == "CANCEL":
            is_cancelled = True
            start_moving = False
            rospy.loginfo("Received CANCEL command")

    def waypoints_callback(self, msg):
        global waypoints
        waypoints = []
        for pose in msg.poses:
            pose_cov = PoseWithCovarianceStamped()
            pose_cov.header = msg.header
            pose_cov.pose.pose = pose
            transformed = changePose(pose_cov, self.frame_id)
            if transformed:
                waypoints.append(transformed)
        
        self.poseArray_publisher.publish(convert_PoseWithCovArray_to_PoseArray(waypoints))
        rospy.loginfo("Received %d waypoints", len(waypoints))
        publish_status("DOING")

    def execute(self, userdata):
        global waypoints, start_moving, is_cancelled
        waypoints = []
        start_moving = False
        is_cancelled = False

        publish_status("IDLE")
        rospy.loginfo("Waiting for waypoints and MOVING command...")

        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            if is_cancelled:
                waypoints = []
                start_moving = False
                publish_status("IDLE")
                is_cancelled = False  # reset flag
                rospy.loginfo("Cancelled and reset. Waiting for new path...")

            if waypoints and start_moving:
                userdata.waypoints = waypoints[:]  # copy list
                return 'success'

            rate.sleep()

        return 'preempted'


class FollowPath(State):
    def __init__(self):
        State.__init__(self, outcomes=['success', 'aborted', 'preempted'],
                         input_keys=['waypoints'])
        self.frame_id = rospy.get_param('~goal_frame_id', 'map')
        self.distance_tolerance = rospy.get_param('~waypoint_distance_tolerance', 1.3)  # mét
        self.final_orientation_tolerance = rospy.get_param('~final_orientation_tolerance', 1.0)  # radian

        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo('Connecting to move_base...')
        self.client.wait_for_server(rospy.Duration(10))
        rospy.loginfo('Connected to move_base.')

        self.listener = tf.TransformListener()

    def execute(self, userdata):
        global waypoints, is_cancelled

        if not waypoints:
            rospy.logwarn("No waypoints to follow!")
            return 'aborted'

        publish_status("DOING")

        for i, waypoint in enumerate(waypoints):
            if rospy.is_shutdown() or is_cancelled:
                self.client.cancel_goal()
                waypoints = []
                publish_status("IDLE")
                rospy.loginfo("FollowPath cancelled.")
                return 'preempted'

            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = self.frame_id
            goal.target_pose.header.stamp = rospy.Time.now()
            goal.target_pose.pose.position = waypoint.pose.pose.position

            # Chỉ waypoint cuối cùng mới giữ nguyên orientation
            if i == len(waypoints) - 1:
                goal.target_pose.pose.orientation = waypoint.pose.pose.orientation
                rospy.loginfo("Final waypoint %d/%d - Full pose (position + orientation)", i+1, len(waypoints))
            else:
                # Các điểm giữa: chỉ cần vị trí, orientation để robot dễ quay đầu
                # Có thể để orientation hiện tại hoặc hướng về điểm tiếp theo
                goal.target_pose.pose.orientation.w = 1.0  # quaternion identity (hướng bất kỳ)
                rospy.loginfo("Intermediate waypoint %d/%d - Position only", i+1, len(waypoints))

            rospy.loginfo("Sending goal: (%.2f, %.2f)", 
                          goal.target_pose.pose.position.x, goal.target_pose.pose.position.y)
            self.client.send_goal(goal)

            # Chờ đến khi gần đủ vị trí (không cần chờ hoàn toàn cho điểm giữa)
            while not rospy.is_shutdown():
                if is_cancelled:
                    self.client.cancel_goal()
                    waypoints = []
                    publish_status("IDLE")
                    return 'preempted'

                state = self.client.get_state()
                if state in [actionlib.GoalStatus.SUCCEEDED, actionlib.GoalStatus.PREEMPTED]:
                    break

                # Kiểm tra khoảng cách đến vị trí
                try:
                    now = rospy.Time.now()
                    self.listener.waitForTransform(self.frame_id, 'base_footprint', now, rospy.Duration(1.0))
                    trans, rot = self.listener.lookupTransform(self.frame_id, 'base_footprint', now)
                    dx = goal.target_pose.pose.position.x - trans[0]
                    dy = goal.target_pose.pose.position.y - trans[1]
                    dist = math.sqrt(dx*dx + dy*dy)

                    if dist < self.distance_tolerance:
                        rospy.loginfo("Reached waypoint %d (dist: %.2f < %.2f)", i+1, dist, self.distance_tolerance)
                        break
                except:
                    pass

                rospy.sleep(0.1)

            # Nếu là điểm cuối, có thể chờ thêm để đúng hướng (tùy chọn)
            if i == len(waypoints) - 1:
                self.client.wait_for_result(rospy.Duration(5))  # chờ thêm cho đúng hướng

        return 'success'


class PathComplete(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])
        init_global_publisher()

    def execute(self, userdata):
        global waypoints
        waypoints = []  # reset sau khi hoàn thành
        rospy.loginfo('###############################')
        rospy.loginfo('##### REACHED FINISH GATE #####')
        rospy.loginfo('###############################')
        publish_status("SUCCESS")
        return 'success'


def main():
    rospy.init_node('follow_waypoints')
    init_global_publisher()
    publish_status("IDLE")

    sm = StateMachine(outcomes=['success', 'aborted', 'preempted'])
    with sm:
        StateMachine.add('GET_PATH', GetPath(),
                         transitions={'success': 'FOLLOW_PATH', 'preempted': 'GET_PATH'},
                         remapping={'waypoints': 'waypoints'})
        StateMachine.add('FOLLOW_PATH', FollowPath(),
                         transitions={'success': 'PATH_COMPLETE',
                                      'aborted': 'GET_PATH',
                                      'preempted': 'GET_PATH'},
                         remapping={'waypoints': 'waypoints'})
        StateMachine.add('PATH_COMPLETE', PathComplete(),
                         transitions={'success': 'GET_PATH'})

    outcome = sm.execute()
    rospy.loginfo("SMACH finished with outcome: %s", outcome)
    rospy.spin()


if __name__ == '__main__':
    main()