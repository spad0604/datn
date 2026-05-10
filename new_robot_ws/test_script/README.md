# test_script

Chương trình test độc lập cho từng module phần cứng, không phụ thuộc ROS.
Chạy trực tiếp bằng `python3` trên Raspberry Pi để kiểm tra kết nối/đọc dữ liệu trước khi đưa lên ROS node.

## 1. BNO055 (IMU 9-DoF qua I2C)

```bash
pip install smbus2
python3 test_bno055.py                      # mặc định bus=1, addr=0x29, 10Hz
python3 test_bno055.py --address 0x28 --rate 20
```

Đầu ra: Euler (heading/roll/pitch), quaternion, linear accel, gyro, nhiệt độ,
trạng thái calibration (S/G/A/M mỗi giá trị 0-3, 3 là đã calib xong).

Nối dây (khớp với robot hiện tại - ADR kéo lên VCC nên addr = 0x29):
- VIN -> 3V3, GND -> GND
- SDA -> GPIO2 (pin 3), SCL -> GPIO3 (pin 5)
- ADR -> VCC (0x29, mặc định). Nếu ADR xuống GND thì đổi sang --address 0x28.

Kiểm tra I2C thấy thiết bị:
```bash
sudo i2cdetect -y 1
```

## 2. SIM7600X (GPS qua UART)

```bash
pip install pyserial
# ttyUSB3 stream sẵn NMEA (không nhận AT) — parse ra lat/lon:
python3 test_sim7600.py --port /dev/ttyUSB3
# ttyUSB2 là cổng AT (nếu mở được) — poll AT+CGPSINFO:
python3 test_sim7600.py --port /dev/ttyUSB2
# Ép mode nếu cần:
python3 test_sim7600.py --port /dev/ttyUSB3 --mode nmea_parsed
python3 test_sim7600.py --port /dev/ttyUSB3 --mode nmea           # in NMEA thô
python3 test_sim7600.py --port /dev/ttyUSB2 --mode cgpsinfo
```

Mặc định mode `auto`: gửi `AT` thử, nếu có `OK` thì poll `AT+CGPSINFO`, nếu không
thì chuyển sang parse NMEA thụ động (thích hợp cho `/dev/ttyUSB3`).

Lưu ý:
- SIM7600 HAT enumerate 4 cổng USB. `/dev/ttyUSB2` thường là AT, `/dev/ttyUSB3`
  là NMEA stream.
- Driver USB-CDC của SIM7600 trên Pi hay báo `BrokenPipeError` khi pyserial set
  DTR. Script đã tự né: mở với `dsrdtr=True` và không toggle DTR/RTS.
- Nếu chạy qua GPIO UART thì thường là `/dev/ttyS0` hoặc `/dev/ttyAMA0`, nhớ
  `sudo raspi-config` tắt serial console.
