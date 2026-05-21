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

        # Pobieranie koordynatów Y dla kluczowych punktów
        # Indeksy COCO: 0-nos, 5-lewy bark, 6-prawy bark, 7-lewy łokieć, 8-prawy łokieć, 9-lewy nadgarstek, 10-prawy nadgarstek
        nose_y = keypoints[0][1]

        left_shoulder_y = keypoints[5][1]
        right_shoulder_y = keypoints[6][1]

        left_elbow_y = keypoints[7][1]
        right_elbow_y = keypoints[8][1]

        left_wrist_y = keypoints[9][1]
        right_wrist_y = keypoints[10][1]

        # Zabezpieczenie: upewniamy się, że model widzi wszystkie potrzebne punkty (wartość > 0)
        punkty_do_sprawdzenia = [nose_y, left_shoulder_y, right_shoulder_y,
                                 left_elbow_y, right_elbow_y, left_wrist_y, right_wrist_y]

        if all(v > 0 for v in punkty_do_sprawdzenia):

            # WARUNEK PODNIESIENIA (UP):
            # 1. Nadgarstki wyżej niż nos (oś Y rośnie w dół, więc wartość musi być mniejsza)
            nadgarstki_nad_glowa = left_wrist_y < nose_y and right_wrist_y < nose_y

            # 2. Ręce wyprostowane (nadgarstek wyżej niż łokieć, łokieć wyżej niż bark)
            lewa_wyprostowana = left_wrist_y < left_elbow_y < left_shoulder_y
            prawa_wyprostowana = right_wrist_y < right_elbow_y < right_shoulder_y

            if nadgarstki_nad_glowa and lewa_wyprostowana and prawa_wyprostowana:
                if stage == "down":
                    stage = "up"
                    counter += 1

            # WARUNEK OPUSZCZENIA (DOWN):
            # Resetujemy stan dopiero, gdy nadgarstki z powrotem opadną poniżej barków
            elif left_wrist_y > left_shoulder_y and right_wrist_y > right_shoulder_y:
                stage = "down"

    except (IndexError, AttributeError):
        pass

    cv2.rectangle(annotated_frame, (0, 0), (250, 70), (0, 0, 0), -1)
    cv2.putText(annotated_frame, f'WYNIK: {counter}', (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('Cyber Trener - Wymuszony Wyprost', annotated_frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()