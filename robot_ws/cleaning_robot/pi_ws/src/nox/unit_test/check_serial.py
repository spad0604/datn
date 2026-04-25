import serial
import time

# Thay đổi cổng và baudrate cho phù hợp với thiết bị của bạn
PORT = '/dev/ttyACM0'    # Hoặc '/dev/ttyUSB0' tùy cổng nào đúng
BAUDRATE = 9600          # Thử 115200 nếu 9600 không hoạt động

try:
    # Mở cổng serial
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # Đợi thiết bị ổn định (đặc biệt quan trọng với CH340/CP210x và Arduino)

    print(f"Đã mở cổng {PORT} với baudrate {BAUDRATE}")
    
    # Giữ lệnh L_ON
    command = "L_ON\r\n"  # Nhiều thiết bị cần \r\n ở cuối (CR+LF)
    # Nếu thiết bị chỉ cần \n thì dùng: "L_ON\n"
    # Nếu không cần gì thì dùng: "L_ON"

    ser.write(command.encode('utf-8'))  # Gửi lệnh
    print(f"Đã gửi lệnh: {command.strip()}")

    # Đọc phản hồi từ thiết bị (nếu có)
    time.sleep(0.5)  # Đợi một chút để thiết bị phản hồi
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"Phản hồi: {response}")
    else:
        print("Không có phản hồi (có thể bình thường)")

    # Đóng cổng
    ser.close()
    print("Đã đóng cổng serial.")

except serial.SerialException as e:
    print(f"Lỗi mở cổng serial: {e}")
    print("Kiểm tra lại cổng (ls /dev/ttyUSB*), quyền truy cập (sudo?), hoặc cổng đang bị chiếm bởi screen/minicom")
except Exception as e:
    print(f"Lỗi khác: {e}")