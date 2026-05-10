# Kiến trúc phần mềm ROS trên robot — Mô tả chi tiết cho báo cáo đồ án

Tài liệu này mô tả đầy đủ thiết kế của tầng điều khiển robot chạy trên Raspberry Pi (ROS1 Noetic), gồm: cấu trúc package, từng node thành phần, luồng dữ liệu, thuật toán, lược đồ trạng thái, giao thức truyền thông với BE và MCU. Thích hợp dùng làm chương "Thiết kế và triển khai phần mềm robot" trong báo cáo đồ án.

---

## 1. Tổng quan hệ thống

Robot vận hành theo kiến trúc phân tầng:

```
+--------------------+      REST + STOMP/WS      +-----------------------------+
|     Backend        | <-----------------------> |   Raspberry Pi (ROS1)       |
|   (Spring Boot)    |                           |   gói `new_robot`           |
+--------------------+                           +-----------------------------+
                                                         |            |
                                     57600 baud UART     |            | 9600 baud UART
                                                         v            v
                                                  +------------+ +------------+
                                                  |  ESP32     | |  Arduino   |
                                                  |  motor PID | |  LCD/keypad|
                                                  |  encoder   | |  khóa hộp  |
                                                  +------------+ +------------+
```

Hai "kênh song song" trên Pi:

- **Kênh điều khiển chuyển động**: `cmd_vel → cmd_vel_timeout → esp32_odom → ESP32 → encoder → /odom`. Làm việc độc lập với BE, chịu trách nhiệm an toàn (dừng khi mất cmd_vel).
- **Kênh nghiệp vụ & cảm biến**: `gps_publisher` + `imu_publisher` cung cấp `/fix`, `/imu/data`; `order_listener_sm` nhận đơn từ BE, đẩy PIN/LCD xuống Arduino; `update_location` đẩy vị trí robot ngược lên BE.

Điểm thiết kế đáng chú ý:
- **Pi chỉ làm high-level** (ROS, WebSocket, lập kế hoạch). Toàn bộ PID bám tốc độ bánh do ESP32 đảm nhiệm ở vòng 100 Hz, giúp Pi không bị nhiễu bởi jitter Linux.
- **Tách biệt kênh GPS (NMEA passive) với kênh AT** của SIM7600: module chỉ được dùng như bộ thu GPS thụ động, không cần AT command, giảm độ phức tạp khởi tạo.
- **IMU đọc raw register qua I2C (smbus2)** thay vì dùng `adafruit_bno055`/CircuitPython để bớt phụ thuộc môi trường Python trên Pi.
- **Mọi node tách file riêng, launch theo nhóm chức năng**; bringup có thể bật/tắt từng khối (`enable_gps`, `enable_imu`, `enable_lidar`, `enable_server`, `enable_navigation`).

---

## 2. Cấu trúc package `new_robot`

```
src/new_robot/
├── package.xml                # ROS package manifest (catkin)
├── CMakeLists.txt             # catkin_python_setup + catkin_install_python
├── setup.py                   # find_packages("src") — expose system & server
├── NODES.md                   # Reference: topic/message/param từng node
├── launch/
│   ├── main.launch
│   ├── full.launch            # bringup + optional navigation
│   ├── bringup.launch         # serial + gps + imu + server + lidar
│   ├── server.launch          # WS nodes + gps + arduino bridge
│   ├── gps.launch             # gps_publisher
│   ├── imu.launch             # imu_publisher
│   ├── serial_test.launch     # cmd_vel_timeout + esp32_odom + arduino
│   ├── lidar_xv11.launch      # XV-11 lidar (neato driver)
│   ├── lidar_custom.launch    # LDS-007 lidar + lidar_processor (DWA test)
│   └── navigation_dwa.launch  # move_base + costmaps + DWA
├── cfg/                       # tham số costmap/DWA cho move_base
└── src/                       # mã nguồn Python
    ├── system/                # top-level package `system`
    │   ├── ServerInterface.py
    │   ├── UpdateLocation.py
    │   ├── HardwareInterface.py
    │   ├── pubVelEncoderDiff.py
    │   ├── gps_publisher.py
    │   ├── imu_publisher.py
    │   ├── cmd_vel_fake.py
    │   ├── listen_orders.py
    │   └── lidar/
    │       ├── __init__.py
    │       ├── lidar_lds007_node.py
    │       ├── lidar_processor.py
    │       └── lds007_uart_reader.py   # giải mã packet 22 byte kiểu XV-11
    └── server/                # top-level package `server`
        ├── ws_client.py
        └── config_ws.py
```

Sơ đồ include launch:

