# ROS Nodes — new_robot

Tài liệu tóm tắt các ROS node trong package `new_robot`: vai trò, topic subscribe/publish, format message, tham số chính.

Sơ đồ luồng tổng quát:

```
[BE]   ──WS──►  order_listener_sm ──serial_ard_tx──►  arduino_interface ──UART──►  [Arduino]
                                                      ▲
  /fix◄── gps_publisher  (ttyUSB3 NMEA)               │
  /imu/data◄── imu_publisher  (BNO055 I2C)            │
                                                      │
[cmd_vel]─► cmd_vel_timeout ─/cmd_vel_timeout─► esp32_odom ──UART──► [ESP32]
                           └─serial_ard_tx───►  (đèn tín hiệu)       ▲
                                                                     │
                               /fix ──► update_location ──WS──► [BE]
```

---

## 1. `gps_publisher` — `gps_publisher.py`

Đọc NMEA từ cổng USB của SIM7600X, parse `$xxGGA`, publish `NavSatFix`.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| pub   | `/fix` | `sensor_msgs/NavSatFix` | Publish liên tục theo `rate_hz`. Chưa có fix thì `status.status = STATUS_NO_FIX (-1)`, lat/lon/alt = NaN. |

Format `/fix`:
```
header:
  stamp: <ROS time>
  frame_id: "gps"           # ~frame_id
status:
  status: -1 (NO_FIX) hoặc 0 (FIX)
  service: 1 (GPS)
latitude:  float64  (degrees, WGS84)
longitude: float64  (degrees, WGS84)
altitude:  float64  (meters, MSL)
position_covariance:       [0]*9
position_covariance_type:  0 (COVARIANCE_TYPE_UNKNOWN)
```

Params:
- `~port` (str, `/dev/ttyUSB3`): cổng NMEA của SIM7600.
- `~baud` (int, `115200`).
- `~frame_id` (str, `gps`).
- `~rate_hz` (float, `1.0`).

---

## 2. `imu_publisher` — `imu_publisher.py`

Đọc BNO055 qua I2C (smbus2, không cần `adafruit_bno055`), publish `Imu`.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| pub   | `/imu/data` | `sensor_msgs/Imu` | Chế độ NDOF: có orientation (quaternion từ fusion), angular_velocity (rad/s), linear_acceleration (m/s², đã bỏ trọng lực). |

Format `/imu/data`:
```
header:
  stamp: <ROS time>
  frame_id: "imu_link"
orientation:                         # quaternion đã normalize
  w, x, y, z: float64
orientation_covariance: [9 float]    # diag: roll_var, pitch_var, yaw_var
angular_velocity:                    # rad/s
  x, y, z: float64
angular_velocity_covariance: [9 float]
linear_acceleration:                 # m/s^2, gravity removed
  x, y, z: float64
linear_acceleration_covariance: [9 float]
```

Params:
- `~bus` (int, `1`): số bus I2C.
- `~address` (int, `0x29`): BNO055 address (robot dây ADR → VCC).
- `~frame_id` (str, `imu_link`).
- `~rate_hz` (float, `100.0`).

Yêu cầu: `pip install smbus2`. Calibration status in ra stdout chung khi start.

---

## 3. `order_listener_sm` — `ServerInterface.py`

Lắng nghe đơn hàng từ BE qua STOMP WebSocket; với mỗi đơn mới, publish PIN mở khóa và nội dung LCD xuống Arduino.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| sub   | `/Status_robot` | `std_msgs/String` | Nhận `"STARTING"` để chuyển state WAITING → LISTENING. |
| pub   | `serial_ard_tx` | `std_msgs/String` | Chuỗi lệnh text cho Arduino. |

Format `serial_ard_tx` do node này sinh ra:
- `UNLOCK <pin>` — `<pin>` 8 chữ số (zero-pad nếu cần). Gửi khi có đơn pending mới.
- `LCD|<line1>|<line2>` — mỗi line ≤ 16 ký tự ASCII. Gửi khi trạng thái đơn thay đổi. `<line1>` là phase (`DI LAY DON` / `DI GIAO DON` / `DA GIAO XONG` / `DANG XU LY`), `<line2>` là tên người nhận hoặc `#<orderId>`.

WebSocket:
- Kết nối `ws_url`, subscribe `/topic/robot-order/{robotId}`.
- Retry 5s khi mất kết nối.

