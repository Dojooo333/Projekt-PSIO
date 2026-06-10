import cv2
import config
import math

# Obraca i skaluje klatkę zachowując proporcje obrazu
def scale_image_to_height(frame, camera_idx, target_h=480):
    if frame is None:
        return None

    if camera_idx == 1:
        if config.CAMERA_1_ROTATION:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        mode = config.CAMERA_1_MODE
    elif camera_idx == 2:
        if config.CAMERA_2_ROTATION:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        mode = config.CAMERA_2_MODE
    else:
        return frame

    if mode == "16:9":
        target_w = 853
        target_ar = 16 / 9
    else:
        target_w = 270
        target_ar = 9 / 16

    h, w = frame.shape[:2]
    current_ar = w / h

    if current_ar > target_ar:
        new_w = int(h * target_ar)
        start_x = (w - new_w) // 2
        frame = frame[:, start_x:start_x + new_w]
    elif current_ar < target_ar:
        new_h = int(w / target_ar)
        start_y = (h - new_h) // 2
        frame = frame[start_y:start_y + new_h, :]

    return cv2.resize(frame, (target_w, target_h))

# Rysuje szkielet bezpośrednio na obrazie
def draw_skeleton(frame, yolo_result):
    if yolo_result.keypoints is None or len(yolo_result.keypoints.xy) == 0:
        return frame

    keypoints = yolo_result.keypoints.xy[0].cpu().numpy()
    confidences = yolo_result.keypoints.conf[0].cpu().numpy()

    connections = [
        (0, 1), (0, 2), (1, 3), (2, 4), (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
        (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)
    ]

    for p1, p2 in connections:
        if confidences[p1] > 0.5 and confidences[p2] > 0.5:
            pt1 = (int(keypoints[p1][0]), int(keypoints[p1][1]))
            pt2 = (int(keypoints[p2][0]), int(keypoints[p2][1]))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2, cv2.LINE_AA)

    for i, conf in enumerate(confidences):
        if conf > 0.5:
            pt = (int(keypoints[i][0]), int(keypoints[i][1]))
            cv2.circle(frame, pt, 4, (0, 0, 255), -1, cv2.LINE_AA)

    return frame

# Oblicza wewnętrzny kąt w stopniach
def calculate_angle(p1, p2, p3):
    ang = math.degrees(math.atan2(p3[1] - p2[1], p3[0] - p2[0]) - math.atan2(p1[1] - p2[1], p1[0] - p2[0]))
    ang = abs(ang)
    return 360 - ang if ang > 180 else ang