```
main.launch
└── full.launch
    ├── bringup.launch
    │   ├── serial_test.launch     (cmd_vel_timeout, esp32_odom, arduino_bridge)
    │   ├── gps.launch              (nếu enable_gps)
    │   ├── imu.launch              (nếu enable_imu)
    │   ├── server.launch           (enable_gps=false, enable_arduino_bridge=false
    │   │                            để không double-launch)
    │   └── lidar_xv11.launch       (nếu enable_lidar)
    └── navigation_dwa.launch       (nếu enable_navigation)
```

---

## 3. Danh mục node và luồng topic

### Sơ đồ luồng tổng

```
                          /cmd_vel
                             │
                             ▼
 +---------------------+   (timeout 0.5s)   +---------------------+    cmd_vel_timeout
 |     move_base /     | ─────────────────► | cmd_vel_timeout     | ──────────────────┐
 |     teleop / user   |                    | (cmd_vel_fake.py)   |                   │
 +---------------------+                    +----------+----------+                   │
                                                       │ serial_ard_tx                │
                                                       │ (L_ON / R_ON)                ▼
                                                       │                    +-----------------+
                                                       │                    | esp32_odom      |
                                                       │                    |(pubVelEncoderDiff)|
                                                       │                    +--------+--------+
                                                       ▼                             │
                                              +-----------------+    serial           │
 order_listener_sm  ─ serial_ard_tx ─────────►| arduino_        | ◄──────────► Arduino Nano
 (UNLOCK / LCD)                               | interface       |              (LCD, khóa, đèn)
 /Status_robot ◄───────────────────────────── | (HardwareIntf)  |
                                              +-----------------+

 gps_publisher (ttyUSB3 NMEA) ── /fix ──► update_location ──HTTP──► BE
                                        └──► EKF (tương lai)

 imu_publisher (I2C BNO055) ── /imu/data ──► EKF (tương lai)

 BE ── STOMP ──► order_listener_sm ── /waypoints (đã tạm bỏ TF utm→map)
                                   └── UNLOCK / LCD → Arduino
```

### Bảng topic toàn cục

| Topic | Message type | Publisher | Subscriber | Mục đích |
|---|---|---|---|---|
| `/fix` | `sensor_msgs/NavSatFix` | `gps_publisher` | `update_location` (, EKF tương lai) | Vị trí GPS thô (WGS84) |
| `/imu/data` | `sensor_msgs/Imu` | `imu_publisher` | EKF (dành sẵn) | Quaternion + gia tốc + vận tốc góc |
| `/odom` | `nav_msgs/Odometry` | `esp32_odom` | move_base, EKF | Odometry từ encoder + TF `odom→base_link` |
| `/cmd_vel` | `geometry_msgs/Twist` | move_base / teleop | `cmd_vel_timeout` | Vận tốc yêu cầu |
| `/cmd_vel_timeout` | `geometry_msgs/Twist` | `cmd_vel_timeout` | `esp32_odom` | Vận tốc có safety-timeout |
| `/pid_config` | `geometry_msgs/Twist` | runtime (rostopic pub) | `esp32_odom` | Kp/Ki/Kd nóng cho ESP32 |
| `/speed_desired`, `/speed_feedback` | `std_msgs/Float32` | `esp32_odom` | debug | Kiểm chứng vòng PID |
| `MOTOR_ERROR` | `std_msgs/Bool` | `esp32_odom` | supervisor | Cờ lỗi động cơ |
| `/Status_robot` | `std_msgs/String` | `arduino_interface` | `order_listener_sm`, `arduino_interface` | Tín hiệu trạng thái FSM |
| `serial_ard_tx` | `std_msgs/String` | `order_listener_sm`, `cmd_vel_timeout` | `arduino_interface` | Hàng đợi lệnh text gửi Arduino |
| `/scan` | `sensor_msgs/LaserScan` | `xv11_lidar` hoặc `lidar_lds007` | `lidar_processor`, move_base | Quét 360° |
| `/scan_processed` | `sensor_msgs/LaserScan` | `lidar_processor` | debug, move_base | Quét đã lọc self-footprint |

---

## 4. Mô tả sâu từng node

### 4.1. `cmd_vel_timeout` — `cmd_vel_fake.py`

Node cầu nối cho `cmd_vel`, đảm bảo:

1. **Safety timeout**: nếu không nhận message `cmd_vel` trong 0.5 s, tự phát một `Twist = 0` để ESP32 biết dừng. Chỉ phát một lần, `has_published_zero` khóa lại cho đến khi có message mới.
2. **Forward không jitter**: khi có `cmd_vel`, publish lại nguyên văn sang `cmd_vel_timeout` ngay tức khắc (không đợi loop 20 Hz).
3. **Bật đèn tín hiệu theo hướng lái**:
   - Ngưỡng `angular_threshold = 0.1 rad/s`.
   - Nếu đi lùi (`linear.x < 0`), đảo dấu `angular.z` trước khi so sánh — vì đèn phụ thuộc hướng quay vật lý, không phải dấu toán học.
   - `angular.z > 0.1` → gửi `R_ON` (đèn phải), `< -0.1` → `L_ON` (trái).
   - Dùng bộ đếm `count_delay ≥ 30` để tránh spam xuống Arduino (~1 lần/0.5 s).

