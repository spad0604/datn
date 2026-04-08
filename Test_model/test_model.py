import cv2
import numpy as np
import os # Import thêm thư viện này để kiểm tra đường dẫn

video_path = 'D:/DATN/Test_model/test_2.mp4'

# TRẠM KIỂM SOÁT 1: File có thực sự tồn tại ở đường dẫn này không?
if not os.path.exists(video_path):
    print(f"LỖI: Không tìm thấy file tại đường dẫn: {video_path}")
    print("Gợi ý: Kiểm tra xem file có bị đặt tên thành test.mp4.mp4 không!")
    exit()

# 1. Khởi tạo Video
cap = cv2.VideoCapture(video_path)

# TRẠM KIỂM SOÁT 2: OpenCV có mở được video không?
if not cap.isOpened():
    print("LỖI: Tìm thấy file nhưng OpenCV không thể mở (Lỗi codec hoặc file hỏng).")
    exit()

orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

cur_R = np.eye(3)
cur_t = np.zeros((3, 1))

# Đọc frame đầu tiên
ret, prev_frame = cap.read()

# TRẠM KIỂM SOÁT 3: Có đọc được frame hình ảnh nào không?
if not ret or prev_frame is None:
    print("LỖI: Mở được video nhưng không thể đọc frame đầu tiên (Video có thể rỗng).")
    exit()

# Tạo cửa sổ trước để tránh trường hợp không update UI do các nhánh `continue`
cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)

frame_counter = 0

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
kp1, des1 = orb.detectAndCompute(prev_gray, None)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print(f"🎬 Video đã kết thúc (hoặc không thể đọc tiếp) ở frame thứ {frame_counter}.")
        break
    
    frame_counter += 1
    
    if frame_counter < 3000:
        continue
    
    frame = cv2.resize(frame, (640, 480))
    
    curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Mặc định hiển thị frame thô; nếu tính được VO thì vẽ overlay lên.
    vis = frame.copy()

    # Tìm keypoints và descriptors cho frame hiện tại
    kp2, des2 = orb.detectAndCompute(curr_gray, None)
    
    # Kiểm tra nếu không tìm thấy descriptor nào (ví dụ: màn hình đen/trắng hoàn toàn)
    # Vẫn phải gọi imshow/waitKey để cửa sổ được update.
    if des1 is None or des2 is None:
        kp1, des1 = kp2, des2
        cv2.imshow('Frame', vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue
        
    matches = bf.match(des1, des2)
    
    # -------------------------------------------------------------
    # THÊM ĐOẠN GUARD CLAUSE NÀY VÀO ĐỂ FIX LỖI:
    # Yêu cầu ít nhất 8 cặp điểm để thuật toán RANSAC hoạt động ổn định
    if len(matches) < 8:
        print(f"Cảnh báo: Chỉ tìm thấy {len(matches)} matches. Bỏ qua frame này...")
        # Cập nhật frame hiện tại thành frame trước đó để đối chiếu với frame tiếp theo
        kp1, des1 = kp2, des2 
        cv2.imshow('Frame', vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue
    # -------------------------------------------------------------
    
    # Lấy toạ độ keypoints đã khớp
    pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])
    
    # Tính toán ma trận Essential
    E, mask = cv2.findEssentialMat(pts2, pts1, focal=718.8, pp=(607, 185), method=cv2.RANSAC, prob=0.999, threshold=1.0)
    
    # Kiểm tra thêm trường hợp E trả về None hoặc kích thước không chuẩn
    if E is None or E.shape != (3, 3):
        print("Cảnh báo: Không thể tính toán ma trận Essential hợp lệ.")
        kp1, des1 = kp2, des2
        cv2.imshow('Frame', vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # Khôi phục R và t từ ma trận Essential
    _, R, t, mask_pose = cv2.recoverPose(E, pts2, pts1, focal=718.8, pp=(607, 185))
    
    # Cộng dồn chuyển động
    cur_t = cur_t + cur_R.dot(t)
    cur_R = R.dot(cur_R)
    
    # Hiển thị kết quả
    inlier_mask = None
    if mask is not None:
        inlier_mask = mask.ravel()

    for i, m in enumerate(matches):
        # Kiểm tra xem mask có tồn tại và điểm đó có phải inlier không
        if inlier_mask is not None and len(inlier_mask) > i and int(inlier_mask[i]) == 1:
            pt1 = (int(kp1[m.queryIdx].pt[0]), int(kp1[m.queryIdx].pt[1]))
            pt2 = (int(kp2[m.trainIdx].pt[0]), int(kp2[m.trainIdx].pt[1]))
            cv2.circle(vis, pt2, 5, (0, 255, 0), -1)
            cv2.line(vis, pt1, pt2, (255, 0, 0), 2)
    
    # Show FPS
    if frame_counter > 1:
        fps = cap.get(cv2.CAP_PROP_FPS)
        cv2.putText(vis, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    # imshow true size not full screen
    cv2.resizeWindow('Frame', 640, 480)
    cv2.imshow('Frame', vis)
    
    # Cập nhật kp1, des1 cho vòng lặp tiếp theo
    kp1, des1 = kp2, des2

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()