Params:
- `~ws_url`, `~api_base_url`, `~secret_key` (fallback trong `server/config_ws.py`).

---

## 4. `update_location` — `UpdateLocation.py`

Gửi vị trí GPS của robot lên BE định kỳ, chỉ khi di chuyển đủ xa để tránh spam.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| sub   | `/fix` | `sensor_msgs/NavSatFix` | Chỉ ghi nhận khi `status.status >= 0`. |

Không publish ROS topic nào — đầu ra là HTTP POST `/api/v1/robot/update-location` qua `ServerService`.

Logic:
1. Mỗi `~interval_seconds`, so sánh vị trí mới nhất với vị trí BE đang lưu.
2. Nếu Haversine ≥ `~max_distance_meters` thì gọi `update_robot_location`.
3. Lần đầu tiên luôn gửi.

Params:
- `~ws_url`, `~api_base_url`, `~secret_key`.
- `~interval_seconds` (int, `10`).
- `~max_distance_meters` (float, `10.0`). Tên tham số là max nhưng thực chất là ngưỡng tối thiểu để coi là đã di chuyển.

---

## 5. `arduino_interface` — `HardwareInterface.py`

Bridge giữa ROS và Arduino Nano qua UART. Cầm state machine UNLOCK/LCD/SUCCESS.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| sub   | `serial_ard_tx` | `std_msgs/String` | Mỗi message được gửi xuống UART kèm `\n`. |
| sub   | `/Status_robot` | `std_msgs/String` | `"DOING"` / `"SUCCESS"` để chuyển state. |
| pub   | `/Status_robot` | `std_msgs/String` | Publish `"MOVING"` khi Arduino trả `OK` ở state DOING. |

State machine:
- `WAITING` → nhận `DOING` từ topic → chuyển `DOING`.
- `DOING` → Arduino reply `OK` → publish `MOVING`, set `pending_action=sent_doing`.
- `DOING` → nhận `SUCCESS` → chuyển `SUCCESS`, ghi `L_ON\n` ra UART (bật khóa).
- `SUCCESS` → Arduino reply `OK` → về `WAITING`.

Params:
- `~port_arduino` (str, `/dev/arduino`).
- `~baudrate_ard` (int, `9600`).

Protocol UART với Arduino (text, newline-terminated):
```
TX (ROS → Arduino):
  UNLOCK <8-digit-pin>
  LCD|<line1>|<line2>
  L_ON            # bật khóa khi giao xong

RX (Arduino → ROS):
  OK              # xác nhận đã nhận/xử lý lệnh trước
```

---

## 6. `esp32_odom` — `pubVelEncoderDiff.py`

Driver giao tiếp ESP32: nhận vận tốc mục tiêu, đọc encoder, tính odometry.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| sub   | `/cmd_vel_timeout` | `geometry_msgs/Twist` | Đầu ra của `cmd_vel_timeout` (cmd_vel có timeout). |
| sub   | `/pid_config` | `geometry_msgs/Twist` | Cập nhật Kp/Ki/Kd runtime (x=Kp, y=Ki, z=Kd). |
| pub   | `/odom` | `nav_msgs/Odometry` | Odometry tính từ encoder, frame `odom → base_link`. |
| pub   | `/speed_desired` | `std_msgs/Float32` | Tốc độ đặt cho PID (debug). |
| pub   | `/speed_feedback` | `std_msgs/Float32` | Tốc độ thực đo từ encoder (debug). |
| pub   | `MOTOR_ERROR` | `std_msgs/Bool` | True khi phát hiện lỗi motor. |
| tf    | — | — | Broadcast `odom → base_link`. |

Params:
- `~port` (`/dev/esp32`), `~baud` (`57600`).
- `~wheel_diameter` (cm, `9.5`), `~encoder_total` (pulses/rev, `1798`).
- `~use_imu` (bool, `False`) — chưa dùng.

UART protocol với ESP32 (57600 baud): gửi vận tốc bánh trái/phải, nhận tick encoder. Chi tiết trong `MCU/ESP32/src/src.ino`.

---

## 7. `cmd_vel_timeout` — `cmd_vel_fake.py`