Node đóng vai trò **bộ chuyển vận tốc an toàn** theo kiểu watchdog-valve, một khái niệm cơ bản trong thiết kế robot autonomous: *bất kỳ nguồn `cmd_vel` nào cũng phải đi qua một nút có safety-timeout trước khi xuống phần cứng*.

### 4.2. `esp32_odom` — `pubVelEncoderDiff.py`

Node này là hạt nhân điều khiển chuyển động. Hai nhiệm vụ:

#### 4.2.1. Sinh vận tốc bánh từ Twist

Robot cấu hình vi sai (differential drive) 2 bánh truyền động + 2 bánh bị động, nhưng mảng `speed_desired[4]` giữ nguyên index 4 để tương thích code cũ. Công thức ICC (Instantaneous Center of Curvature):

```
v_left  = v_x * coeff_speed − ω * L / 2
v_right = v_x * coeff_speed + ω * L / 2
```

Trong đó `L = total_length = 52.89 cm` là khoảng cách trục bánh, `coeff_speed = 1.0` dành để tinh chỉnh thực nghiệm. `v_x` (m/s) được nhân 100 để đổi sang cm/s vì ESP32 làm việc ở đơn vị tick/quãng.

Sau đó `runRobot()` đóng gói thành chuỗi ASCII `"<v_left>/<v_right>;"` gửi qua UART 57600 baud, tức là **giao thức text line**. Ví dụ `"15.0/-5.0;"` nghĩa là bánh trái 15 cm/s, bánh phải lùi 5 cm/s. Không có checksum — chấp nhận vì kênh UART 50 cm, môi trường sạch.

#### 4.2.2. Odometry từ encoder

ESP32 gửi về chuỗi `"enc_left/enc_right;"` với encoder_total (uint16 mod 32768) hiện tại. Node:

1. **Xử lý wraparound** của encoder uint16 trong `NormalizeOverflow`: nếu `delta > 10000` hoặc `< −10000` thì cộng/trừ `32768` để khôi phục chênh lệch thực. Điều này cho phép bánh đi quãng dài mà không mất tick do overflow.
2. **Quy đổi tick sang mét**: `cmPerCount = π · D / N` với `D = 9.5 cm`, `N = 1798 tick/vòng` → `≈ 0.01659 cm/tick`.
3. **Tính tịnh tiến và xoay**:

   ```
   Δxy = (Δ_left + Δ_right) / 2                     # dịch chuyển tiến
   Δθ  = (Δ_left − Δ_right) / L                     # xoay (tính trên trục giữa)
   Δx  = cos(θ + Δθ/2) · Δxy
   Δy  = sin(θ + Δθ/2) · Δxy
   ```

   Đây là công thức **runge-kutta order 1 kiểu midpoint** (đánh giá hướng ở giữa khoảng) thay vì chỉ lấy `cos(θ)` — giảm sai số tích lũy khi xoay nhanh.

4. **Pose tích lũy** `(x, y, θ)` được wrap về `[−π, π]`.
5. **Lọc tốc độ tuyến tính** bằng IIR bậc 2:

   ```
   v_filt[k] = a · v_filt[k−1] + b · v[k] + b · v[k−1]
   ```
   với `a = 0.52188555`, `b = 0.23905722`. Hai hệ số này tạo bộ lọc thông thấp bậc 1 ~2 Hz (đã tune thực nghiệm).

6. **Publish `nav_msgs/Odometry`** với:
   - Pose: `(x, y, 0)` + quaternion từ yaw.
   - Twist: `linear.x = v_filt_x`, `angular.z = −v_filt_z` (đảo dấu vì convention trái dấu giữa ROS và code).
   - Covariance đã gán tay: vị trí `0.1 m²`, yaw `0.35 rad²` khi có xoay, `1e-4` khi đi thẳng, các trục không dùng đặt `1e6` (gần như vô tận) để EKF loại.
7. **Broadcast TF `odom → base_link`** tương ứng.

#### 4.2.3. PID runtime

Topic `/pid_config` (Twist) cho phép chỉnh Kp, Ki, Kd nóng — node pack thành chuỗi `"<Kp>:<Ki>#<Kd>;"` và gửi qua UART. ESP32 parse, reset integral, áp dụng vào vòng 100 Hz. Lợi ích: người vận hành có thể `rostopic pub /pid_config geometry_msgs/Twist "{linear: {x: 0.6, y: 0.05, z: 0.02}}"` để đo đáp ứng bước mà không cần re-flash firmware.

### 4.3. `imu_publisher` — `imu_publisher.py`

Driver BNO055 **không dùng CircuitPython**, làm việc trực tiếp với I2C qua `smbus2`.

