import cv2
from ultralytics import YOLO

# Inicjalizacja modelu YOLOv11
model = YOLO('yolo11n-pose.pt')

cap = cv2.VideoCapture(0)

counter = 0
stage = "down"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Nie można połączyć się z kamerą.")
        break

    results = model.predict(frame, verbose=False)
    annotated_frame = results[0].plot()

    try:
        keypoints = results[0].keypoints.xy[0].cpu().numpy()

        # Pobieranie współrzędnych Y (wysokość na ekranie)
        nose_y = keypoints[0][1]

        left_shoulder_y = keypoints[5][1]
        right_shoulder_y = keypoints[6][1]

        left_wrist_y = keypoints[9][1]
        right_wrist_y = keypoints[10][1]

        # Pobieranie współrzędnych X (szerokość na ekranie)
        left_shoulder_x = keypoints[5][0]
        right_shoulder_x = keypoints[6][0]

        # Indeksy 15 i 16 to kostki (lewa i prawa)
        left_ankle_x = keypoints[15][0]
        right_ankle_x = keypoints[16][0]

        # Zabezpieczenie: model musi widzieć nos, barki, nadgarstki i KOSTKI
        punkty_do_sprawdzenia = [nose_y, left_shoulder_y, right_shoulder_y,
                                 left_wrist_y, right_wrist_y, left_shoulder_x,
                                 right_shoulder_x, left_ankle_x, right_ankle_x]

        if all(v > 0 for v in punkty_do_sprawdzenia):

            # Obliczenie odległości na osi X
            szerokosc_barkow = abs(left_shoulder_x - right_shoulder_x)
            rozstaw_kostek = abs(left_ankle_x - right_ankle_x)

            # WARUNEK "UP" (Pajacyk otwarty)
            # 1. Ręce w górze
            rece_w_gorze = left_wrist_y < nose_y and right_wrist_y < nose_y
            # 2. Nogi szeroko (odległość między kostkami to min. 1.5x szerokości barków)
            nogi_szeroko = rozstaw_kostek > (szerokosc_barkow * 1.5)

            if rece_w_gorze and nogi_szeroko:
                if stage == "down":
                    stage = "up"
                    counter += 1

            # WARUNEK "DOWN" (Pajacyk zamknięty)
            # 1. Ręce w dole (nadgarstki poniżej barków)
            rece_w_dole = left_wrist_y > left_shoulder_y and right_wrist_y > right_shoulder_y
            # 2. Nogi złączone (odległość między kostkami nie większa niż 1.2x szerokości barków)
            nogi_zlaczone = rozstaw_kostek <= (szerokosc_barkow * 1.2)

            if rece_w_dole and nogi_zlaczone:
                stage = "down"

    except (IndexError, AttributeError):
        pass

    cv2.rectangle(annotated_frame, (0, 0), (250, 70), (0, 0, 0), -1)
    cv2.putText(annotated_frame, f'WYNIK: {counter}', (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('Cyber Trener - Pajacyki', annotated_frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()