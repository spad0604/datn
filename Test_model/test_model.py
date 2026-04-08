import cv2
import numpy as np
import os
import time

# ==========================================
# CẤU HÌNH THÔNG SỐ
# ==========================================
VIDEO_PATH = 'D:/DATN/Test_model/test_4.mp4'
START_FRAME = 0  # Frame bắt đầu chạy

# Chế độ chạy
# DEBUG_VIS=True: hiển thị khung hình + vẽ mũi tên/match để debug
# DEBUG_VIS=False: tắt toàn bộ GUI/vẽ để tối ưu tốc độ trên Edge
DEBUG_VIS = True

USE_SIDE_REGIONS = False
SIDE_REGION_FRAC = 1.0 / 3.0  

TREND_EMA_ALPHA = 0.85  
ARROW_SCALE_PX = 120    
ARROW_COLOR = (0, 0, 255)
ARROW_THICKNESS = 4
ARROW_TIP_LENGTH = 0.25

# Cấu hình feature/matching
ORB_NFEATURES = 800
RATIO_TEST = 0.75
MIN_MATCHES = 8

# Scale cho recoverPose(t): bắt buộc có nguồn ngoài để ra đơn vị mét thực.
# Nếu có tốc độ từ encoder/odometry, điền ODOM_SPEED_MPS.
ODOM_SPEED_MPS = None
# Hoặc đặt cố định khi test (ví dụ 0.03 m/frame). None = chưa có scale thực.
FIXED_SCALE_PER_FRAME_M = None

PRINT_FPS_EVERY_N_FRAMES = 30

# Kích thước xử lý/hiển thị
PROCESS_WIDTH = 640
PROCESS_HEIGHT = 480
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600

# Camera intrinsics + tham số ước lượng Essential matrix
CAMERA_FOCAL_PX = 718.8
CAMERA_PP = (607.0, 185.0)
ESSENTIAL_METHOD = cv2.RANSAC
ESSENTIAL_PROB = 0.999
ESSENTIAL_THRESHOLD = 1.0

# ==========================================
# CÁC HÀM PHỤ TRỢ (GIỮ NGUYÊN TỪ CỦA BẠN)
# ==========================================
def _filter_matches_side_regions(kp_a, kp_b, matches, frame_width, side_frac=1.0 / 3.0):
    if frame_width is None or frame_width <= 0:
        return matches
    left_x = frame_width * side_frac
    right_x = frame_width * (1.0 - side_frac)
    kept = []
    for m in matches:
        x1 = kp_a[m.queryIdx].pt[0]
        x2 = kp_b[m.trainIdx].pt[0]
        if (x1 <= left_x or x1 >= right_x) or (x2 <= left_x or x2 >= right_x):
            kept.append(m)
    return kept

def _estimate_trend_from_matches(kp_a, kp_b, matches, inlier_mask=None):
    if matches is None or len(matches) == 0:
        return None
    disp = []
    for i, m in enumerate(matches):
        if inlier_mask is not None and i < len(inlier_mask) and int(inlier_mask[i]) != 1:
            continue
        x1, y1 = kp_a[m.queryIdx].pt
        x2, y2 = kp_b[m.trainIdx].pt
        disp.append((x2 - x1, y2 - y1))
        
    if len(disp) < 8:
        return None
        
    disp = np.asarray(disp, dtype=np.float32)
    med = np.median(disp, axis=0)  
    return -med  # Đảo dấu


def _build_flann_lsh_matcher():
    # ORB tạo binary descriptors, FLANN nên dùng index LSH cho hiệu năng tốt hơn BF.
    index_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
    search_params = dict(checks=32)
    return cv2.FlannBasedMatcher(index_params, search_params)


