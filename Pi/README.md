# Raspberry Pi Bridge Base (Python)

Base project cho Raspberry Pi với 3 tầng giao tiếp:
- HTTP GET API
- WebSocket (client tới server + local WebSocket endpoint để debug)
- UART (kết nối MCU)

## 1) Cài đặt

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## 2) Cấu hình môi trường

Tạo file `.env` (hoặc set biến môi trường) theo mẫu:

```env
HTTP_HOST=0.0.0.0
HTTP_PORT=8080
UART_PORT=COM3
UART_BAUDRATE=115200
WS_SERVER_URL=ws://localhost:9000/ws
WS_RECONNECT_SEC=3
```

Gợi ý trên Raspberry Pi (Linux): `UART_PORT=/dev/ttyAMA0` hoặc `/dev/serial0`.

## 3) Chạy

```bash
python main.py
```

## 4) Endpoint chính

- `GET /health`: trạng thái thành phần
- `GET /state`: snapshot dữ liệu gần nhất
- `GET /mcu/send?data=...`: gửi chuỗi xuống UART
- `GET /ws/send?data=...`: gửi dữ liệu lên remote WebSocket server
- `WS /ws/local`: WebSocket local để monitor realtime

## 5) Luồng dữ liệu mặc định

- UART RX -> cập nhật state + broadcast local WS + forward lên remote WS
- Remote WS RX -> cập nhật state + broadcast local WS

Bạn có thể tùy biến thêm rule forward trong `src/pi_base/bridge_app.py`.