An toàn cho velocity: nếu không nhận `cmd_vel` trong 0.5s thì publish zero. Đồng thời bật đèn tín hiệu trái/phải theo `angular.z`.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| sub   | `cmd_vel` | `geometry_msgs/Twist` | Nguồn: move_base hoặc teleop. |
| pub   | `cmd_vel_timeout` | `geometry_msgs/Twist` | Forward message, hoặc zero Twist khi timeout. |
| pub   | `serial_ard_tx` | `std_msgs/String` | `L_ON` / `R_ON` để bật đèn xi-nhan trên Arduino. |

Logic:
- Forward `cmd_vel` ngay lập tức.
- Nếu `linear.x < 0` (lùi), đảo dấu `angular.z` khi chọn đèn.
- `angular.z > 0.1` → `R_ON` (đèn phải). `angular.z < -0.1` → `L_ON`.
- Không có cmd_vel trong 0.5s → publish Twist = 0 (một lần, không lặp).

---

## 8. `listen_orders` — `listen_orders.py`

Utility CLI để in đơn hàng BE realtime (debug). Không phải node production.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| —     | —     | —            | Chỉ gọi `ServerService.listen_orders`, in ra stdout. |

---

## 9. Lidar nodes

### `lidar_lds007` — `lidar/lidar_lds007_node.py`

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| pub   | `/scan` | `sensor_msgs/LaserScan` | LDS-007 qua UART custom protocol (22-byte packet). |

### `lidar_processor` — `lidar/lidar_processor.py`

Filter + DWA local planner đơn giản cho lidar.

| Hướng | Topic | Message type | Ghi chú |
|-------|-------|--------------|---------|
| sub   | `/scan` (hoặc `~scan_topic`) | `sensor_msgs/LaserScan` | |
| pub   | `/scan_processed` | `sensor_msgs/LaserScan` | Đã lọc nhiễu / clamp range. |
| pub   | `/cmd_vel` (hoặc `~cmd_topic`) | `geometry_msgs/Twist` | Twist sau khi né vật cản. |

---

## Bảng topic tổng hợp

| Topic | Type | Publishers | Subscribers |
|-------|------|------------|-------------|
| `/fix` | `sensor_msgs/NavSatFix` | `gps_publisher` | `update_location` |
| `/imu/data` | `sensor_msgs/Imu` | `imu_publisher` | (reserved for EKF) |
| `/Status_robot` | `std_msgs/String` | `arduino_interface` | `order_listener_sm`, `arduino_interface` |
| `serial_ard_tx` | `std_msgs/String` | `order_listener_sm`, `cmd_vel_timeout` | `arduino_interface` |
| `cmd_vel` | `geometry_msgs/Twist` | move_base / teleop / `lidar_processor` | `cmd_vel_timeout` |
| `cmd_vel_timeout` | `geometry_msgs/Twist` | `cmd_vel_timeout` | `esp32_odom` |
| `/pid_config` | `geometry_msgs/Twist` | (rostopic pub thủ công) | `esp32_odom` |
| `/odom` | `nav_msgs/Odometry` | `esp32_odom` | move_base / EKF |
| `/speed_desired` | `std_msgs/Float32` | `esp32_odom` | (debug) |
| `/speed_feedback` | `std_msgs/Float32` | `esp32_odom` | (debug) |
| `MOTOR_ERROR` | `std_msgs/Bool` | `esp32_odom` | (monitor) |
| `/scan` | `sensor_msgs/LaserScan` | `lidar_lds007` hoặc `xv11_lidar` | `lidar_processor` |
| `/scan_processed` | `sensor_msgs/LaserScan` | `lidar_processor` | (debug / move_base) |

---

## Launch quick-ref

- `roslaunch new_robot gps.launch` — chỉ GPS.
- `roslaunch new_robot imu.launch` — chỉ IMU.
- `roslaunch new_robot server.launch` — GPS + order listener + update location + arduino bridge (gửi `/fix` lên BE luôn). Tắt GPS nếu không cần: `enable_gps:=false`.
- `roslaunch new_robot serial_test.launch` — cmd_vel_timeout + esp32_odom + arduino_interface.
- `roslaunch new_robot bringup.launch` — tất cả phần trên (GPS, IMU, serial, server). Lidar optional. Tự disable GPS + arduino_bridge khi include server.launch để không bị double-open port.
- `roslaunch new_robot full.launch` — bringup + navigation (optional).

Disable từng phần bằng arg: `enable_gps:=false`, `enable_imu:=false`, `enable_lidar:=true`, v.v.