def _match_orb_descriptors(flann, des1, des2, ratio_test=0.75):
    if des1 is None or des2 is None:
        return []
    if len(des1) < 2 or len(des2) < 2:
        return []

    # FLANN + LSH yêu cầu dtype uint8 cho ORB descriptors.
    if des1.dtype != np.uint8:
        des1 = des1.astype(np.uint8)
    if des2.dtype != np.uint8:
        des2 = des2.astype(np.uint8)

    knn = flann.knnMatch(des1, des2, k=2)
    good = []
    for pair in knn:
        if len(pair) != 2:
            continue
        m, n = pair
        if m.distance < ratio_test * n.distance:
            good.append(m)
    return good


def _resolve_translation_scale(dt_s):
    # recoverPose trả về hướng t (độ dài chuẩn hoá), cần scale ngoài để ra quãng đường thực.
    if ODOM_SPEED_MPS is not None and dt_s > 0:
        return max(ODOM_SPEED_MPS * dt_s, 1e-6)
    if FIXED_SCALE_PER_FRAME_M is not None:
        return max(FIXED_SCALE_PER_FRAME_M, 1e-6)
    return 1.0

# ==========================================
# CHƯƠNG TRÌNH CHÍNH
# ==========================================
if not os.path.exists(VIDEO_PATH):
    print(f"LỖI: Không tìm thấy file {VIDEO_PATH}")
    exit()

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("LỖI: Không thể mở video.")
    exit()

# Tua nhanh đến frame cần bắt đầu (thay cho việc dùng vòng lặp continue)
cap.set(cv2.CAP_PROP_POS_FRAMES, START_FRAME)

# Đọc frame đầu tiên sau khi tua
ret, prev_frame = cap.read()
if not ret:
    print("LỖI: Không thể đọc frame đầu tiên.")
    exit()

if DEBUG_VIS:
    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)

orb = cv2.ORB_create(nfeatures=ORB_NFEATURES)
flann = _build_flann_lsh_matcher()

cur_R = np.eye(3)
cur_t = np.zeros((3, 1))
trend_vec_ema = np.zeros((2,), dtype=np.float32)

fps_ema = 0.0
last_time = time.perf_counter()
missing_scale_warned = False

prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
kp1, des1 = orb.detectAndCompute(prev_gray, None)