#### 4.3.1. Khởi tạo chip

Trình tự trong `begin()` (theo datasheet BNO055):

1. Đọc `CHIP_ID = 0xA0` để xác nhận thiết bị.
2. Chuyển mode `OPR_CONFIG (0x00)`.
3. Soft reset bằng `SYS_TRIGGER |= 0x20`, chờ 700 ms rồi poll lại chip id.
4. Set `PWR_MODE = NORMAL (0x00)`, clear `SYS_TRIGGER`.
5. Set `UNIT_SEL = 0x00` (m/s², dps, deg, Android orientation).
6. Chuyển sang `OPR_NDOF (0x0C)` — chế độ fusion 9 trục (accel + gyro + mag) để lấy quaternion tuyệt đối có drift tối thiểu.

#### 4.3.2. Vòng đọc & publish

- Rate mặc định **100 Hz** để phù hợp EKF.
- Mỗi iteration đọc 3 block register:
  - `REG_QUAT (0x20, 8 bytes)`: quaternion `w, x, y, z` dạng Q14 (chia `2^14`).
  - `REG_GYR_DATA (0x14, 6 bytes)`: dps chia `16`, rồi đổi sang rad/s bằng `math.radians`.
  - `REG_LIN_ACC (0x28, 6 bytes)`: gia tốc **đã khử trọng lực**, đơn vị mg chia `100` → m/s².
- Chuẩn hóa quaternion: nếu `|q| ∉ (0.9, 1.1)` thì giữ nguyên `last_msg.orientation` (tránh output đột biến khi I2C có glitch). Nếu hợp lệ thì normalize về đơn vị.
- **Lock đa luồng** cho bus I2C (`threading.Lock`) để không cạnh tranh với các client khác trên cùng bus.
- Reconnect tự động: khi `OSError`, đóng bus, set `sensor = None`; vòng `run()` tự re-init mỗi lần rỗng.

#### 4.3.3. Covariance

Lấy từ calibration thực nghiệm trước đó của robot `nox` (phiên bản cũ). Đặt diag cho ma trận 3×3 của quaternion, gyro, accel. Các off-diagonal bỏ `0` vì chưa có dữ liệu chéo.

### 4.4. `gps_publisher` — `gps_publisher.py`

Driver GPS thụ động cho SIM7600X. Chỉ đọc, không gửi lệnh AT.

#### 4.4.1. Vấn đề thực tế với SIM7600

- Module enumerate **4 cổng ttyUSB** (0–3). Cổng `ttyUSB3` tự phát NMEA; cổng `ttyUSB2` là AT.
- Driver CDC của SIM7600 trên Linux không cho `TIOCMBIS` set DTR → pyserial raise `BrokenPipeError` khi mở bằng mặc định (vì pyserial cố DTR=True để "wake" modem).

Giải pháp trong `_open_serial()`:
- Tạo `Serial()` chưa open, set `dsrdtr=True`, `rtscts=False`, `xonxoff=False`.
- Nếu raise: tạo lại, gán `ser.dtr = None` và `ser.rts = None` (tín hiệu cho pyserial: "đừng động vào line này"), sau đó `open()`.
- Nếu vẫn raise nhưng `ser.is_open == True`, vẫn tiếp tục (port đã mở được, chỉ ioctl DTR thất bại — không ảnh hưởng đọc/ghi).

#### 4.4.2. Thuật toán đọc & parse

Hai luồng trong node:

- **Reader thread** (`_reader_loop`): vòng lặp đọc `ser.readline()`, chỉ giữ dòng bắt đầu `$` và chứa `GGA`, gọi `parse_gga`.
- **Publish loop** (`_publish_loop`): chạy rate `~rate_hz`, lấy snapshot `self.latest` đã protect bằng `Lock`, đóng gói `NavSatFix`.

Parser `parse_gga` + kiểm checksum NMEA XOR:

```
chk = 0
for ch in payload (giữa $ và *): chk ^= ord(ch)
if chk != int(two_hex_digits, 16): reject
```

Chuyển NMEA `ddmm.mmmm` / `dddmm.mmmm` sang decimal degrees: tách phần độ (2 hoặc 3 chữ số trước `ddmm`), cộng với `mm.mmmm / 60`, áp dấu theo `N/S/E/W`.

Nếu `fix_quality ∈ {"", "0"}` → NoFix; `status.status = STATUS_NO_FIX (-1)`, lat/lon/alt = `NaN`. Ngược lại `STATUS_FIX (0)`, `service = SERVICE_GPS (1)`. Covariance để `UNKNOWN` vì raw NMEA không báo HDOP xứng đáng đổi sang σ².

### 4.5. `order_listener_sm` — `ServerInterface.py`

Một state machine tương tác với BE qua STOMP WebSocket.

#### 4.5.1. Mô hình STOMP

