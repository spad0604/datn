import cv2

# Khởi tạo camera
cap = cv2.VideoCapture(0)

# Khởi tạo bộ trích xuất ORB
orb = cv2.ORB_create(nfeatures=500)

# Khởi tạo bộ khớp điểm Brute-Force Matcher dựa trên khoảng cách Hamming (chuẩn của ORB)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

ret, prev_frame = cap.read()
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
# Tìm keypoints và descriptors cho khung hình đầu tiên
kp_prev, des_prev = orb.detectAndCompute(prev_gray, None)

print("Di chuyển camera từ từ để xem các đường line nối các điểm đặc trưng giữa 2 khung hình.")
print("Bấm 'q' để thoát.")

while True:
    ret, curr_frame = cap.read()
    if not ret:
        break
        
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    
    # Tìm keypoints và descriptors cho khung hình hiện tại
    kp_curr, des_curr = orb.detectAndCompute(curr_gray, None)
    
    # Đảm bảo có đủ descriptors để match
    if des_prev is not None and des_curr is not None and len(des_prev) > 0 and len(des_curr) > 0:
        # Match descriptors giữa 2 khung hình
        matches = bf.match(des_prev, des_curr)
        
        # Sắp xếp các matches theo khoảng cách (điểm nào giống nhau nhất thì xếp lên đầu)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Chỉ vẽ 50 matches tốt nhất để màn hình đỡ rối
        img_matches = cv2.drawMatches(prev_frame, kp_prev, curr_frame, kp_curr, matches[:50], None, 
                                      flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        
        cv2.imshow("ORB Tracking: Previous Frame vs Current Frame", img_matches)
    else:
        cv2.imshow("ORB Tracking: Previous Frame vs Current Frame", curr_frame)

    # Cập nhật khung hình cũ bằng khung hình mới cho vòng lặp tiếp theo
    prev_frame = curr_frame.copy()
    kp_prev = kp_curr
    des_prev = des_curr

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()