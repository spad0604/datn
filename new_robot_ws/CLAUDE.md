# ROS Workspace - new_robot_ws

ROS1 Noetic catkin workspace running on Raspberry Pi. Controls the delivery robot: navigation, lidar, server communication, and hardware interface.

## Tech Stack
- **ROS1 Noetic**, Python 3
- **Navigation**: DWA local planner, costmaps
- **Lidar**: XV-11 / LDS-007
- **Communication**: STOMP WebSocket (websocket-client), REST (requests)
- **Odometry**: Differential drive encoder integration
- **GPS**: navsat_transform for UTM<->map frame conversion

## Package Layout
```
src/new_robot/
├── launch/
│   ├── main.launch              # Top-level entry (includes full.launch)
│   ├── full.launch              # bringup + optional navigation
│   ├── bringup.launch           # hardware + server + lidar
│   ├── server.launch            # WebSocket nodes only
│   ├── serial_test.launch       # ESP32 serial communication
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
├── src/new_robot/
│   ├── system/
│   │   ├── ServerInterface.py       # Order listener state machine (WS + TF)
│   │   ├── UpdateLocation.py        # Periodic GPS->BE location updates
│   │   ├── HardwareInterface.py     # Motor/encoder serial comm
│   │   ├── pubVelEncoderDiff.py     # Odometry publisher (differential drive)
│   │   ├── listen_orders.py         # Simple order listener
│   │   ├── cmd_vel_fake.py          # Velocity command simulator
│   │   └── lidar/
│   │       ├── lidar_lds007_node.py # LDS-007 ROS node
│   │       ├── lidar_processor.py   # Scan data processing
│   │       └── lds007_uart_reader.py # UART communication
│   └── server/
│       ├── ws_client.py             # STOMP WebSocket client (ServerService)
│       └── config_ws.py             # Fallback URL/secret config
└── requirements.txt
```

## ROS Nodes

### order_listener_sm (ServerInterface.py)
- **Purpose**: Listen for orders from BE via WebSocket, publish waypoints
- **Subscribes**: `/Status_robot` (String) - state transitions
- **Publishes**: `/waypoints` (PoseArray), `serial_ard_tx` (String - Arduino commands)
- **WebSocket**: Connects to BE STOMP, subscribes to `/topic/robot-order/{robotId}`
- **TF**: Waits for `utm -> map` transform (from navsat_transform) in background thread
- **State Machine**: LISTENING -> WAITING (when order received, waits for robot to finish)
- **Arduino commands sent via `serial_ard_tx`**:
  - `UNLOCK <pin>` on new order (8-digit PIN, zero-padded)
  - `LCD|<line1>|<line2>` on order status change (phase + identifier)

### update_location (UpdateLocation.py)
- **Purpose**: Send robot GPS position to BE periodically
- **Subscribes**: `/fix` (NavSatFix) - GPS data
- **WebSocket**: Sends to `/app/update-location` via STOMP
- **Logic**: Only sends if moved > min_distance since last update

### pubVelEncoderDiff (pubVelEncoderDiff.py)
- **Purpose**: Differential drive odometry from encoder data
- **Subscribes**: `/cmd_vel_timeout` (Twist), `/pid_config` (Twist)
- **Publishes**: `/odom` (Odometry), TF `odom -> base_link`
- **Serial**: Reads encoder counts, sends speed commands to ESP32
- **Parameters**: wheel_diameter=9.5cm, encoder_total=1798 pulses/rev, robot_length=52.89cm

## Launch Hierarchy
```
main.launch
  └── full.launch
        ├── bringup.launch
        │     ├── serial_test.launch    (ESP32 UART)
        │     ├── server.launch         (WebSocket nodes)
        │     └── lidar_xv11.launch     (Lidar)
        └── navigation_dwa.launch       (optional)
```

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

## Important Notes

- `ServerInterface.py` starts WebSocket listener immediately; TF wait runs in background thread. This allows server.launch to work standalone without navsat_transform.
- `config_ws.py` contains fallback IPs used when ROS params are missing. Keep it in sync with `server.launch`.
- The `ws_client.py` (ServerService) opens a fresh STOMP connection for each location update. The order listener maintains a persistent connection with retry logic (5s delay).

## Dependencies
```
numpy, pyserial, requests, websocket-client, utm, matplotlib
```