`ServerService.listen_orders()`:
- Mở WebSocket native tới `ws_url`.
- Gửi frame `CONNECT` với header `robot-id` + `secret-key` (xác thực dùng HMAC tĩnh — secret share `DATN_2025_2_GIAP`).
- Gửi `SUBSCRIBE` tới destination `/topic/robot-order/{robotId}`.
- Vòng `while True`: nhận frame, parse JSON payload, map về `List[Order]`, gọi callback.
- Nếu disconnect: đóng, chờ `retry_delay_seconds = 5`, mở lại. Vòng này kết thúc khi `should_stop()` trả True.

Node chạy worker trên **thread riêng** (`_listen_worker`), thread chính chỉ `rospy.spin()`. Cờ `self.is_listening` + `self.state` làm đồng bộ.

#### 4.5.2. FSM

```
        ┌──────────────── STARTING / /Status_robot ───────┐
        │                                                 │
        ▼                                                 │
  ┌───────────┐  có đơn pending  ┌─────────┐              │
  │ LISTENING │ ────────────────►│ WAITING │──────────────┘
  └───────────┘                  └─────────┘
```

- **LISTENING**: thread đang mở WS, tiếp nhận đơn.
- **WAITING**: đã publish UNLOCK/LCD, tạm dừng nghe để robot đi giao hàng, chờ BE hoặc Arduino gửi `"STARTING"` qua `/Status_robot` để quay lại LISTENING.

#### 4.5.3. Xử lý đơn hàng

`handle_order_change(orders, payload, event_type)`:

1. Lọc `orders` có `status == "pending"`. Nếu không có đơn pending mà vẫn có `orders` — nghĩa là chỉ là status update → cập nhật LCD để hiển thị phase (giao/lấy/xong).
2. Lấy `pending_orders[0]`. Gọi:
   - `publish_unlock_pin(order)`: pad PIN lên 8 chữ số với `zfill(8)`. Dedupe bằng `last_published_order_id`, đảm bảo không gửi trùng lệnh UNLOCK cho cùng 1 đơn.
   - `publish_lcd_status(order)`: sinh 2 dòng text, dòng 1 là phase theo bảng trạng thái:
     ```
     pending/picking_up/assigned → "DI LAY DON"
     delivering/on_delivery      → "DI GIAO DON"
     delivered/done/completed    → "DA GIAO XONG"
     else                        → "DANG XU LY"
     ```
     Dòng 2 là tên người nhận, fallback `#<id>`.
3. Gọi `_ascii16(s)`:
   - Normalize NFKD để bóc dấu tiếng Việt.
   - Thay `|` (ký tự phân cách) thành `/`, loại `\r\n`.
   - Thay ký tự ngoài ASCII in-được (`32..126`) bằng `?`.
   - Cắt còn 16 ký tự.
4. Kết gói `LCD|<line1>|<line2>` → publish `serial_ard_tx`.

Lược đồ ký tự đảm bảo Arduino (chỉ hỗ trợ ASCII cơ bản trên HD44780) không gặp ký tự lạ gây lỗi LCD.

#### 4.5.4. Lưu ý về TF routing

Phiên bản hiện tại **đã bỏ** `_wait_and_get_static_transform` và `publish_waypoints_from_route`. Trước đây node chờ TF `utm → map` do `navsat_transform_node` tạo, sau đó convert mỗi `routePoint` từ lat/lon → UTM → map frame → publish `/waypoints`. Vì hệ thống chưa cần navigation map-frame (đang chạy GPS waypoint ngoài trời không map), phần này tạm cắt để giảm phụ thuộc và tránh loop warning. Khi tích hợp `robot_localization`, code có thể khôi phục từ git history.

### 4.6. `update_location` — `UpdateLocation.py`

Nhiệm vụ: đẩy vị trí robot lên BE theo chính sách "chỉ gửi khi di chuyển đủ xa".

Thuật toán:

1. `gps_callback`: nhận `/fix`. Chỉ cập nhật `latest_lat/lon` nếu `msg.status.status >= 0` (hợp lệ).
2. Mỗi `interval_seconds = 10s`, gọi `update_location_if_needed`:
   - Lấy robot đang lưu ở BE qua REST `GET /api/v1/robot/{id}/location` (bên trong `ServerService.get_robot_location`).
   - Nếu BE chưa có vị trí → gửi lần đầu.
   - Nếu có → tính **khoảng cách Haversine** giữa vị trí BE và vị trí hiện tại.
3. Nếu khoảng cách ≥ `max_distance_meters`, gọi `update_robot_location(lat, lon)` — một POST kèm HMAC body. `ServerService` mở REST session mới mỗi lần để tránh giữ socket dài.

Công thức Haversine:

