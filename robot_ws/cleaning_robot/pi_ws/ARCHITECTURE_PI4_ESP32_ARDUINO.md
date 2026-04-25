# Kien truc dieu khien robot (Pi4 + ESP32 + Arduino)

## 1) Muc tieu tai lieu
Tai lieu nay tom tat kien truc thuc te trong source hien co:
- Pi4 chay ROS Noetic va cac node dieu huong/dieu khien.
- ESP32 (hoac firmware tuong tu) xu ly dong co + encoder qua serial.
- Arduino (module I/O phu: khoa, den, trang thai...) giao tiep serial rieng.

Luu y: mot phan logic vi dieu khien co dau hieu khong co source day du trong repo (chi thay diem giao tiep).

## 2) So do tong quan

```text
[Firebase/Server]
      |
      v
[server/ServerInterface.py] ---> /waypoints ---> [nox/MovingServer.py] --- move_base goal ---> [move_base]
                                      |                                      |
                                      | /Status_robot (DOING/MOVING/SUCCESS)|
                                      v                                      v
                             [nox/HardwareInterface.py]                /cmd_vel
                                      |                                      |
                                      | serial /dev/arduino (9600)          |
                                      v                                      v
                                 [Arduino board] <--- serial_ard_tx --- [nox/cmd_vel_fake.py]

/cmd_vel_timeout ----------------------------------------------> [nox/pubVelEncoderDiff.py]
                                                                  |
                                                                  | serial /dev/esp32 (57600)
                                                                  v
                                                               [ESP32 motor fw]
                                                                  |
                                                                  | encoder feedback
                                                                  v
                                                            /odom -> EKF (robot_localization)

Sensors:
- LiDAR: /dev/lidar -> xv_11_laser_driver
- IMU BNO055: imu.py publish /imu/data
- GPS: nmea_navsat_driver (/dev/ttyUSB3)
```

## 3) Thanh phan chinh va vai tro

### 3.1 Pi4 (ROS side)
- Bringup chinh: `pi_ws/src/nox/launch/nox_bringup_tf.launch`
- Node quan trong:
  - `nox/pubVelEncoderDiff.py`: cau serial voi ESP, gui lenh toc do va nhan encoder, tinh odom.
  - `nox/cmd_vel_fake.py`: tao topic `cmd_vel_timeout` (timeout an toan), dong thoi phat lenh den qua `serial_ard_tx`.
  - `nox/HardwareInterface.py`: FSM giao tiep Arduino (+ SIM neu bat).
  - `nox/MovingServer.py`: FSM dieu huong waypoint qua `move_base`.
  - `server/ServerInterface.py`: nhan don Firebase, convert route -> waypoint ROS.
  - `imu/imu.py`: publish `/imu/data`.

### 3.2 ESP32 (motor + encoder)
- Diem giao tiep ro rang tren Pi:
  - Port mac dinh: `/dev/esp32`
  - Baud: `57600`
  - Node giao tiep: `nox/pubVelEncoderDiff.py`
- Firmware co trong repo:
  - `src/src.ino` + `src/config.h`
  - Co parser serial nhan lenh speed va gui odom encoder.

### 3.3 Arduino (I/O phu)
- Diem giao tiep ro rang tren Pi:
  - Port mac dinh: `/dev/arduino`
  - Baud: `9600`
  - Node giao tiep: `nox/HardwareInterface.py`
- Lenh duoc gui xuong Arduino:
  - `UNLOCK <8-digit>`
  - `L_ON`, `R_ON`
- Arduino tra ve `OK` de cho phep chuyen state tren Pi.

## 4) Giao thuc serial xac dinh duoc

### 4.1 Pi -> ESP32
Dinh dang lenh toc do (tu `pubVelEncoderDiff.py`):

```text
<left_speed>/<right_speed>;
```

Vi du:

```text
12/-8;
```

### 4.2 ESP32 -> Pi
Dinh dang encoder tong (tu `src.ino` ham `send_odom()`):

```text
<L_up>/<L_down>&<R_up>*<R_down>;
```

Vi du:

```text
123/120&130*129;
```

### 4.3 Pi -> Arduino
Qua `HardwareInterface.py` va `cmd_vel_fake.py`:

```text
UNLOCK 12345678
L_ON
R_ON
```

### 4.4 Arduino -> Pi
- Ky vong phan hoi then chot: `OK`
- `HardwareInterface.py` dung `OK` de doi state:
  - `DOING` + `OK` -> publish `MOVING`
  - `SUCCESS` + `OK` -> quay lai `WAITING`

## 5) Luong dieu khien robot (end-to-end)

1. Server day route (Firebase) -> `ServerInterface.py` publish `/waypoints`.
2. `MovingServer.py` nhan waypoint, publish status `DOING`.
3. `HardwareInterface.py` thay `DOING` -> gui `UNLOCK ...` cho Arduino.
4. Arduino tra `OK` -> `HardwareInterface.py` publish `MOVING`.
5. `MovingServer.py` nhan `MOVING` -> bat dau gui goal cho `move_base`.
6. Navigation xuat `/cmd_vel` -> `cmd_vel_fake.py` -> `/cmd_vel_timeout`.
7. `pubVelEncoderDiff.py` doi `/cmd_vel_timeout` thanh speed wheel, gui qua serial cho ESP.
8. ESP gui encoder tong ve Pi; `pubVelEncoderDiff.py` tinh odom va publish `/odom`.
9. EKF hop nhat `/odom` + `/imu/data` -> `odometry/filtered/local`.
10. Khi den diem cuoi, `MovingServer.py` publish `SUCCESS`; `HardwareInterface.py` gui lenh ket thuc xuong Arduino.

## 6) Dau hieu phan "binary/khong co source"

1. Khong tim thay source firmware Arduino xu ly cac lenh `UNLOCK/L_ON/R_ON` trong repo hien tai.
2. Source ESP co (`src/src.ino`) nhung luong Arduino I/O dường như nam o board khac va khong co file `.ino` tuong ung.
3. Co tham chieu launch `nox_bringup_thinh.launch` trong `nox_navigation_teb_pi.launch` nhung file nay khong co trong thu muc launch -> co the nam ngoai repo hoac da dong goi khac.

## 7) Vi tri can check khi trien khai tren Pi

- Device serial hien tai:
  - `ls -l /dev/ttyUSB* /dev/ttyACM* /dev/ttyAMA0 /dev/ttyS0`
- Udev/quyen port:
  - `pi_ws/uart.sh` dang tao rule quyen, NHUNG chua tao symlink `/dev/esp32` va `/dev/arduino` (chi co comment mau).
- Port trong launch/param:
  - ESP: tham so `port` cua `pubVelEncoderDiff.py`
  - Arduino: tham so `~port_arduino` cua `HardwareInterface.py`

## 8) Ket luan nhanh

- Kien truc hien tai tach 2 kenh serial:
  - Kenh 1 (ESP32): dong co + encoder + odom.
  - Kenh 2 (Arduino): lenh I/O/trang thai theo FSM giao hang.
- Luong dieu khien chinh duoc dong bo bang topic `/Status_robot` giua `MovingServer.py` va `HardwareInterface.py`.
- Co kha nang dung binary/firmware ngoai repo cho Arduino I/O vi khong thay source tuong ung trong workspace.
