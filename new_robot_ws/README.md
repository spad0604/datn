# new_robot_ws (standalone)

This folder is a standalone **catkin workspace** containing the `new_robot` package.

## Folder Split

- `src/system/`: runtime entrypoints used by launch files.
- `test/`: standalone test scripts.
- `src/`: legacy implementation files kept behind the system wrappers.
- `launch/main.launch`: the top-level program entrypoint that brings everything up.

## Quick start (ROS1 on Ubuntu/Pi)

```bash
source /opt/ros/$ROS_DISTRO/setup.bash

cd ~/new_robot_ws
catkin_make
source devel/setup.bash

# python deps (serial + BE client)
pip3 install -r src/new_robot/requirements.txt

# base control (no server, no lidar, no navigation)
roslaunch new_robot main.launch enable_server:=false enable_lidar:=false enable_navigation:=false
```

## Notes

- This workspace assumes ROS1 is already installed (e.g., `ros-noetic-*`).
- Optional features:
  - LiDAR launch expects `xv_11_laser_driver` package in the same workspace.
  - Navigation expects `move_base` stack and related configs.