```
φ1, φ2 = radians(lat1, lat2)
Δφ     = radians(lat2 − lat1)
Δλ     = radians(lon2 − lon1)
a      = sin²(Δφ/2) + cos(φ1) · cos(φ2) · sin²(Δλ/2)
c      = 2 · atan2(√a, √(1 − a))
d      = R · c      với R = 6_371_000 m
```

Ngưỡng `max_distance_meters` mặc định từ launch là `200` m — giá trị lớn này phục vụ test BE; khi triển khai thực nên giảm xuống `3–5` m để có dashboard trơn.

### 4.7. `arduino_interface` — `HardwareInterface.py`

Cầu nối giữa ROS và Arduino Nano, thực hiện 3 hành vi chính:

- **Forward text**: mọi message `std_msgs/String` xuống `serial_ard_tx` được ghép `"\n"` và gửi qua UART 9600 baud.
- **FSM đồng bộ với navigation**:
  ```
    ┌── "DOING" từ /Status_robot ──┐
    │                              ▼
  WAITING ──►  DOING ──►  SUCCESS ──►  WAITING
    ▲                        │          ▲
    │  Arduino reply "OK"    │          │
    │  (đơn đã lấy)          │  "SUCCESS" từ /Status_robot
    │                        ▼
    └── Arduino reply "OK" (đã giao xong)
  ```
  - Khi vào `DOING`, node đợi Arduino trả "OK" (xác nhận đã nhận PIN) rồi publish `"MOVING"` để node điều khiển bắt đầu di chuyển.
  - Khi vào `SUCCESS`, node ghi `L_ON\n` xuống Arduino để bật nam châm khóa cửa xe, rồi đợi Arduino trả "OK".
- **Non-blocking I/O** với `select.select`: tránh dùng thread riêng, vòng `spin()` vẫn 10 Hz, mỗi lần poll serial 10 ms. Cân bằng giữa độ trễ phản hồi và CPU usage.

Trước đây node còn "kiêm" driver SIM7600 gửi SMS (`send_sms`, `wait_for_module_ready`, `check_signal`). Đã tách bỏ vì dùng SIM thành GPS receiver, không cần SMS.

### 4.8. Lidar nodes

#### 4.8.1. `lidar_lds007_node` — `lidar_lds007_node.py`

Driver Python cho lidar **LDS-007** (gần giống packet format XV-11):

- **Packet format 22 byte**:
  ```
  byte  0: 0xFA header
  byte  1: index 0xA0..0xF9 (90 block, mỗi block 4°)
  byte  2..3: motor speed (speed_raw / 64 = RPM)
  byte  4..19: 4 measurement (4 byte/đo)
               dist_l | (dist_h_flags & 0x3F) << 8  (mm)
               bit 7 = invalid, bit 6 = warning
               intensity_l | intensity_h << 8
  byte 20..21: checksum 16-bit
  ```
  Checksum tính theo:
  ```
  chk = 0
  for b in byte[0..19]: chk = ((chk << 1) + b) & 0xFFFFFFFF
  return chk & 0x7FFF
  ```
  → so với `byte[20]|byte[21]<<8` đã mask `0x7FFF`.
- **Khởi động** cần gửi ASCII command `startlds$` xuống lidar MCU qua UART 115200. Driver:
  - Tắt DTR/RTS trước khi `open()` để không reset MCU qua bridge CP210x.
  - Chờ `boot_wait_s = 1.5s` cho MCU boot xong.
  - Gửi lệnh tối đa 3 lần, mỗi lần chờ 1 s quan sát `in_waiting`.
- **Generator `packets()`**: mỗi iteration đọc 256 byte, tìm `0xFA`, parse frame 22 byte, yield `Lds007Packet`. Nếu `idle_yield_s = 1s` trôi qua mà không có packet nào → yield `None` để consumer có thể watchdog.
- **Node ROS**: tích lũy 90 packet (= 360 điểm) rồi publish 1 `sensor_msgs/LaserScan` với:
  ```
  angle_min       = 0
  angle_max       = 2π
  angle_increment = 2π/360
  range_min       = 0.05 m
  range_max       = 6.0 m
  ranges          = [360 float]   ; inf nếu invalid/out-of-range
  intensities     = [360 float]
  ```
  Watchdog: nếu 3 s không có packet, log warning + gọi `send_start_command()` để re-kick motor.

#### 4.8.2. `lidar_processor` — `lidar_processor.py`

Hai vai trò:

1. **Self-filter + republish** `LaserScan → /scan_processed`:
   - Quy đổi polar sang Cartesian `(r cosθ + laser_offset_x, r sinθ + laser_offset_y)`.
   - Loại bỏ các điểm rơi vào bounding box của thân robot (`self_filter_x_min..max`, `self_filter_y_min..max`).
   - Các range non-finite hoặc < `range_min` được đổi thành `inf`.

