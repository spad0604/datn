cmake_minimum_required(VERSION 3.0.2)
project(new_robot)

find_package(catkin REQUIRED)

catkin_python_setup()

catkin_package()

# This package is Python/launch focused.

# Make Python nodes discoverable by rosrun/roslaunch (generated into devel/lib/new_robot)
catkin_install_python(PROGRAMS
  src/system/cmd_vel_fake.py
  src/system/pubVelEncoderDiff.py
  src/system/HardwareInterface.py
  src/system/ServerInterface.py
  src/system/UpdateLocation.py
  src/system/listen_orders.py
  src/system/gps_publisher.py
  src/system/lidar/lidar_processor.py
  src/system/lidar/lidar_lds007_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY launch cfg
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  USE_SOURCE_PERMISSIONS
)
