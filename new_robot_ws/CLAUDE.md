# ROS Workspace - new_robot_ws

ROS1 Noetic catkin workspace running on Raspberry Pi. Controls the delivery robot: navigation, lidar, server communication, and hardware interface.

## Tech Stack
- **ROS1 Noetic**, Python 3
- **Navigation**: DWA local planner, costmaps
- **Lidar**: XV-11 / LDS-007
- **Communication**: STOMP WebSocket (websocket-client), REST (requests)
- **Odometry**: Differential drive encoder integration
- **GPS**: SIM7600X NMEA stream (passive, no AT), publish `/fix`
- **IMU**: Bosch BNO055 over I2C (smbus2), NDOF fusion, publish `/imu/data`

## Package Layout
```
src/new_robot/
├── NODES.md                    # Per-node topic/message/param reference
├── launch/
│   ├── main.launch              # Top-level entry (includes full.launch)
│   ├── full.launch              # bringup + optional navigation
│   ├── bringup.launch           # hardware + server + gps + imu + lidar
│   ├── server.launch            # WebSocket nodes + gps (default) + arduino bridge
│   ├── gps.launch               # gps_publisher (ttyUSB3 NMEA)
│   ├── imu.launch               # imu_publisher (BNO055 I2C)
│   ├── serial_test.launch       # ESP32 serial + cmd_vel timeout + arduino bridge
│   ├── navigation_dwa.launch    # DWA path planning
│   ├── lidar_xv11.launch        # XV-11 lidar driver
│   ├── lidar_custom.launch      # Custom LDS-007 lidar
│   └── lidar_signal.launch      # Signal-based lidar
├── cfg/
│   ├── costmap_common_params.yaml
│   ├── dwa_local_planner_params.yaml
│   ├── global_costmap_params.yaml
│   ├── local_costmap_params.yaml
│   └── move_base_params.yaml
├── src/
│   ├── system/
│   │   ├── ServerInterface.py       # Order listener state machine (WS only, TF/waypoint routing removed)
│   │   ├── UpdateLocation.py        # Periodic GPS->BE location updates
│   │   ├── HardwareInterface.py     # Arduino UART bridge (SIM7600 SMS code removed)
│   │   ├── pubVelEncoderDiff.py     # Odometry publisher (differential drive)
│   │   ├── gps_publisher.py         # SIM7600 NMEA -> /fix (no AT commands)
│   │   ├── imu_publisher.py         # BNO055 I2C -> /imu/data (smbus2, NDOF)
│   │   ├── listen_orders.py         # Simple order listener CLI
│   │   ├── cmd_vel_fake.py          # cmd_vel timeout + turn signal bridge
│   │   └── lidar/
│   │       ├── lidar_lds007_node.py # LDS-007 ROS node
│   │       ├── lidar_processor.py   # Scan data processing
│   │       └── lds007_uart_reader.py # UART communication
│   └── server/
│       ├── ws_client.py             # STOMP WebSocket client (ServerService)
│       └── config_ws.py             # Fallback URL/secret config
├── test_script/                # Standalone hardware probes (no ROS)
│   ├── test_bno055.py
│   └── test_sim7600.py
└── requirements.txt
```

Top-level Python packages in `src/` are `system` and `server` (flat layout after
the `new_robot/` sub-folder was removed). Imports use `from server.ws_client import ...`,
not `new_robot.server.*`. Keep `setup.py` / `CMakeLists.txt` entries aligned.

## ROS Nodes

For the full topic map, message formats and parameters, see `src/new_robot/NODES.md`.
Short summary below.

### order_listener_sm (ServerInterface.py)
- **Purpose**: Listen for orders from BE via WebSocket
- **Subscribes**: `/Status_robot` (String)
- **Publishes**: `serial_ard_tx` (String) - `UNLOCK <pin>` and `LCD|<line1>|<line2>`
- **WebSocket**: STOMP `/topic/robot-order/{robotId}` with 5s retry
- **Removed**: `/waypoints` publisher, TF `utm->map` wait, and `utm`/`tf2_*` imports.
  Waypoint routing will come back when `navsat_transform_node` is wired in.

### update_location (UpdateLocation.py)
- **Subscribes**: `/fix` (NavSatFix)
- **Output**: HTTP POST `/api/v1/robot/update-location` via `ServerService`
- **Throttle**: only sends when moved ≥ `~max_distance_meters` since last push

### gps_publisher (gps_publisher.py)
- **Purpose**: Passive NMEA reader for SIM7600X — no AT commands
- **Publishes**: `/fix` (NavSatFix), frame `gps`, default 1Hz
- **Port**: `/dev/ttyUSB3` (the NMEA port; ttyUSB2 would be the AT port)
- **Handles SIM7600 USB-CDC `BrokenPipeError`** by opening with `dsrdtr=True`
  and not touching DTR/RTS.