2. **Lightweight DWA controller** (Dynamic Window Approach) cho chế độ test:

   **Bước A — Window vận tốc**:
   ```
   v_window = [max(0, v_cur − a_max·Δt), min(v_max, v_cur + a_max·Δt)]
   w_window = [max(−w_max, w_cur − α_max·Δt), min(w_max, w_cur + α_max·Δt)]
   ```
   với `Δt = sim_dt = 0.15 s`, `a_max = 0.25 m/s²`, `α_max = 1.8 rad/s²`. Tức là chỉ xét các `(v, w)` **khả thi về động lực học** trong bước tiếp theo.

   **Bước B — Sinh quỹ đạo**: lấy `linear_samples = 6` giá trị `v`, `angular_samples = 21` giá trị `w`. Với mỗi cặp, tích phân theo uniform kinematics trong `prediction_time = 1.5 s`:
   ```
   for k = 1..N:
       x += v · cos(yaw) · Δt
       y += v · sin(yaw) · Δt
       yaw += w · Δt
   ```

   **Bước C — Khoảng cách an toàn**:
   - Với mỗi trạng thái trên quỹ đạo, tính `min_distance − robot_radius` tới đám mây điểm.
   - Nếu `< safety_margin = 0.08 m`, loại bỏ quỹ đạo.

   **Bước D — Hàm mục tiêu**:
   ```
   score = 2.6·end_x           # ưu tiên tiến xa về phía trước
         + 1.8·clearance        # ưu tiên xa vật cản
         + 1.0·v               # thưởng tốc độ
         − 0.7·|w|             # phạt quay
         − 0.4·|yaw_end|       # phạt lệch hướng
         − 0.6·|end_y|         # phạt trôi ngang
   ```
   Khi `front_clearance < slow_down_distance`, trừ tiếp `3.0 · max(0, v − 0.65 · v_cruise)` để buộc giảm tốc gần vật cản.

   **Bước E — Escape**: nếu tất cả quỹ đạo đều vi phạm `safety_margin` → quay tại chỗ về phía có `sector_clearance` lớn hơn với `escape_angular_speed = 0.8 rad/s`.

   **Bước F — Emergency stop**: nếu `front_clearance < emergency_stop_distance = 0.42 m`, buộc `v = 0`; chỉ giữ `w` (đổi hướng) từ kết quả trên.

   **Sector clearance** được định nghĩa: với tập điểm `(x, y)` sau self-filter, lấy các điểm có góc `atan2(y, x)` nằm trong cung `[α_min, α_max]`, trả `min(√(x²+y²))`. Có 3 sector: front (`±35°`), left (`15..120°`), right (`−120..−15°`).

   **Plot**: nếu `plot=true` và có `DISPLAY`, matplotlib vẽ XY scatter điểm lidar + quỹ đạo dự đoán + heading, refresh 10 Hz — cực hữu ích để debug thuật toán.

### 4.9. `listen_orders.py`

Utility CLI, không phải node production, chỉ gọi `ServerService.listen_orders` để in đơn ra stdout. Dùng để test BE→Pi.

---

## 5. Giao thức truyền thông

### 5.1. Pi ↔ Backend (Spring Boot)

Hai kênh song song:

- **WebSocket native** (`/ws-delivery-native`) dùng giao thức STOMP tối giản. Tại sao "native" và không dùng SockJS: client Python (`websocket-client`) không hỗ trợ SockJS handshake, BE phải expose endpoint riêng. Xác thực: header `robot-id` + `secret-key` trong frame CONNECT.
- **REST** (`/api/v1/robot/*`) cho các thao tác đồng bộ: `get_robot_location`, `update_robot_location`. Mỗi gọi mở session mới → stateless.

Destination STOMP:

| Direction | Destination | Payload |
|---|---|---|
| BE → Pi | `/topic/robot-order/{robotId}` | JSON `{type, data: {orders, robot}}` — `orders[i]` gồm `pinCode`, `routePoints`, `status`, `receiverName`... |
| Pi → BE | `/app/update-location` | `{robotId, lat, lng}` |

### 5.2. Pi ↔ ESP32 (motor)

UART **57600 baud, 8N1**, không checksum (kênh ngắn, môi trường sạch). Dùng text line kết thúc `;`:

| Pi → ESP32 | Ý nghĩa |
|---|---|
| `"<v_left>/<v_right>;"` | Set tốc độ bánh (cm/s). `-` âm = lùi. |
| `"<Kp>:<Ki>#<Kd>;"` | Reload tham số PID. |

| ESP32 → Pi | Ý nghĩa |
|---|---|
| `"<enc_left>/<enc_right>;"` | Encoder cumulative (uint16 mod 32768). |

ESP32 chạy vòng PID 100 Hz, bản thân nó thực thi bão hòa PWM. Chi tiết firmware trong `MCU/ESP32/src/src.ino` (nằm ngoài phạm vi tài liệu này).

### 5.3. Pi ↔ Arduino Nano (LCD, khóa)

