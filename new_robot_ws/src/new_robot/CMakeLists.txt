cmake_minimum_required(VERSION 3.0.2)
project(new_robot)

find_package(catkin REQUIRED)

catkin_python_setup()

catkin_package()

# This package is Python/launch focused.

# Make Python nodes discoverable by rosrun/roslaunch (generated into devel/lib/new_robot)
catkin_install_python(PROGRAMS
  src/new_robot/system/cmd_vel_fake.py
  src/new_robot/system/pubVelEncoderDiff.py
  src/new_robot/system/HardwareInterface.py
  src/new_robot/system/ServerInterface.py
  src/new_robot/system/UpdateLocation.py
  src/new_robot/system/listen_orders.py
  src/new_robot/system/lidar/lidar_processor.py
  src/new_robot/system/lidar/lidar_lds007_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch cfg
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  USE_SOURCE_PERMISSIONS
)