### imu_publisher (imu_publisher.py)
- **Purpose**: BNO055 over I2C using raw registers (smbus2, no `adafruit_bno055`)
- **Publishes**: `/imu/data` (Imu), frame `imu_link`, default 100Hz
- **Mode**: NDOF (9-DoF fusion). Address default `0x29` (ADR pin tied to VCC)
- **Covariances**: copied from the legacy calibration in `robot_ws/cleaning_robot`

### arduino_interface (HardwareInterface.py)
- **Purpose**: UART bridge to Arduino Nano for LCD + lock relay
- **Subscribes**: `serial_ard_tx` (String), `/Status_robot` (String)
- **Publishes**: `/Status_robot` (`"MOVING"` after Arduino acks DOING)
- **State machine**: WAITING -> DOING -> SUCCESS -> WAITING
- **SIM7600 SMS code removed** (was unused `use_sim=False`). Node now only
  manages the Arduino port.

### pubVelEncoderDiff (pubVelEncoderDiff.py)
- **Subscribes**: `/cmd_vel_timeout` (Twist), `/pid_config` (Twist)
- **Publishes**: `/odom` (Odometry), `/speed_desired`, `/speed_feedback`,
  `MOTOR_ERROR`, TF `odom -> base_link`
- **Parameters**: wheel_diameter=9.5cm, encoder_total=1798 pulses/rev, robot_length=52.89cm

### cmd_vel_timeout (cmd_vel_fake.py)
- **Subscribes**: `cmd_vel` (Twist)
- **Publishes**: `cmd_vel_timeout` (Twist), `serial_ard_tx` (L_ON/R_ON for turn signals)
- **Safety**: publishes zero Twist if no cmd_vel for 0.5s

## Launch Hierarchy
```
main.launch
  └── full.launch
        ├── bringup.launch
        │     ├── serial_test.launch    (ESP32 UART + cmd_vel_timeout + arduino bridge)
        │     ├── gps.launch            (if enable_gps, default true)
        │     ├── imu.launch            (if enable_imu, default true)
        │     ├── server.launch         (WebSocket nodes — gps + arduino bridge
        │     │                          are force-disabled here to avoid
        │     │                          double-launch from bringup)
        │     └── lidar_xv11.launch     (if enable_lidar)
        └── navigation_dwa.launch       (if enable_navigation)
```

Running `server.launch` standalone *does* start `gps_publisher` (so
`update_location` has a `/fix` source). When included from `bringup.launch`,
the parent passes `enable_gps:=false` and `enable_arduino_bridge:=false` to
avoid conflicting with its own copies of those nodes.

## Configuration

### Server Connection (server.launch args)
- `ws_url`: `ws://192.168.100.153:8080/ws-delivery-native`
- `api_base_url`: `http://192.168.100.153:8080/api/v1/robot`
- `secret_key`: `DATN_2025_2_GIAP`

### Navigation (DWA)
- Max velocity: 0.14 m/s forward, 0.6 rad/s angular
- Goal tolerance: 0.15m XY, 0.22 rad yaw
- Obstacle inflation: 0.2285m
- Robot footprint: 1.0m x 0.2m rectangle

### Hardware
- ESP32 serial: 57600 baud, port `/dev/esp32`
- Arduino serial: 9600 baud (for lock mechanism)
- Encoder: 1798 pulses/rev, wheel diameter 9.5cm
- GPS: SIM7600X USB, NMEA on `/dev/ttyUSB3` @115200
- IMU: BNO055 on I2C bus 1, address `0x29`

## Important Notes

- `config_ws.py` contains fallback IPs used when ROS params are missing. Keep it in sync with `server.launch`.
- `ServerService` (`ws_client.py`) opens a fresh STOMP connection for each location update. The order listener keeps a persistent connection with 5s retry.
- SIM7600 is used **only as a USB GPS receiver** now. AT/SMS code was removed from `HardwareInterface.py`. The module enumerates 4 ttyUSB ports; `/dev/ttyUSB3` is the NMEA stream (no AT), `/dev/ttyUSB2` is the AT port (not used).
- BNO055 is read via raw I2C registers with `smbus2` instead of `adafruit_bno055`, so no CircuitPython / `board` / `busio` deps are needed on the Pi.
- `test_script/` contains standalone probes that run without ROS, useful for bench-testing a single sensor.

## Dependencies
```
numpy, pyserial, requests, websocket-client, utm, matplotlib, smbus2
```