frame_counter = START_FRAME

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print(f"🎬 Video kết thúc ở frame {frame_counter}.")
        break
    
    frame = cv2.resize(frame, (PROCESS_WIDTH, PROCESS_HEIGHT))  # Resize để tăng tốc độ xử lý
    
    frame_counter += 1
    now = time.perf_counter()
    dt_s = max(now - last_time, 1e-6)
    last_time = now

    inst_fps = 1.0 / dt_s
    if fps_ema <= 0.0:
        fps_ema = inst_fps
    else:
        fps_ema = 0.9 * fps_ema + 0.1 * inst_fps

    curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    vis = frame.copy() if DEBUG_VIS else None
    
    kp2, des2 = orb.detectAndCompute(curr_gray, None)
    
    if des1 is not None and des2 is not None:
        matches = _match_orb_descriptors(flann, des1, des2, ratio_test=RATIO_TEST)
        
        if USE_SIDE_REGIONS:
            w = frame.shape[1]
            matches_side = _filter_matches_side_regions(kp1, kp2, matches, w, SIDE_REGION_FRAC)
            if len(matches_side) >= MIN_MATCHES:
                matches = matches_side
                
        if len(matches) >= MIN_MATCHES:
            pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
            pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])
            
            E, mask = cv2.findEssentialMat(
                pts2,
                pts1,
                focal=CAMERA_FOCAL_PX,
                pp=CAMERA_PP,
                method=ESSENTIAL_METHOD,
                prob=ESSENTIAL_PROB,
                threshold=ESSENTIAL_THRESHOLD,
            )
            
            if E is not None and E.shape == (3, 3):
                _, R, t, mask_pose = cv2.recoverPose(
                    E,
                    pts2,
                    pts1,
                    focal=CAMERA_FOCAL_PX,
                    pp=CAMERA_PP,
                )

                scale_m = _resolve_translation_scale(dt_s)
                if ODOM_SPEED_MPS is None and FIXED_SCALE_PER_FRAME_M is None and not missing_scale_warned:
                    print("Cảnh báo: Chưa có scale thực cho t. cur_t hiện chỉ đúng về hướng tương đối.")
                    missing_scale_warned = True

                cur_t = cur_t + cur_R.dot(t * scale_m)
                cur_R = R.dot(cur_R)
                
                inlier_mask = mask.ravel() if mask is not None else None
                
                # Tính xu hướng mũi tên
                trend_vec = _estimate_trend_from_matches(kp1, kp2, matches, inlier_mask)
                if trend_vec is not None:
                    trend_vec_ema = (TREND_EMA_ALPHA * trend_vec_ema) + ((1.0 - TREND_EMA_ALPHA) * trend_vec.astype(np.float32))
                    if DEBUG_VIS:
                        h, w = vis.shape[:2]
                        start_pt = (w // 2, h // 2)
                        norm = float(np.linalg.norm(trend_vec_ema))

                        if norm > 1e-3:
                            v = (trend_vec_ema / norm) * float(ARROW_SCALE_PX)
                            end_pt = (int(start_pt[0] + v[0]), int(start_pt[1] + v[1]))
                            cv2.arrowedLine(vis, start_pt, end_pt, ARROW_COLOR, ARROW_THICKNESS, tipLength=ARROW_TIP_LENGTH)
                            cv2.putText(vis, f"Trend: ({trend_vec_ema[0]:.1f}, {trend_vec_ema[1]:.1f})",
                                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, ARROW_COLOR, 2, cv2.LINE_AA)

                # Vẽ điểm Inliers
                if DEBUG_VIS:
                    for i, m in enumerate(matches):
                        if inlier_mask is not None and len(inlier_mask) > i and int(inlier_mask[i]) == 1:
                            pt1 = (int(kp1[m.queryIdx].pt[0]), int(kp1[m.queryIdx].pt[1]))
                            pt2 = (int(kp2[m.trainIdx].pt[0]), int(kp2[m.trainIdx].pt[1]))
                            cv2.circle(vis, pt2, 5, (0, 255, 0), -1)
                            cv2.line(vis, pt1, pt2, (255, 0, 0), 2)

    if frame_counter % PRINT_FPS_EVERY_N_FRAMES == 0:
        print(f"Frame {frame_counter} | FPS~{fps_ema:.1f} | t=({cur_t[0,0]:.3f}, {cur_t[1,0]:.3f}, {cur_t[2,0]:.3f})")
                        
    # Vẽ line 2 bên ranh giới
    if USE_SIDE_REGIONS:
        if DEBUG_VIS:
            h, w = vis.shape[:2]
            cv2.line(vis, (int(w * SIDE_REGION_FRAC), 0), (int(w * SIDE_REGION_FRAC), h), (0, 255, 255), 1)
            cv2.line(vis, (int(w * (1.0 - SIDE_REGION_FRAC)), 0), (int(w * (1.0 - SIDE_REGION_FRAC)), h), (0, 255, 255), 1)

    # Hiển thị UI MỘT LẦN DUY NHẤT ở cuối vòng lặp
    if DEBUG_VIS:
        cv2.putText(vis, f"FPS: {fps_ema:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 220, 50), 2, cv2.LINE_AA)
        
        cv2.resizeWindow('Frame', DISPLAY_WIDTH, DISPLAY_HEIGHT)
        cv2.imshow('Frame', vis)
    
    # Cập nhật descriptor của frame trước cho vòng lặp kế tiếp nếu frame hiện tại có descriptor.
    if des2 is not None:
        kp1, des1 = kp2, des2

    if DEBUG_VIS:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
if DEBUG_VIS:
    cv2.destroyAllWindows()