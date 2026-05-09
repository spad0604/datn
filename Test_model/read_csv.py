import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Đường dẫn đến file CSV của bạn
csv_file = 'out.csv'

def animate(i):
    try:
        # Đọc dữ liệu từ CSV
        data = pd.read_csv(csv_file)
        
        if data.empty:
            return

        # Lọc bỏ các điểm invalid (invalid == 1) hoặc khoảng cách bằng 0
        valid_data = data[data['invalid'] == 0]
        
        angles = np.deg2rad(valid_data['angle_deg'])
        distances = valid_data['distance_mm']

        # Xóa frame cũ để vẽ frame mới
        ax.clear()
        
        # Vẽ các điểm laser (dùng màu sắc theo khoảng cách để dễ nhìn)
        sc = ax.scatter(angles, distances, c=distances, s=10, cmap='plasma', alpha=0.75)
        
        # Cấu hình hiển thị radar
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_title(f"Lidar Live Scan (RPM: {data['rpm'].iloc[-1]})", va='bottom')
        
        # Giới hạn khoảng cách hiển thị (ví dụ 5000mm = 5m)
        # Bạn có thể bỏ dòng này nếu muốn tự động scale
        ax.set_rmax(5000) 
        
    except Exception as e:
        print(f"Waiting for data or error: {e}")

# Thiết lập cửa sổ vẽ
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='polar')

# Tạo hiệu ứng hoạt họa (cập nhật mỗi 200ms)
ani = FuncAnimation(fig, animate, interval=200, cache_frame_data=False)

plt.tight_layout()
plt.show()