UART **9600 baud, 8N1**, text line kết thúc `\n`:

| Pi → Arduino | Ý nghĩa |
|---|---|
| `UNLOCK <8digit>` | Nạp PIN mới vào EEPROM tạm, sẵn sàng so sánh với keypad. |
| `LCD\|<line1>\|<line2>` | Ghi 2 dòng lên LCD 16×2 (line ≤ 16 ký tự ASCII). |
| `L_ON` | Bật nam châm khóa hộp giao hàng. |

| Arduino → Pi | Ý nghĩa |
|---|---|
| `OK` | Xác nhận đã xử lý lệnh trước đó. |

### 5.4. Pi ↔ SIM7600 (GPS passive)

UART **115200 baud**, chỉ đọc, NMEA 0183. Không gửi AT. Module enumerate 4 cổng ttyUSB; chọn ttyUSB3 là cổng stream NMEA. Câu sử dụng: **`$GPGGA`** (hoặc tương đương Beidou/Glonass) — chứa lat, lon, fix quality, altitude, #sats, HDOP.

### 5.5. Pi ↔ BNO055 (IMU I2C)

I2C bus 1, 400 kHz, địa chỉ `0x29` (ADR tied to VCC). Register map đầy đủ trong datasheet. Node `imu_publisher` mở bus qua `smbus2.SMBus(1)`.

### 5.6. Pi ↔ LDS-007 (Lidar UART)

UART **115200 baud, 8N1**, bridge qua CP210x. Lệnh khởi động `startlds$` (ASCII). Packet 22 byte như mô tả mục 4.8.1.

---

## 6. Tham số launch quan trọng

```
# bringup/full
enable_server   = true   # order_listener_sm + update_location
enable_gps      = true   # gps_publisher
enable_imu      = true   # imu_publisher
enable_lidar    = false  # lidar + XV-11 driver
enable_navigation = false  # move_base

ws_url          = ws://<ip>:8080/ws-delivery-native
api_base_url    = http://<ip>:8080/api/v1/robot
secret_key      = DATN_2025_2_GIAP

esp32_baud      = 57600
arduino_baud    = 9600
wheel_diameter  = 9.5        (cm)
encoder_total   = 1798       (tick/rev)

gps_port        = /dev/ttyUSB3
gps_baud        = 115200
imu_bus         = 1
imu_address     = 0x29
imu_rate_hz     = 100.0
```

Chi tiết thêm (DWA navigation ngoài scope node): costmap inflation `0.2285 m`, footprint `1.0 × 0.2 m`, `max_vel_x = 0.14 m/s`, `max_vel_theta = 0.6 rad/s`, `xy_goal_tolerance = 0.15 m`, `yaw_goal_tolerance = 0.22 rad` — xem `cfg/*.yaml`.

---

## 7. Tổng kết thuật toán đã dùng

| Module | Thuật toán / kỹ thuật |
|---|---|
| `esp32_odom` | Differential-drive kinematics (Runge-Kutta midpoint), IIR bậc 2 lọc vận tốc, uint16 encoder wraparound correction |
| `imu_publisher` | BNO055 fusion NDOF (ngầm chạy trên chip), chuẩn hóa quaternion, reconnect bus I2C |
| `gps_publisher` | NMEA GGA parser + checksum XOR, passive reader, DTR bypass cho CP-CDC |
| `lidar_lds007_node` | XV-11-like frame parsing, custom `((chk<<1)+b) & 0x7FFF` checksum, watchdog auto-restart |
| `lidar_processor` | Self-filter bounding box, DWA (dynamic window + trajectory rollout + scored cost function + escape behavior + emergency stop) |
| `order_listener_sm` | STOMP subscribe + retry, FSM LISTENING/WAITING, ASCII16 diacritic-strip |
| `update_location` | Haversine distance + dead-band (gửi khi Δ ≥ threshold) |
| `cmd_vel_timeout` | Safety watchdog (zero-Twist sau 0.5 s), turn-signal hysteresis + đếm throttle |
| `arduino_interface` | Non-blocking select I/O, FSM đồng bộ nav ↔ lock |

---

## 8. Hướng mở rộng

- Tích hợp `robot_localization` (EKF) nhận `/odom` + `/imu/data` + `/fix` → publish `/odometry/filtered` + TF `map → odom`.
- Khôi phục `publish_waypoints_from_route` kèm `navsat_transform_node` để chuyển route GPS sang frame `map` cho `move_base`.
- Thêm sanity check HDOP trong `gps_publisher` và populate `position_covariance` theo HDOP² × (UERE)².
- Unit test cho parser NMEA/LDS-007 (dễ vì không phụ thuộc phần cứng).
- Supervisor node subscribe `MOTOR_ERROR`, `/imu/data` (detect fall), `/scan` (detect bumper contact) — chuyển sang emergency stop qua `cmd_vel_timeout`.
